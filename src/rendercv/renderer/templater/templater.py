import pathlib
from typing import Literal

import jinja2

from rendercv.schema.models.rendercv_model import RenderCVModel

from .model_preprocessor import preprocess_model

templates_directory = pathlib.Path(__file__).parent / "templates"
jinja2_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        [
            pathlib.Path.cwd(),  # To allow users to override the templates
            templates_directory,
        ]
    ),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_template(
    relative_template_path: str,
    rendercv_model: RenderCVModel,
    **kwargs,
) -> str:
    template = jinja2_environment.get_template(relative_template_path)
    return template.render(
        cv=rendercv_model.cv,
        design=rendercv_model.design,
        locale=rendercv_model.locale,
        rendercv_settings=rendercv_model.rendercv_settings,
        **kwargs,
    )


def template_rendercv_file(
    rendercv_model: RenderCVModel, file_type: Literal["typst", "markdown"]
) -> str:
    extension = {
        "typst": "typ",
        "markdown": "md",
    }[file_type]

    rendercv_model = preprocess_model(rendercv_model, file_type)

    preamble = render_template(f"{file_type}/Preamble.j2.{extension}", rendercv_model)
    header = render_template(f"{file_type}/Header.j2.{extension}", rendercv_model)

    code = preamble + header
    for rendercv_section in rendercv_model.cv.rendercv_sections:
        section_beginning = render_template(
            f"{file_type}/SectionBeginning.j2.{extension}",
            rendercv_model,
            section_title=rendercv_section.title,
            entry_type=rendercv_section.entry_type,
        )
        section_ending = render_template(
            f"{file_type}/SectionEnding.j2.{extension}",
            rendercv_model,
            section_title=rendercv_section.title,
            entry_type=rendercv_section.entry_type,
        )
        entries_code = ""
        for entry in rendercv_section.entries:
            entry_code = render_template(
                f"{file_type}/entries/{rendercv_section.entry_type}.j2.{extension}",
                rendercv_model,
                entry=entry,
            )
            entries_code += entry_code
        section_code = section_beginning + entries_code + section_ending
        code += section_code

    return code
