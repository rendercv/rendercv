import importlib
import importlib.util
from functools import reduce
from operator import or_
from pathlib import Path
from typing import Annotated

import pydantic

from ...utils.variant_class_generator import create_variant_class
from .classic_theme import ClassicTheme


def discover_other_themes() -> list[type[ClassicTheme]]:
    """Auto-discover and load all theme files from other_themes/ directory.

    Returns:
        Dictionary mapping class names (e.g., "EngineeringresumesTheme") to dynamically
        created Pydantic model classes.
    """
    other_themes_dir = Path(__file__).parent / "other_themes"
    discovered: list[type[ClassicTheme]] = []

    for py_file in sorted(other_themes_dir.glob("*.py")):
        if py_file.stem == "__init__":
            continue

        theme_name = py_file.stem
        module = importlib.import_module(
            f"rendercv.schema.models.design.other_themes.{theme_name}"
        )
        theme_data = getattr(module, f"{theme_name}_theme")
        theme_class = create_variant_class(
            variant_name=theme_name,
            defaults=theme_data,
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
built_in_design_adapter = pydantic.TypeAdapter(BuiltInDesign)
