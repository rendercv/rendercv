import pathlib

from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path
from .templater.templater import render_full_template


def generate_markdown(rendercv_model: RenderCVModel) -> pathlib.Path | None:
    """Generate Markdown file from CV model via Jinja2 templates.

    Why:
        Markdown provides human-readable CV format for version control and
        web platforms. Acts as intermediate format for HTML generation.

    Args:
        rendercv_model: Validated CV model with content.

    Returns:
        Path to generated Markdown file, or None if generation disabled.
    """
    if rendercv_model.settings.render_command.dont_generate_markdown:
        return None
    markdown_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.markdown_path
    )
    markdown_contents = render_full_template(rendercv_model, "markdown")
    markdown_path.write_text(markdown_contents, encoding="utf-8")
    return markdown_path
