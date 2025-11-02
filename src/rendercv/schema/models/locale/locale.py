import importlib
from functools import reduce
from operator import or_
from pathlib import Path
from typing import Annotated, Any, Literal

import pydantic

from .english_locale import EnglishLocale


def create_other_locale_class(
    locale_name: str, defaults: dict[str, Any]
) -> type[EnglishLocale]:
    """Dynamically create a locale model class with the given defaults.

    Args:
        locale_name: Name of the locale (e.g., "english", "turkish")
        defaults: Dictionary of field names to default values

    Returns:
        A dynamically created Pydantic model class that inherits from BaseLocale
        with all field defaults applied from the defaults dictionary.

    Example:
        >>> locale_data = {"language": "english", "month": "month", ...}
        >>> english_locale = create_locale_class("english", locale_data)
        >>> locale = english_locale()
        >>> locale.language
        'english'
    """
    base_fields = EnglishLocale.model_fields
    field_specs: dict[str, Any] = {}

    for field_name, default_value in defaults.items():
        if field_name not in base_fields:
            message = (
                f"Field {field_name} in defaults for {locale_name} "
                "is not defined in BaseLocale"
            )
            raise ValueError(message)

        base_field_info = base_fields[field_name]

        new_field = pydantic.Field(
            default=default_value,
            description=base_field_info.description,
            title=base_field_info.title,
        )

        field_annotation = base_field_info.annotation

        # For discriminated unions, each subclass needs a Literal type
        if field_name == "language":
            field_annotation = Literal[default_value]  # type: ignore

        field_specs[field_name] = (field_annotation, new_field)

    model_class_name = f"{locale_name.replace('_', ' ').title().replace(' ', '')}Locale"

    return pydantic.create_model(
        model_class_name,
        __base__=EnglishLocale,
        __module__="rendercv.schema.models.locale",
        **field_specs,
    )


def discover_other_locales() -> dict[str, type[EnglishLocale]]:
    """Auto-discover and load all locale files from locales/ directory.

    Returns:
        Dictionary mapping class names (e.g., "EnglishLocale") to dynamically
        created Pydantic model classes.
    """
    locales_dir = Path(__file__).parent / "other_locales"
    discovered: dict[str, type[EnglishLocale]] = {}

    for py_file in sorted(locales_dir.glob("*.py")):
        if py_file.stem == "__init__":
            continue

        locale_name = py_file.stem
        module = importlib.import_module(
            f"rendercv.schema.models.locale.other_locales.{locale_name}"
        )
        locale_data = getattr(module, f"{locale_name}_locale")
        locale_class = create_other_locale_class(locale_name, locale_data)
        discovered[locale_class.__name__] = locale_class

    return discovered


# Build discriminated union dynamically
type Locale = Annotated[
    reduce(or_, discover_other_locales().values()),  # pyright: ignore[reportInvalidTypeForm]
    pydantic.Field(discriminator="language"),
]
