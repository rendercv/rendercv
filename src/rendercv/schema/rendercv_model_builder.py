import pathlib
from datetime import date as Date
from typing import TypedDict, Unpack

from .models.context import ValidationContext
from .models.rendercv_model import RenderCVModel
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
    dont_generate_html: bool | None
    dont_generate_markdown: bool | None
    dont_generate_pdf: bool | None
    dont_generate_png: bool | None


def build_rendercv_dictionary(
    main_input_file_path_or_contents: pathlib.Path | str,
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> dict:
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
        "dont_generate_html": kwargs.get("dont_generate_html"),
        "dont_generate_markdown": kwargs.get("dont_generate_markdown"),
        "dont_generate_pdf": kwargs.get("dont_generate_pdf"),
        "dont_generate_png": kwargs.get("dont_generate_png"),
    }

    input_dict = input_dict.setdefault("settings", {}).setdefault("render_command", {})

    for key, value in render_overrides.items():
        if value:
            input_dict[key] = value

    return input_dict


def build_rendercv_model(
    main_input_file_path_or_contents: pathlib.Path | str,
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> RenderCVModel:
    return build_rendercv_model_from_dictionary(
        build_rendercv_dictionary(main_input_file_path_or_contents, **kwargs),
        (
            main_input_file_path_or_contents
            if isinstance(main_input_file_path_or_contents, pathlib.Path)
            else None
        ),
    )


def build_rendercv_model_from_dictionary(
    input_dictionary: dict,
    input_file_path: pathlib.Path | None = None,
) -> RenderCVModel:
    model = RenderCVModel.model_validate(
        input_dictionary,
        context={
            "context": ValidationContext(
                input_file_path=input_file_path or pathlib.Path(),
                date_today=input_dictionary.get("rendercv_settings", {}).get(
                    "date", Date.today()
                ),
            )
        },
    )
    model._input_file_path = input_file_path
    return model
