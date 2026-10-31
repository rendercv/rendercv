import pathlib
from collections.abc import Sequence
from typing import Any, TypedDict, Unpack

import pydantic
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

from rendercv.exception import (
    OVERLAY_SOURCE_TO_YAML_SOURCE,
    OverlaySourceKey,
    RenderCVUserValidationError,
    RenderCVValidationError,
    YamlLocation,
    YamlSource,
)

from .models.rendercv_model import RenderCVModel
from .models.validation_context import ValidationContext
from .override_dictionary import apply_overrides_to_dictionary, merge_overlay
from .pydantic_error_handling import (
    get_coordinates_of_a_key_in_a_yaml_object,
    parse_validation_errors,
)
from .yaml_reader import yaml


class BuildRendercvModelArguments(TypedDict, total=False):
    input_paths: tuple[pathlib.Path, ...]
    design_yaml_file: str | None
    locale_yaml_file: str | None
    settings_yaml_file: str | None
    # Sources (for error messages) and contents of the files merged over the input:
    overlay_yaml_files: list[tuple[YamlSource, str]] | None
    design_path: pathlib.Path | None
    locale_path: pathlib.Path | None
    output_folder: pathlib.Path | str | None
    typst_path: pathlib.Path | str | None
    pdf_path: pathlib.Path | str | None
    markdown_path: pathlib.Path | str | None
    html_path: pathlib.Path | str | None
    png_path: pathlib.Path | str | None
    svg_path: pathlib.Path | str | None
    dont_generate_typst: bool | None
    dont_generate_html: bool | None
    dont_generate_markdown: bool | None
    dont_generate_pdf: bool | None
    dont_generate_png: bool | None
    dont_generate_svg: bool | None
    overrides: dict[str, str] | None


def get_yaml_error_location(error: ruamel.yaml.YAMLError) -> YamlLocation | None:
    """Extract 1-indexed line/column coordinates from ruamel parser errors.

    Args:
        error: YAML parsing exception raised by ruamel.

    Returns:
        Start/end coordinates when available, otherwise None.
    """
    context_mark = getattr(error, "context_mark", None)
    problem_mark = getattr(error, "problem_mark", None)
    start_mark = context_mark or problem_mark
    end_mark = problem_mark or context_mark

    if start_mark is None or end_mark is None:
        return None

    return (
        (start_mark.line + 1, start_mark.column + 1),
        (end_mark.line + 1, end_mark.column + 1),
    )


def read_yaml_with_validation_errors(
    yaml_content: str, yaml_source: YamlSource
) -> CommentedMap:
    """Parse YAML content and convert parser failures into validation errors.

    Why:
        YAML syntax errors should use the same error pipeline as schema validation,
        so the CLI can display all input issues through one consistent path.

    Args:
        yaml_content: YAML string content.
        yaml_source: Which input file this YAML content came from.

    Returns:
        Parsed YAML map preserving source coordinates.

    Raises:
        RenderCVUserValidationError: If YAML cannot be parsed.
    """
    try:
        parsed = yaml.load(yaml_content)
        if not isinstance(parsed, dict):
            raise RenderCVUserValidationError(
                [
                    RenderCVValidationError(
                        schema_location=(),
                        yaml_location=get_coordinates_of_a_key_in_a_yaml_object(
                            parsed, ()
                        ),
                        yaml_source=yaml_source,
                        message="The YAML document must contain a mapping of fields.",
                        input="...",
                    )
                ]
            )
        return parsed
    except ruamel.yaml.YAMLError as e:
        parser_message = str(e).splitlines()[0].strip()
        if not parser_message.endswith("."):
            parser_message += "."

        raise RenderCVUserValidationError(
            validation_errors=[
                RenderCVValidationError(
                    schema_location=None,
                    yaml_location=get_yaml_error_location(e),
                    yaml_source=yaml_source,
                    message=f"This is not a valid YAML file. {parser_message}",
                    input="...",
                )
            ]
        ) from e


