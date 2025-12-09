from functools import reduce
from operator import or_
from pathlib import Path
from typing import Annotated, get_args

import pydantic

from ...variant_pydantic_model_generator import create_variant_pydantic_model
from ...yaml_reader import read_yaml
from .classic_theme import ClassicTheme


def discover_other_themes() -> list[type[ClassicTheme]]:
    """Auto-discover and load theme variant classes from other_themes/ directory.

    Why:
        Built-in themes beyond classic are defined as YAML files with field
        overrides. Dynamic discovery and variant generation keeps theme
        system extensible without code changes for each theme.

    Returns:
        List of dynamically generated theme variant classes.
    """
    other_themes_dir = Path(__file__).parent / "other_themes"
    discovered: list[type[ClassicTheme]] = []

    for yaml_file in sorted(other_themes_dir.glob("*.yaml")):
        theme_class = create_variant_pydantic_model(
            variant_name=yaml_file.stem,
            defaults=read_yaml(yaml_file)["design"],
            base_class=ClassicTheme,
            discriminator_field="theme",
            class_name_suffix="Theme",
            module_name="rendercv.schema.models.design",
        )
        discovered.append(theme_class)

    return discovered


# Build discriminated union dynamically
type BuiltInDesign = Annotated[
    ClassicTheme | reduce(or_, discover_other_themes()),  # pyright: ignore[reportInvalidTypeForm]
    pydantic.Field(discriminator="theme"),
]
available_themes: list[str] = [
    ThemeClass.model_fields["theme"].default
    for ThemeClass in get_args(get_args(BuiltInDesign.__value__)[0])
]
built_in_design_adapter = pydantic.TypeAdapter(BuiltInDesign)
