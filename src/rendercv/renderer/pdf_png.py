import functools
import pathlib
import shutil

import rendercv_fonts
import typst

from rendercv.exception import RenderCVInternalError
from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path


def generate_pdf(
    rendercv_model: RenderCVModel, typst_path: pathlib.Path | None
) -> pathlib.Path | None:
    """Compile Typst source to PDF using typst-py compiler.

    Why:
        PDF is the primary output format for CVs. Typst compilation produces
        high-quality PDFs with proper fonts, layout, and typography from the
        intermediate Typst markup.

    Args:
        rendercv_model: CV model for path resolution and photo handling.
        typst_path: Path to Typst source file to compile.

    Returns:
        Path to generated PDF file, or None if generation disabled.
    """
    if rendercv_model.settings.render_command.dont_generate_pdf or typst_path is None:
        return None
    pdf_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.pdf_path
    )
    typst_compiler = get_typst_compiler(typst_path, rendercv_model._input_file_path)
    copy_photo_next_to_typst_file(rendercv_model, typst_path)
    typst_compiler.compile(format="pdf", output=pdf_path)

    return pdf_path


def generate_png(
    rendercv_model: RenderCVModel, typst_path: pathlib.Path | None
) -> list[pathlib.Path] | None:
    """Compile Typst source to PNG images using typst-py compiler.

    Why:
        PNG format enables CV preview in web applications and README files.
        Multi-page CVs produce multiple PNG files with sequential numbering.

    Args:
        rendercv_model: CV model for path resolution and photo handling.
        typst_path: Path to Typst source file to compile.

    Returns:
        List of paths to generated PNG files, or None if generation disabled.
    """
    if rendercv_model.settings.render_command.dont_generate_png or typst_path is None:
        return None
    png_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.png_path
    )
    
    pattern = f"{png_path.stem}_*.png"
    for existing_png_file in png_path.parent.glob(pattern):
        if existing_png_file.is_file():
            existing_png_file.unlink()
    
    typst_compiler = get_typst_compiler(typst_path, rendercv_model._input_file_path)
    copy_photo_next_to_typst_file(rendercv_model, typst_path)
    png_files_bytes = typst_compiler.compile(format="png")

    if not isinstance(png_files_bytes, list):
        png_files_bytes = [png_files_bytes]

    png_files = []
    for i, png_file_bytes in enumerate(png_files_bytes):
        if png_file_bytes is None:
            raise RenderCVInternalError("Typst compiler returned None for PNG bytes")
        png_file = png_path.parent / (png_path.stem + f"_{i + 1}.png")
        png_file.write_bytes(png_file_bytes)
        png_files.append(png_file)

    return png_files if png_files else None


def copy_photo_next_to_typst_file(
    rendercv_model: RenderCVModel, typst_path: pathlib.Path
) -> None:
    """Copy CV photo to Typst file directory for compilation.

    Why:
        Typst compiler resolves image paths relative to source file location.
        Copying photo ensures compilation succeeds regardless of original
        photo location.

    Args:
        rendercv_model: CV model containing photo path.
        typst_path: Path to Typst source file.
    """
    if rendercv_model.cv.photo:
        photo_path = rendercv_model.cv.photo
        copy_to = typst_path.parent / photo_path.name
        if photo_path != copy_to:
            shutil.copy(
                rendercv_model.cv.photo,
                typst_path.parent / rendercv_model.cv.photo.name,
            )


@functools.lru_cache(maxsize=1)
def get_typst_compiler(
    file_path: pathlib.Path,
    input_file_path: pathlib.Path | None,
) -> typst.Compiler:
    """Create cached Typst compiler with font paths configured.

    Why:
        Compiler initialization is expensive. Caching enables reuse for both
        PDF and PNG generation. Font paths include package fonts and optional
        user fonts from input file directory.

    Args:
        file_path: Typst source file to compile.
        input_file_path: Original input file path for relative font resolution.

    Returns:
        Configured Typst compiler instance.
    """
    return typst.Compiler(
        file_path,
        font_paths=[
            *rendercv_fonts.paths_to_font_folders,
            (
                input_file_path.parent / "fonts"
                if input_file_path
                else pathlib.Path.cwd() / "fonts"
            ),
        ],
    )