def build_rendercv_dictionary(
    main_yaml_file: str,
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> tuple[CommentedMap, list[tuple[YamlSource, CommentedMap]]]:
    """Merge main YAML with overlays and CLI overrides into final dictionary.

    Why:
        Each layer takes precedence over the previous ones: the main file, the
        files of the `settings`, `design`, and `locale` fields (which replace these
        fields), the overlay files (which are merged in order), and the CLI
        overrides of single values.

    Args:
        main_yaml_file: Primary CV YAML content string.
        kwargs: Optional YAML overlay strings, output paths, generation flags,
            and CLI overrides.

    Returns:
        Tuple of merged dictionary and the files laid over the main file, in order,
        with their documents (for error reporting).
    """
    input_dict = read_yaml_with_validation_errors(main_yaml_file, "main_yaml_file")

    yaml_overlays: dict[OverlaySourceKey, str | None] = {
        "settings": kwargs.get("settings_yaml_file"),
        "design": kwargs.get("design_yaml_file"),
        "locale": kwargs.get("locale_yaml_file"),
    }

    sources: list[tuple[YamlSource, CommentedMap]] = []
    for key, yaml_content in yaml_overlays.items():
        if yaml_content is not None:
            overlay_cm = read_yaml_with_validation_errors(
                yaml_content, OVERLAY_SOURCE_TO_YAML_SOURCE[key]
            )
            if key not in overlay_cm:
                raise RenderCVUserValidationError(
                    [
                        RenderCVValidationError(
                            schema_location=(key,),
                            yaml_location=get_coordinates_of_a_key_in_a_yaml_object(
                                overlay_cm, ()
                            ),
                            yaml_source=OVERLAY_SOURCE_TO_YAML_SOURCE[key],
                            message="This field is required.",
                            input="...",
                        )
                    ]
                )
            input_dict[key] = overlay_cm[key]
            sources.append((OVERLAY_SOURCE_TO_YAML_SOURCE[key], overlay_cm))

    for source, yaml_content in kwargs.get("overlay_yaml_files") or []:
        overlay = read_yaml_with_validation_errors(yaml_content, source)
        settings_overlay = overlay.get("settings")
        command_overlay = (
            settings_overlay.get("render_command")
            if isinstance(settings_overlay, dict)
            else None
        )
        if isinstance(command_overlay, dict):
            for role in ("design", "locale", "overlays"):
                if role in command_overlay:
                    location = ("settings", "render_command", role)
                    raise RenderCVUserValidationError(
                        [
                            RenderCVValidationError(
                                schema_location=location,
                                yaml_location=get_coordinates_of_a_key_in_a_yaml_object(
                                    overlay, location
                                ),
                                yaml_source=source,
                                message=(
                                    "General overlays cannot select input files. "
                                    "Put file references in the main or settings "
                                    "file, or use the corresponding CLI option."
                                ),
                                input=str(command_overlay[role]),
                            )
                        ]
                    )
        merge_overlay(input_dict, overlay)
        sources.append((source, overlay))

    render_overrides: dict[str, pathlib.Path | str | bool | None] = {
        "design": kwargs.get("design_path"),
        "locale": kwargs.get("locale_path"),
        "output_folder": kwargs.get("output_folder"),
        "typst_path": kwargs.get("typst_path"),
        "pdf_path": kwargs.get("pdf_path"),
        "markdown_path": kwargs.get("markdown_path"),
        "html_path": kwargs.get("html_path"),
        "png_path": kwargs.get("png_path"),
        "svg_path": kwargs.get("svg_path"),
        "dont_generate_typst": kwargs.get("dont_generate_typst"),
        "dont_generate_html": kwargs.get("dont_generate_html"),
        "dont_generate_markdown": kwargs.get("dont_generate_markdown"),
        "dont_generate_pdf": kwargs.get("dont_generate_pdf"),
        "dont_generate_png": kwargs.get("dont_generate_png"),
        "dont_generate_svg": kwargs.get("dont_generate_svg"),
    }

    settings = input_dict.setdefault("settings", {})
    if isinstance(settings, dict):
        render_command = settings.setdefault("render_command", {})
        if isinstance(render_command, dict):
            render_command.update(
                (key, value)
                for key, value in render_overrides.items()
                if value is not None
            )

    overrides = kwargs.get("overrides")
    if overrides:
        input_dict = apply_overrides_to_dictionary(input_dict, overrides)

    return input_dict, sources


def build_rendercv_model_from_commented_map(
    commented_map: CommentedMap | dict[str, Any],
    input_file_path: pathlib.Path | None = None,
    sources: Sequence[tuple[YamlSource, CommentedMap]] = (),
    input_paths: tuple[pathlib.Path, ...] = (),
) -> RenderCVModel:
    """Validate merged dictionary and build Pydantic model with error mapping.

    Args:
        commented_map: Merged dictionary with line/column metadata.
        input_file_path: Source file path for context and photo resolution.
        sources: The files laid over the main file, in order, with their documents
            (for correct error coordinates).

    Returns:
        Validated RenderCVModel instance.
    """
    settings = commented_map.get("settings")
    try:
        validation_context = {
            "context": ValidationContext(
                input_file_path=input_file_path,
                input_paths=input_paths,
                current_date=(
                    settings.get("current_date", "today")
                    if isinstance(settings, dict)
                    else "today"
                ),
            )
        }
        model = RenderCVModel.model_validate(commented_map, context=validation_context)
    except pydantic.ValidationError as e:
        validation_errors = parse_validation_errors(e, commented_map, sources)
        raise RenderCVUserValidationError(validation_errors) from e

    return model


def build_rendercv_dictionary_and_model(
    main_yaml_file: str,
    *,
    input_file_path: pathlib.Path | None = None,
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> tuple[CommentedMap, RenderCVModel]:
    """Complete pipeline from raw YAML string to validated model.

    Args:
        main_yaml_file: Primary CV YAML content string.
        input_file_path: Source file path for validation context (path resolution).
        kwargs: Optional YAML overlay strings, output paths, generation flags,
            and CLI overrides.

    Returns:
        Tuple of merged dictionary and validated model.
    """
    d, sources = build_rendercv_dictionary(main_yaml_file, **kwargs)
    m = build_rendercv_model_from_commented_map(
        d, input_file_path, sources, kwargs.get("input_paths", ())
    )
    return d, m
