import functools
import pathlib
from typing import Literal

import jinja2

from rendercv.schema.models.rendercv_model import RenderCVModel

from .markdown_parser import markdown_to_html
from .model_processor import process_model

templates_directory = pathlib.Path(__file__).parent / "templates"


@functools.lru_cache(maxsize=1)
def get_jinja2_environment(
    input_file_path: pathlib.Path | None = None,
) -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            [
                (  # To allow users to override the templates:
                    input_file_path.parent if input_file_path else pathlib.Path.cwd()
                ),
                templates_directory,
            ]
        ),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_full_template(
    rendercv_model: RenderCVModel, file_type: Literal["typst", "markdown"]
) -> str:
    extension = {
        "typst": "typ",
        "markdown": "md",
    }[file_type]

    rendercv_model = process_model(rendercv_model, file_type)

    if file_type == "typst":
        preamble = render_single_template(
            f"{file_type}/Preamble.j2.{extension}", rendercv_model
        )
    else:
        preamble = ""

    header = render_single_template(
        f"{file_type}/Header.j2.{extension}", rendercv_model
    )
    code = f"{preamble}\n\n{header}\n"
    for rendercv_section in rendercv_model.cv.rendercv_sections:
        section_beginning = render_single_template(
            f"{file_type}/SectionBeginning.j2.{extension}",
            rendercv_model,
            section_title=rendercv_section.title,
            entry_type=rendercv_section.entry_type,
        )
        section_ending = render_single_template(
            f"{file_type}/SectionEnding.j2.{extension}",
            rendercv_model,
            entry_type=rendercv_section.entry_type,
        )
        entry_codes = []
        for entry in rendercv_section.entries:
            entry_code = render_single_template(
                f"{file_type}/entries/{rendercv_section.entry_type}.j2.{extension}",
                rendercv_model,
                entry=entry,
            )
            entry_codes.append(entry_code)
        entries_code = "\n\n".join(entry_codes)
        section_code = f"{section_beginning}\n{entries_code}\n{section_ending}"
        code += f"\n{section_code}"

    return code


def render_html(rendercv_model: RenderCVModel, markdown: str) -> str:
    html_body = markdown_to_html(markdown)
    return render_single_template("html/Full.html", rendercv_model, html_body=html_body)


def render_single_template(
    relative_template_path: str,
    rendercv_model: RenderCVModel,
    **kwargs,
) -> str:
    template = get_jinja2_environment(rendercv_model._input_file_path).get_template(
        relative_template_path
    )
    return template.render(
        cv=rendercv_model.cv,
        design=rendercv_model.design,
        locale=rendercv_model.locale,
        settings=rendercv_model.settings,
        **kwargs,
    )
