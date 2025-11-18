import pathlib
from typing import Literal

import jinja2

from rendercv.schema.models.rendercv_model import RenderCVModel

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
    template_folder: Literal[
        "typst", "typst/entries", "markdown", "markdown/entries", "html"
    ],
    template_file_name: str,
    rendercv_model: RenderCVModel,
    **kwargs,
) -> str:
    template = jinja2_environment.get_template(
        f"{template_folder}/{template_file_name}"
    )
    return template.render(
        cv=rendercv_model.cv,
        design=rendercv_model.design,
        locale=rendercv_model.locale,
        rendercv_settings=rendercv_model.rendercv_settings,
        **kwargs,
    )



def generate_typst_from_rendercv_model(rendercv_model: RenderCVModel) -> str:
    preamble = render_template("typst", "Preamble.j2.typ", rendercv_model)
    header = render_template("typst", "Header.j2.typ", rendercv_model)

    typst_code = preamble + header
    for rendercv_section in rendercv_model.cv.rendercv_sections:
        section_beginning = render_template(
            "typst",
            "SectionBeginning.j2.typ",
            rendercv_model,
            entry_type=rendercv_section.entry_type,
        )
        section_ending = render_template(
            "typst",
            "SectionEnding.j2.typ",
            rendercv_model,
            entry_type=rendercv_section.entry_type,
        )
        entries_code = ""
        for entry in rendercv_section.entries:
            entry_code = render_template(
                "typst/entries",
                f"{rendercv_section.entry_type}.j2.typ",
                rendercv_model,
                entry=entry,
            )
            entries_code += entry_code
        section_code = section_beginning + entries_code + section_ending
        typst_code += section_code

    return typst_code
