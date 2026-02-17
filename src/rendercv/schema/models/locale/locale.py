from functools import reduce
from operator import or_
from pathlib import Path
from typing import Annotated, get_args

import pydantic

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
        )
        discovered.append(locale_model)

    return discovered


# Build discriminated union dynamically
type Locale = Annotated[
    EnglishLocale | reduce(or_, discover_other_locales()),  # ty: ignore[invalid-type-form]
    pydantic.Field(discriminator="language"),
]
available_locales = [
    LocaleModel.model_fields["language"].default
    for LocaleModel in get_args(get_args(Locale.__value__)[0])
]
locale_adapter = pydantic.TypeAdapter[Locale](Locale)
