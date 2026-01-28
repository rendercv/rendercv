import pathlib

from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path
from .templater.templater import render_html


def generate_html(
    rendercv_model: RenderCVModel, markdown_path: pathlib.Path | None
) -> pathlib.Path | None:
    """Generate HTML file from Markdown source with styling.

    Why:
        HTML format enables web hosting and sharing CVs online. Converts
        Markdown to HTML body and wraps with CSS styling and metadata.

    Args:
        rendercv_model: CV model for path resolution and rendering context.
        markdown_path: Path to Markdown source file.

    Returns:
        Path to generated HTML file, or None if generation disabled.
    """
    if (
        rendercv_model.settings.render_command.dont_generate_html
        or markdown_path is None
    ):
        return None
    html_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.html_path
    )
    html_contents = render_html(
        rendercv_model, markdown_path.read_text(encoding="utf-8")
    )
    html_path.write_text(html_contents, encoding="utf-8")
    return html_path
