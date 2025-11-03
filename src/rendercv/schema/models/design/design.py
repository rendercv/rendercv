import importlib
import importlib.util
import pathlib
from functools import reduce
from operator import or_
from pathlib import Path
from typing import Annotated, Any, Literal

import pydantic

from ..base import BaseModelWithoutExtraKeys
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

    Example:
        >>> theme_data = {"theme": "engineeringresumes", "page": {"show_page_numbering": False}, ...}
        >>> engineeringresumes_theme = create_theme_class(
        ...     "engineeringresumes", theme_data
        ... )
        >>> theme = engineeringresumes_theme()
        >>> theme.theme
        'engineeringresumes'
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


# Build available_theme_options dict for validate_design_options
available_theme_options = {
    theme_class.model_fields["theme"].default: theme_class
    for theme_class in theme_classes
}

available_built_in_themes = list(available_theme_options.keys())

# Build __all__ with explicit strings
__all__ = ["BuiltInDesign", "ClassicTheme", "Design"]
__all__.extend(discovered_themes.keys())


def validate_design_options(
    design: Any,
    available_theme_options: dict[str, type],
) -> Any:
    """Check if the design options are for a built-in theme or a custom theme. If it is
    a built-in theme, validate it with the corresponding data model. If it is a custom
    theme, check if the necessary files are provided and validate it with the custom
    theme data model, found in the `__init__.py` file of the custom theme folder.

    Args:
        design: The design options to validate.
        available_theme_options: The available theme options. The keys are the theme
            names and the values are the corresponding data models.

    Returns:
        The validated design as a Pydantic data model.
    """
    module = importlib.import_module(".rendercv_data_model", __package__)
    INPUT_FILE_DIRECTORY = module.INPUT_FILE_DIRECTORY

    if isinstance(design, tuple(available_theme_options.values())):
        # Then it means it is an already validated built-in theme. Return it as it is:
        return design
    if design["theme"] in available_theme_options:
        # Then it is a built-in theme, but it is not validated yet. Validate it and
        # return it:
        theme_data_model = available_theme_options[design["theme"]]
        return theme_data_model(**design)
    # It is a custom theme. Validate it:
    theme_name: str = str(design["theme"])

    # Custom theme should only contain letters and digits:
    if not theme_name.isalnum():
        message = "The custom theme name should only contain letters and digits."
        raise ValueError(
            message,
            "theme",  # this is the location of the error
            theme_name,  # this is value of the error
        )

    if INPUT_FILE_DIRECTORY is None:
        theme_parent_folder = pathlib.Path.cwd()
    else:
        theme_parent_folder = INPUT_FILE_DIRECTORY

    custom_theme_folder = theme_parent_folder / theme_name

    # Check if the custom theme folder exists:
    if not custom_theme_folder.exists():
        message = (
            (
                f"The custom theme folder `{custom_theme_folder}` does not exist."
                " It should be in the working directory as the input file."
            ),
        )
        raise ValueError(
            message,
            "",  # this is the location of the error
            theme_name,  # this is value of the error
        )

    # Import __init__.py file from the custom theme folder if it exists:
    path_to_init_file = custom_theme_folder / "__init__.py"

    if path_to_init_file.exists():
        spec = importlib.util.spec_from_file_location(
            "theme",
            path_to_init_file,
        )
        assert spec is not None

        theme_module = importlib.util.module_from_spec(spec)
        try:
            assert spec.loader is not None
            spec.loader.exec_module(theme_module)
        except SyntaxError as e:
            message = (
                f"The custom theme {theme_name}'s __init__.py file has a syntax"
                " error. Please fix it."
            )
            raise ValueError(message) from e
        except ImportError as e:
            message = (
                (
                    f"The custom theme {theme_name}'s __init__.py file has an"
                    " import error. If you have copy-pasted RenderCV's built-in"
                    " themes, make sure to update the import statements (e.g.,"
                    ' "from . import" to "from rendercv.themes import").'
                ),
            )

            raise ValueError(message) from e

        model_name = f"{theme_name.capitalize()}ThemeOptions"
        try:
            theme_data_model_class = getattr(
                theme_module,
                model_name,
            )
        except AttributeError as e:
            message = (
                f"The custom theme {theme_name} does not have a {model_name} class."
            )
            raise ValueError(message) from e

        # Initialize and validate the custom theme data model:
        theme_data_model = theme_data_model_class(**design)
    else:
        # Then it means there is no __init__.py file in the custom theme folder.
        # Create a dummy data model and use that instead.
        class ThemeOptionsAreNotProvided(BaseModelWithoutExtraKeys):
            theme: str = theme_name

        theme_data_model = ThemeOptionsAreNotProvided(theme=theme_name)

    return theme_data_model


# RenderCV supports custom themes as well. Therefore, `Any` type is used to allow custom
# themes. However, the JSON Schema generation is skipped, otherwise, the JSON Schema
# would accept any `design` field in the YAML input file.
Design = Annotated[
    pydantic.json_schema.SkipJsonSchema[Any] | BuiltInDesign,
    pydantic.BeforeValidator(
        lambda design: validate_design_options(
            design,
            available_theme_options=available_theme_options,
        )
    ),
]
