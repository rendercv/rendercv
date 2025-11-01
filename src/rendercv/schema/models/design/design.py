import importlib
import importlib.util
import pathlib
from typing import Annotated, Any

import pydantic

from ....themes import (
    ClassicThemeOptions,
    EngineeringclassicThemeOptions,
    EngineeringresumesThemeOptions,
    ModerncvThemeOptions,
    Sb2novThemeOptions,
)
from ..base import BaseModelWithoutExtraKeys


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
        ThemeDataModel = available_theme_options[design["theme"]]
        return ThemeDataModel(**design)
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
            ThemeDataModel = getattr(
                theme_module,
                model_name,
            )
        except AttributeError as e:
            message = (
                f"The custom theme {theme_name} does not have a {model_name} class."
            )
            raise ValueError(message) from e

        # Initialize and validate the custom theme data model:
        theme_data_model = ThemeDataModel(**design)
    else:
        # Then it means there is no __init__.py file in the custom theme folder.
        # Create a dummy data model and use that instead.
        class ThemeOptionsAreNotProvided(BaseModelWithoutExtraKeys):
            theme: str = theme_name

        theme_data_model = ThemeOptionsAreNotProvided(theme=theme_name)

    return theme_data_model


available_theme_options = {
    "classic": ClassicThemeOptions,
    "sb2nov": Sb2novThemeOptions,
    "engineeringresumes": EngineeringresumesThemeOptions,
    "engineeringclassic": EngineeringclassicThemeOptions,
    "moderncv": ModerncvThemeOptions,
}

available_themes = list(available_theme_options.keys())

# It is a union of all the design options and the correct design option is determined by
# the theme field, thanks to Pydantic's discriminator feature.
# See https://docs.pydantic.dev/2.7/concepts/fields/#discriminator for more information
BuiltinDesign = Annotated[
    ClassicThemeOptions
    | Sb2novThemeOptions
    | EngineeringresumesThemeOptions
    | EngineeringclassicThemeOptions
    | ModerncvThemeOptions,
    pydantic.Field(discriminator="theme"),
]

# RenderCV supports custom themes as well. Therefore, `Any` type is used to allow custom
# themes. However, the JSON Schema generation is skipped, otherwise, the JSON Schema
# would accept any `design` field in the YAML input file.
Design = Annotated[
    pydantic.json_schema.SkipJsonSchema[Any] | BuiltinDesign,
    pydantic.BeforeValidator(
        lambda design: validate_design_options(
            design,
            available_theme_options=available_theme_options,
        )
    ),
]
