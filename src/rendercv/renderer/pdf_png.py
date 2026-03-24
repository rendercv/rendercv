import atexit
import functools
import pathlib
import shutil
import tempfile
import tomllib

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


def read_version_from_typst_toml(typst_toml_path: pathlib.Path) -> str:
    """Read the version field from a typst.toml file.

    Why:
        Multiple bundled Typst packages need their version extracted for
        directory layout. Centralizes the parsing logic.

    Args:
        typst_toml_path: Path to the typst.toml file.

    Returns:
        The version string.
    """
    data = tomllib.loads(typst_toml_path.read_text(encoding="utf-8"))
    try:
        return data["package"]["version"]
    except KeyError as e:
        message = f"Could not find version in {typst_toml_path}"
        raise RenderCVInternalError(message) from e


def install_bundled_typst_package(
    bundled_path: pathlib.Path,
    package_name: str,
    temp_dir: pathlib.Path,
    typ_files: list[str],
) -> None:
    """Copy a bundled Typst package into the temporary package cache.

    Why:
        The Typst compiler expects packages in a directory structure of
        preview/{name}/{version}/. This copies the required files from
        a bundled package into that layout.

    Args:
        bundled_path: Path to the bundled package directory.
        package_name: Name of the Typst package (used in directory structure).
        temp_dir: Root of the temporary package cache.
        typ_files: List of .typ filenames to copy alongside typst.toml.
    """
    version = read_version_from_typst_toml(bundled_path / "typst.toml")
    package_directory = temp_dir / "preview" / package_name / version
    package_directory.mkdir(parents=True)
    shutil.copy2(bundled_path / "typst.toml", package_directory / "typst.toml")
    for typ_file in typ_files:
        shutil.copy2(bundled_path / typ_file, package_directory / typ_file)


@functools.lru_cache(maxsize=1)
def get_package_path() -> pathlib.Path:
    """Set up local Typst package resolution from bundled Typst packages.

    Why:
        Bundled Typst packages (rendercv, fontawesome) are shipped inside the
        Python package so that PDF compilation works without downloading from
        Typst Universe. The Typst compiler expects packages in a directory
        structure of preview/{name}/{version}/, so this creates a temporary
        directory with that layout.

    Returns:
        Path to temporary package cache directory.
    """
    temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="rendercv-pkg-"))
    atexit.register(shutil.rmtree, str(temp_dir), True)

    renderer_dir = pathlib.Path(__file__).parent

    install_bundled_typst_package(
        bundled_path=renderer_dir / "rendercv_typst",
        package_name="rendercv",
        temp_dir=temp_dir,
        typ_files=["lib.typ"],
    )

    install_bundled_typst_package(
        bundled_path=renderer_dir / "typst_fontawesome",
        package_name="fontawesome",
        temp_dir=temp_dir,
        typ_files=[
            "lib.typ",
            "lib-impl.typ",
            "lib-gen-func.typ",
            "lib-gen-map.typ",
        ],
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
        package_path=get_package_path(),
    )
