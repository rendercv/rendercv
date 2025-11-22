import pathlib

from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path
from .templater.templater import render_full_template


def render_typst_to_file(rendercv_model: RenderCVModel) -> pathlib.Path | None:
    if rendercv_model.settings.render_command.dont_generate_typst:
        return None
    typst_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.typst_path
    )
    typst_contents = render_full_template(rendercv_model, "typst")
    typst_path.write_text(typst_contents)
    return typst_path
