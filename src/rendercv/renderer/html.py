import pathlib

from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path
from .templater.templater import render_html


def render_html_to_file(
    rendercv_model: RenderCVModel, markdown_path: pathlib.Path
) -> None:
    html_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.html_path
    )
    html_contents = render_html(rendercv_model, markdown_path.read_text())
    html_path.write_text(html_contents)
