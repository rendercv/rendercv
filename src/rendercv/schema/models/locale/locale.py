from functools import reduce
from operator import or_
from pathlib import Path
from typing import Annotated, get_args

import pydantic

from ...variant_class_generator import create_variant_class
from ...yaml_reader import read_yaml
from .english_locale import EnglishLocale


def discover_other_locales() -> list[type[EnglishLocale]]:
    """Auto-discover and load all locale files from locales/ directory.

    Returns:
        Dictionary mapping class names (e.g., "EnglishLocale") to dynamically
        created Pydantic model classes.
    """
    other_locales_dir = Path(__file__).parent / "other_locales"
    discovered: list[type[EnglishLocale]] = []

    for yaml_file in sorted(other_locales_dir.glob("*.yaml")):
        locale_class = create_variant_class(
            variant_name=yaml_file.stem,
            defaults=read_yaml(yaml_file, read_type="safe")["locale"],
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
available_locales = [
    LocaleClass.model_fields["language"].default
    for LocaleClass in get_args(get_args(Locale.__value__)[0])
]
locale_adapter = pydantic.TypeAdapter(Locale)
