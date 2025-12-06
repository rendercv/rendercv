import pathlib
from typing import TypedDict, Unpack

import pydantic
from ruamel.yaml.comments import CommentedMap

from rendercv.exception import RenderCVUserValidationError

from .models.validation_context import ValidationContext
from .models.rendercv_model import RenderCVModel
from .override_dictionary import apply_overrides_to_dictionary
from .pydantic_error_handling import parse_validation_errors
from .yaml_reader import read_yaml


class BuildRendercvModelArguments(TypedDict, total=False):
    design_file_path_or_contents: pathlib.Path | str | None
    locale_file_path_or_contents: pathlib.Path | str | None
    settings_file_path_or_contents: pathlib.Path | str | None
    typst_path: pathlib.Path | str | None
    pdf_path: pathlib.Path | str | None
    markdown_path: pathlib.Path | str | None
    html_path: pathlib.Path | str | None
    png_path: pathlib.Path | str | None
    dont_generate_typst: bool | None
    dont_generate_html: bool | None
    dont_generate_markdown: bool | None
    dont_generate_pdf: bool | None
    dont_generate_png: bool | None
    overrides: dict[str, str] | None


def build_rendercv_dictionary(
    main_input_file_path_or_contents: pathlib.Path | str,
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> CommentedMap:
    """Merge main YAML with overlays and CLI overrides into final dictionary.

    Why:
        Users need modular configuration (separate design/locale files) and
        quick testing (CLI overrides). This pipeline applies all modifications
        before validation, ensuring users see complete configuration errors.

    Example:
        ```py
        data = build_rendercv_dictionary(
            pathlib.Path("cv.yaml"),
            design_file_path_or_contents=pathlib.Path("classic.yaml"),
            overrides={"cv.phone": "+1234567890"}
        )
        # data contains merged cv + design + overrides
        ```

    Args:
        main_input_file_path_or_contents: Primary CV YAML file or string.
        kwargs: Optional YAML overlay paths, output paths, generation flags, and CLI overrides.

    Returns:
        Merged dictionary ready for validation.
    """
    input_dict = read_yaml(main_input_file_path_or_contents)

    # Optional YAML overlays
    yaml_overlays: dict[str, pathlib.Path | str | None] = {
        "design": kwargs.get("design_file_path_or_contents"),
        "locale": kwargs.get("locale_file_path_or_contents"),
        "settings": kwargs.get("settings_file_path_or_contents"),
    }

    for key, path in yaml_overlays.items():
        if path:
            input_dict[key] = read_yaml(path)[key]

    # Optional render-command overrides
    render_overrides: dict[str, pathlib.Path | str | bool | None] = {
        "typst_path": kwargs.get("typst_path"),
        "pdf_path": kwargs.get("pdf_path"),
        "markdown_path": kwargs.get("markdown_path"),
        "html_path": kwargs.get("html_path"),
        "png_path": kwargs.get("png_path"),
        "dont_generate_typst": kwargs.get("dont_generate_typst"),
        "dont_generate_html": kwargs.get("dont_generate_html"),
        "dont_generate_markdown": kwargs.get("dont_generate_markdown"),
        "dont_generate_pdf": kwargs.get("dont_generate_pdf"),
        "dont_generate_png": kwargs.get("dont_generate_png"),
    }

    input_dict.setdefault("settings", {}).setdefault("render_command", {})

    for key, value in render_overrides.items():
        if value:
            input_dict["settings"]["render_command"][key] = value

    overrides = kwargs.get("overrides")
    if overrides:
        input_dict = apply_overrides_to_dictionary(input_dict, overrides)

    return input_dict


def build_rendercv_model_from_commented_map(
    commented_map: CommentedMap,
    input_file_path: pathlib.Path | None = None,
) -> RenderCVModel:
    """Validate merged dictionary and build Pydantic model with error mapping.

    Why:
        Validation transforms raw YAML into type-safe objects. When validation
        fails, CommentedMap metadata enables precise error location reporting
        instead of generic Pydantic messages.

    Args:
        commented_map: Merged dictionary with line/column metadata.
        input_file_path: Source file path for context and photo resolution.

    Returns:
        Validated RenderCVModel instance.
    """
    try:
        model = RenderCVModel.model_validate(
            commented_map,
            context={
                "context": ValidationContext(
                    input_file_path=input_file_path,
                    current_date=commented_map.get("settings", {}).get(
                        "current_date", None
                    ),
                )
            },
        )
    except pydantic.ValidationError as e:
        validation_errors = parse_validation_errors(e, commented_map)
        raise RenderCVUserValidationError(validation_errors) from e

    return model


def build_rendercv_dictionary_and_model(
    main_input_file_path_or_contents: pathlib.Path | str,
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> tuple[CommentedMap, RenderCVModel]:
    """Complete pipeline from raw input to validated model.

    Why:
        Main entry point for render command combines merging and validation
        in one call. Returns both dictionary and model because error handlers
        need dictionary metadata for location mapping.

    Example:
        ```py
        data, model = build_rendercv_dictionary_and_model(
            pathlib.Path("cv.yaml"),
            pdf_path="output.pdf"
        )
        # model.cv.name is validated, data preserves YAML line numbers
        ```

    Args:
        main_input_file_path_or_contents: Primary CV YAML file or string.
        kwargs: Optional YAML overlay paths, output paths, generation flags, and CLI overrides.

    Returns:
        Tuple of merged dictionary and validated model.
    """
    d = build_rendercv_dictionary(main_input_file_path_or_contents, **kwargs)
    input_file_path = (
        main_input_file_path_or_contents
        if isinstance(main_input_file_path_or_contents, pathlib.Path)
        else None
    )
    m = build_rendercv_model_from_commented_map(d, input_file_path)
    return d, m
