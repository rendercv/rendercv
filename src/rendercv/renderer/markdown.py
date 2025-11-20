from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path
from .templater.templater import render_full_template


def render_markdown_to_file(rendercv_model: RenderCVModel) -> None:
    markdown_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.markdown_path
    )
    markdown_contents = render_full_template(rendercv_model, "markdown")
    markdown_path.write_text(markdown_contents)
