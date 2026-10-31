import importlib
import importlib.util
import pathlib
import re
from typing import Annotated, Any

import pydantic
import pydantic_core

from rendercv.exception import RenderCVInternalError

from ...variant_pydantic_model_generator import create_variant_pydantic_model
from ..custom_error_types import CustomPydanticErrorTypes
from ..validation_context import get_input_file_path
from .built_in_design import (
    BuiltInDesign,
    built_in_design_adapter,
    built_in_theme_models,
)
from .classic_theme import ClassicTheme

# A custom theme name names a directory and, capitalized, a Python class
# (`MythemeTheme`). `$(?!\n)` ends the string in both Python and JSON Schema regexes:
custom_theme_name_pattern = re.compile(r"^[a-z][a-z0-9]*$(?!\n)")


class CustomTheme(pydantic.BaseModel):
    """Describe custom theme input without claiming to know its local options.

    Why:
        Editors cannot load local Python models. A separate schema branch accepts
        custom names and options while leaving built-in validation and completion
        intact. Excluding built-in names prevents this branch bypassing their schema.
    """

    model_config = pydantic.ConfigDict(extra="allow")
    theme: str = pydantic.Field(
        pattern=custom_theme_name_pattern,
        json_schema_extra={"not": {"enum": list(built_in_theme_models)}},
        description="Name of a custom theme folder next to the input file.",
    )


class ThemeName(pydantic.BaseModel):
    theme: str

    @pydantic.field_validator("theme")
    @classmethod
    def validate_name(cls, name: str) -> str:
        """Reject invalid custom names at the selector field.

        Args:
            name: Built-in theme name or local theme directory name.

        Returns:
            Unchanged valid name.
        """
        if (
            name not in built_in_theme_models
            and not custom_theme_name_pattern.fullmatch(name)
        ):
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "The custom theme name must start with a lowercase letter and contain"
                " only lowercase letters and digits. The provided value is"
                " `{theme_name}`.",
                {"theme_name": name},
            )
        return name


def find_missing_options(
    model: pydantic.BaseModel, reference: type[pydantic.BaseModel], prefix: str = ""
) -> list[str]:
    """List the options of a reference model that a model doesn't define.

    Why:
        A custom theme's `__init__.py` is a copy of the classic theme's model, and
        the renderer reads the classic theme's options from it. A copy made by an
        older RenderCV lacks the options added since, so it must fail validation
        instead of crashing the renderer.

    Example:
        ```py
        find_missing_options(old_theme, ClassicTheme)
        # ["colors.subsection_titles", "templates.single_date"]
        ```

    Args:
        model: Validated model to check.
        reference: Model class whose options the model must define.
        prefix: Dotted path of `model` within the theme, for the result.

    Returns:
        Dotted paths of the missing options.
    """
    missing_options = []
    model_fields = type(model).model_fields
    for name, field_info in reference.model_fields.items():
        if name not in model_fields:
            missing_options.append(f"{prefix}{name}")
            continue
        value = getattr(model, name)
        option_class = field_info.annotation
        if (
            isinstance(option_class, type)
            and issubclass(option_class, pydantic.BaseModel)
            and isinstance(value, pydantic.BaseModel)
        ):
            missing_options.extend(
                find_missing_options(value, option_class, f"{prefix}{name}.")
            )
    return missing_options


def validate_design(design: Any, info: pydantic.ValidationInfo) -> pydantic.BaseModel:
    """Validate design options for built-in or custom themes with dynamic loading.

    Why:
        Users can use built-in themes or create custom themes in local folders.
        The theme name selects a built-in model or a local custom model before
        validating its options. Option errors never trigger another route.

    Args:
        design: Design dictionary to validate.
        info: Validation context containing input file path.

    Returns:
        Validated design model (built-in or custom theme class).
    """
    if isinstance(design, pydantic.BaseModel) and hasattr(design, "theme"):
        # A theme model built in Python, like the one `rendercv new` builds:
        return design
    if not isinstance(design, dict):
        return built_in_design_adapter.validate_python(design, context=info.context)

    theme_name = ThemeName.model_validate(design).theme
    if theme_name in built_in_theme_models:
        return built_in_theme_models[theme_name].model_validate(
            design, context=info.context
        )

    input_file_path = get_input_file_path(info)
    relative_to = input_file_path.parent if input_file_path else pathlib.Path.cwd()

    custom_theme_folder = relative_to / theme_name
    # Check if the custom theme folder exists:
    if not custom_theme_folder.is_dir():
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
        if spec is None:
            msg = f"Failed to load spec from {path_to_init_file}"
            raise RenderCVInternalError(msg)

        theme_module = importlib.util.module_from_spec(spec)
        try:
            if spec.loader is None:
                msg = f"spec.loader is None for {path_to_init_file}"
                raise RenderCVInternalError(msg)
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
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "The custom theme {theme_name} does not have a {model_name} class.",
                {"theme_name": theme_name, "model_name": model_name},
            ) from e

        if not isinstance(theme_data_model_class, type) or not issubclass(
            theme_data_model_class, pydantic.BaseModel
        ):
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "The custom theme {theme_name}'s {model_name} must be a Pydantic model"
                " class.",
                {"theme_name": theme_name, "model_name": model_name},
            )

        theme_data_model = theme_data_model_class.model_validate(
            design, context=info.context
        )
        if missing_options := find_missing_options(theme_data_model, ClassicTheme):
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "The custom theme {theme_name} lacks design options that RenderCV"
                " needs: {missing_options}. Its __init__.py was probably created by an"
                " older version of RenderCV. Create a new theme with `rendercv"
                " create-theme` and copy your changes into it, or add these options.",
                {
                    "theme_name": theme_name,
                    "missing_options": ", ".join(missing_options),
                },
            )
    else:
        # A template-only custom theme (no __init__.py) accepts the classic theme's
        # design options:
        theme_data_model = create_variant_pydantic_model(
            variant_name=theme_name,
            defaults={"theme": theme_name},
            base_class=ClassicTheme,
            discriminator_field="theme",
            class_name_suffix="Theme",
            module_name="rendercv.schema.models.design",
        ).model_validate(design, context=info.context)

    return theme_data_model


# Local themes define their own fields and serializers at runtime, so their static
# type is necessarily dynamic. The validator always returns a validated BaseModel;
# Any lets Pydantic serialize that actual model rather than a built-in union branch.
type Design = Annotated[
    Any,
    pydantic.BeforeValidator(
        validate_design,
        json_schema_input_type=BuiltInDesign | CustomTheme,
    ),
]
