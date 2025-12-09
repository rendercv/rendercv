import pathlib

from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path
from .templater.templater import render_full_template


def generate_typst(rendercv_model: RenderCVModel) -> pathlib.Path | None:
    """Generate Typst source file from CV model via Jinja2 templates.

    Why:
        Typst is the intermediate format before PDF/PNG compilation. Templates
        convert validated model data to Typst markup with proper formatting,
        fonts, and styling from design options.

    Args:
        rendercv_model: Validated CV model with content and design.

    Returns:
        Path to generated Typst file, or None if generation disabled.
    """
    if rendercv_model.settings.render_command.dont_generate_typst:
        return None
    typst_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.typst_path
    )
    typst_contents = render_full_template(rendercv_model, "typst")
    typst_path.write_text(typst_contents, encoding="utf-8")
    return typst_path
