import atexit
import functools
import pathlib
import shutil
import tempfile

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
    typst_compiler = get_typst_compiler(
        rendercv_model._input_file_path, typst_path.parent
    )
    copy_photo_next_to_typst_file(rendercv_model, typst_path)
    typst_compiler.compile(input=typst_path, format="pdf", output=pdf_path)

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

    typst_compiler = get_typst_compiler(
        rendercv_model._input_file_path, typst_path.parent
    )
    copy_photo_next_to_typst_file(rendercv_model, typst_path)
    png_files_bytes = typst_compiler.compile(input=typst_path, format="png")

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
    photo_path = rendercv_model.cv.photo
    if isinstance(photo_path, pathlib.Path):
        copy_to = typst_path.parent / photo_path.name
        if photo_path != copy_to:
            shutil.copy(photo_path, copy_to)


@functools.lru_cache(maxsize=1)
def get_local_package_path() -> pathlib.Path | None:
    """Set up local Typst package resolution for development.

    Why:
        During development, the rendercv-typst package version referenced in
        templates may not be published to the Typst registry yet. This detects
        if the rendercv-typst/ directory exists in the repository and creates a
        temporary package cache so the Typst compiler resolves the import
        locally. In production (installed via pip), rendercv-typst/ won't exist
        and the compiler falls back to the Typst registry.

    Returns:
        Path to temporary package cache directory, or None if not in development.
    """
    repository_root = pathlib.Path(__file__).parent.parent.parent.parent
    rendercv_typst_directory = repository_root / "rendercv-typst"
    typst_toml_path = rendercv_typst_directory / "typst.toml"

    if not typst_toml_path.is_file():
        return None

    version = None
    for line in typst_toml_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("version"):
            version = stripped.split("=", 1)[1].strip().strip('"')
            break

    if version is None:
        return None

    temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="rendercv-pkg-"))
    atexit.register(shutil.rmtree, str(temp_dir), True)

    package_directory = temp_dir / "preview" / "rendercv" / version
    shutil.copytree(
        rendercv_typst_directory,
        package_directory,
        ignore=shutil.ignore_patterns(".git*", "CHANGELOG.md", "*.pdf"),
    )

    return temp_dir


@functools.lru_cache(maxsize=1)
def get_typst_compiler(
    input_file_path: pathlib.Path | None,
    root: pathlib.Path,
) -> typst.Compiler:
    """Create cached Typst compiler with font paths configured.

    Why:
        Compiler initialization is expensive. Caching enables reuse across
        all compilations. The source file is passed per compile() call, so
        the compiler survives output filename changes (e.g., when cv.name
        changes). Font paths include package fonts and optional user fonts
        from input file directory.

    Args:
        input_file_path: Original input file path for relative font resolution.
        root: Root directory for Typst project. Must contain the input file.

    Returns:
        Configured Typst compiler instance.
    """
    return typst.Compiler(
        root=root,
        font_paths=[
            *rendercv_fonts.paths_to_font_folders,
            (
                input_file_path.parent / "fonts"
                if input_file_path
                else pathlib.Path.cwd() / "fonts"
            ),
        ],
        package_path=get_local_package_path(),
    )
