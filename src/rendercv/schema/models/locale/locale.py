import importlib
from functools import reduce
from operator import or_
from pathlib import Path
from typing import Annotated

import pydantic

from ...utils.variant_class_generator import create_variant_class
from .english_locale import EnglishLocale


def discover_other_locales() -> list[type[EnglishLocale]]:
    """Auto-discover and load all locale files from locales/ directory.

    Returns:
        Dictionary mapping class names (e.g., "EnglishLocale") to dynamically
        created Pydantic model classes.
    """
    other_locales_dir = Path(__file__).parent / "other_locales"
    discovered: list[type[EnglishLocale]] = []

    for py_file in sorted(other_locales_dir.glob("*.py")):
        if py_file.stem == "__init__":
            continue

        locale_name = py_file.stem
        module = importlib.import_module(
            f"rendercv.schema.models.locale.other_locales.{locale_name}"
        )
        locale_data = getattr(module, f"{locale_name}_locale")
        locale_class = create_variant_class(
            variant_name=locale_name,
            defaults=locale_data,
            base_class=EnglishLocale,
            discriminator_field="language",
            class_name_suffix="Locale",
            module_name="rendercv.schema.models.locale",
        )
        discovered.append(locale_class)

    return discovered


# Build discriminated union dynamically
type Locale = Annotated[
    EnglishLocale | reduce(or_, discover_other_locales()),  # pyright: ignore[reportInvalidTypeForm]
    pydantic.Field(discriminator="language"),
]
locale_adapter = pydantic.TypeAdapter(Locale)
