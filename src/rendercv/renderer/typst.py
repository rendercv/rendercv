import pathlib
import tempfile

from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path
from .templater.templater import render_full_template


def generate_typst(rendercv_model: RenderCVModel) -> tuple[pathlib.Path, bool]:
    """Generate Typst source file from CV model via Jinja2 templates.

    Why:
        Typst is the intermediate format before PDF/PNG compilation. Templates
        convert validated model data to Typst markup with proper formatting,
        fonts, and styling from design options.

    Args:
        rendercv_model: Validated CV model with content and design.

    Returns:
        Tuple of (path to generated Typst file, is_temporary flag).
        When dont_generate_typst is True, returns a temporary file path
        that should be cleaned up after PDF/PNG generation.
    """
    typst_contents = render_full_template(rendercv_model, "typst")

    if rendercv_model.settings.render_command.dont_generate_typst:
        # Create temporary file for PDF/PNG compilation
        temp_dir = tempfile.mkdtemp(prefix="rendercv_")
        typst_path = pathlib.Path(temp_dir) / "cv.typ"
        typst_path.write_text(typst_contents, encoding="utf-8")
        return typst_path, True

    typst_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.typst_path
    )
    typst_path.write_text(typst_contents, encoding="utf-8")
    return typst_path, False
