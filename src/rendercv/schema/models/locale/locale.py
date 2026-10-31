from functools import reduce
from operator import or_
from pathlib import Path
from typing import Annotated, Any, get_args

import pydantic
from pydantic_core import PydanticCustomError

from ...variant_pydantic_model_generator import create_variant_pydantic_model
from ...yaml_reader import read_yaml
from .english_locale import EnglishLocale


def discover_other_locales() -> list[type[EnglishLocale]]:
    """Auto-discover and load locale variant classes from other_locales/ directory.

    Why:
        Locales beyond English are defined as YAML files with translations
        and format overrides. Dynamic discovery enables community-contributed
        locales without core code changes.

    Returns:
        List of dynamically generated locale variant classes.
    """
    other_locales_dir = Path(__file__).parent / "other_locales"
    discovered: list[type[EnglishLocale]] = []

    for yaml_file in sorted(other_locales_dir.glob("*.yaml")):
        locale_model = create_variant_pydantic_model(
            variant_name=yaml_file.stem,
            defaults=read_yaml(yaml_file)["locale"],
            base_class=EnglishLocale,
            discriminator_field="language",
            class_name_suffix="Locale",
            module_name="rendercv.schema.models.locale",
            require_all_fields=True,
        )
        discovered.append(locale_model)

    return discovered


class LocaleName(pydantic.BaseModel):
    language: str

    @pydantic.field_validator("language")
    @classmethod
    def validate_language(cls, language: str) -> str:
        """Check the selector against the discovered locale registry.

        Args:
            language: Requested locale name.

        Returns:
            Unchanged supported name.
        """
        if language not in locale_models:
            raise PydanticCustomError(
                "rendercv_locale",
                "Unknown language `{language}`. Choose one of: {choices}.",
                {"language": language, "choices": ", ".join(available_locales)},
            )
        return language


def validate_locale(
    locale: Any,
    handler: pydantic.ValidatorFunctionWrapHandler,
    info: pydantic.ValidationInfo,
) -> Any:
    """Select a locale before validating its fields, without branch labels.

    Args:
        locale: Input mapping or an existing locale instance.
        handler: Union validator for non-mapping inputs.
        info: Validation context forwarded to the selected model.

    Returns:
        Validated locale model.
    """
    if not isinstance(locale, dict):
        return handler(locale)
    language = LocaleName.model_validate(locale).language
    return locale_models[language].model_validate(locale, context=info.context)


# Keep the discriminated union in JSON Schema. Runtime routing uses the registry.
type Locale = Annotated[
    reduce(or_, discover_other_locales(), EnglishLocale),  # ty: ignore[invalid-type-form]
    pydantic.Field(discriminator="language"),
    pydantic.WrapValidator(validate_locale),
]
locale_models: dict[str, type[EnglishLocale]] = {
    LocaleModel.model_fields["language"].default: LocaleModel
    for LocaleModel in get_args(get_args(Locale.__value__)[0])
}
available_locales = list(locale_models)
locale_adapter = pydantic.TypeAdapter[Locale](Locale)
