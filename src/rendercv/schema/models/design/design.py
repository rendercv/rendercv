import importlib
import importlib.util
import pathlib
from typing import Annotated, Any

import pydantic
import pydantic_core

from ..base import BaseModelWithoutExtraKeys
from .built_in_design import BuiltInDesign


def validate_design_for_custom_theme(design: Any) -> Any:
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
    # TODO: Context
    theme_name = str(design["theme"])

    # Custom theme should only contain letters and digits:
    if not theme_name.isalnum():
        message = "The custom theme name should only contain letters and digits."
        raise pydantic_core.PydanticCustomError(
            "rendercv_custom_error",
            "The custom theme name should only contain letters and digits. The provided"
            " value is {theme_name}.",
            {"theme_name": theme_name},
        )

    custom_theme_folder = pathlib.Path.cwd() / theme_name
    # Check if the custom theme folder exists:
    if not custom_theme_folder.exists():
        raise pydantic_core.PydanticCustomError(
            "rendercv_custom_error",
            "The custom theme folder `{custom_theme_folder}` does not exist. It should"
            " be in the working directory as the input file.",
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
                "rendercv_custom_error",
                "The custom theme {theme_name}'s __init__.py file has a syntax"
                " error. Please fix it.",
                {"theme_name": theme_name},
            ) from e
        except ImportError as e:
            raise pydantic_core.PydanticCustomError(
                "rendercv_custom_error",
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
                f"The custom theme {theme_name} does not have a {model_name} class. It"
                f" has the following classes: {theme_module.__dict__}."
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
    BuiltInDesign
    | pydantic.json_schema.SkipJsonSchema[
        Annotated[Any, pydantic.PlainValidator(validate_design_for_custom_theme)]
    ],
    pydantic.Field(union_mode="left_to_right"),
]
