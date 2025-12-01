import importlib
import importlib.util
import pathlib
import re
from typing import Annotated, Any

import pydantic
import pydantic_core

from ...pydantic_error_handling import CustomPydanticErrorTypes
from ..context import get_input_file_path
from .built_in_design import BuiltInDesign, built_in_design_adapter
from .classic_theme import ClassicTheme

custom_theme_name_pattern = re.compile(r"^[a-z0-9]+$")


def validate_design(design: Any, info: pydantic.ValidationInfo) -> Any:
    """Validate design options for built-in or custom themes with dynamic loading.

    Why:
        Users can use built-in themes or create custom themes in local folders.
        Validation attempts built-in first, then falls back to dynamic import
        of custom theme classes from theme folder's __init__.py.

    Args:
        design: Design dictionary to validate.
        info: Validation context containing input file path.

    Returns:
        Validated design model (built-in or custom theme class).
    """
    try:
        return built_in_design_adapter.validate_python(design)
    except pydantic.ValidationError as e:
        errors = e.errors()
        custom_theme = False
        for error in errors:
            if (
                "ctx" in error
                and "discriminator" in error["ctx"]
                and error["ctx"]["discriminator"] == "'theme'"
            ):
                custom_theme = True
                break

        if custom_theme:
            pass
        else:
            raise e

    # Then it's a custom theme:
    input_file_path = get_input_file_path(info)
    relative_to = input_file_path.parent if input_file_path else pathlib.Path.cwd()
    theme_name = str(design["theme"])

    # Custom theme should only contain letters and digits:
    if not custom_theme_name_pattern.match(theme_name):
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "The custom theme name should only contain lowercase letters and digits."
            " The provided value is `{theme_name}`.",
            {
                "theme_name": theme_name,
                "loc": ("design", "theme"),
                "input": theme_name,
            },
        )

    custom_theme_folder = relative_to / theme_name
    # Check if the custom theme folder exists:
    if not custom_theme_folder.exists():
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "The custom theme folder `{custom_theme_folder}` does not exist. It should"
            " be in the same directory as the input file.",
            {"custom_theme_folder": custom_theme_folder.absolute()},
        )
    # Check if at least there is one *.j2.typ file in the custom theme folder:
    if not any(custom_theme_folder.rglob("*.j2.typ")):
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "The custom theme folder `{custom_theme_folder}` does not contain any"
            " *.j2.typ files. It should contain at least one *.j2.typ file.",
            {"custom_theme_folder": custom_theme_folder.absolute()},
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
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "The custom theme {theme_name}'s __init__.py file has a syntax"
                " error. Please fix it.",
                {"theme_name": theme_name},
            ) from e
        except ImportError as e:
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "The custom theme {theme_name}'s __init__.py file has an import error!"
                " Check the import statements.",
                {"theme_name": theme_name},
            ) from e

        model_name = f"{theme_name.capitalize()}Theme"
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
        class ThemeOptionsAreNotProvided(ClassicTheme):
            theme: str = theme_name

        theme_data_model = ThemeOptionsAreNotProvided(theme=theme_name)

    return theme_data_model


# RenderCV supports custom themes as well. For JSON schema, expose only BuiltInDesign.
# The validator runs after the built-in validation to support custom themes.
Design = Annotated[
    BuiltInDesign,
    pydantic.WrapValidator(lambda v, _, info: validate_design(v, info)),
]
