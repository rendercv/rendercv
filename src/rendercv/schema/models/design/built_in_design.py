import importlib
import importlib.util
from functools import reduce
from operator import or_
from pathlib import Path
from typing import Annotated, Any, Literal

import pydantic

from .classic_theme import ClassicTheme


def create_other_theme_class(
    theme_name: str, defaults: dict[str, Any]
) -> type[ClassicTheme]:
    """Dynamically create a theme model class with the given defaults.

    Args:
        theme_name: Name of the theme (e.g., "engineeringresumes", "sb2nov")
        defaults: Dictionary of field names to default values (supports nested dicts)

    Returns:
        A dynamically created Pydantic model class that inherits from ClassicTheme
        with all field defaults applied from the defaults dictionary.
    """
    base_fields = ClassicTheme.model_fields
    field_specs: dict[str, Any] = {}

    for field_name, default_value in defaults.items():
        if field_name not in base_fields:
            message = (
                f"Field {field_name} in defaults for {theme_name} "
                "is not defined in ClassicTheme"
            )
            raise ValueError(message)

        base_field_info = base_fields[field_name]

        # For discriminator field
        if field_name == "theme":
            field_specs[field_name] = (
                Literal[default_value],  # type: ignore
                pydantic.Field(default=default_value),
            )
        # For nested objects (dict values mean we need to override nested fields)
        elif isinstance(default_value, dict):
            # Get the base nested object's default
            base_default = base_field_info.default

            if base_field_info.default_factory is None:
                # If no default_factory, use the default value directly
                new_field = pydantic.Field(default=default_value)
            else:
                # Get the default factory and create an instance
                base_nested_obj = base_field_info.default_factory()

                # Override specific nested fields
                modified_nested = base_nested_obj.model_copy(update=default_value)

                new_field = pydantic.Field(default=modified_nested)

            field_specs[field_name] = (base_field_info.annotation, new_field)
        # For simple field overrides
        else:
            new_field = pydantic.Field(default=default_value)
            field_specs[field_name] = (base_field_info.annotation, new_field)

    model_class_name = f"{theme_name.replace('_', ' ').title().replace(' ', '')}Theme"

    return pydantic.create_model(
        model_class_name,
        __base__=ClassicTheme,
        __module__="rendercv.schema.models.design",
        **field_specs,
    )


def discover_other_themes() -> dict[str, type[ClassicTheme]]:
    """Auto-discover and load all theme files from other_themes/ directory.

    Returns:
        Dictionary mapping class names (e.g., "EngineeringresumesTheme") to dynamically
        created Pydantic model classes.
    """
    other_themes_dir = Path(__file__).parent / "other_themes"
    discovered: dict[str, type[ClassicTheme]] = {}

    for py_file in sorted(other_themes_dir.glob("*.py")):
        if py_file.stem == "__init__":
            continue

        theme_name = py_file.stem
        module = importlib.import_module(
            f"rendercv.schema.models.design.other_themes.{theme_name}"
        )
        theme_data = getattr(module, f"{theme_name}_theme")
        theme_class = create_other_theme_class(theme_name, theme_data)
        discovered[theme_class.__name__] = theme_class

    return discovered


# Build discriminated union dynamically
type BuiltInDesign = Annotated[
    ClassicTheme | reduce(or_, discover_other_themes().values()),  # pyright: ignore[reportInvalidTypeForm]
    pydantic.Field(discriminator="theme"),
]
