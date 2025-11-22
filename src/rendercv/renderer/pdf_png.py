import functools
import pathlib

import rendercv_fonts
import typst

from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path


def generate_pdf(
    rendercv_model: RenderCVModel, typst_path: pathlib.Path | None
) -> pathlib.Path | None:
    if rendercv_model.settings.render_command.dont_generate_pdf or typst_path is None:
        return None
    pdf_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.pdf_path
    )
    typst_compiler = get_typst_compiler(typst_path, rendercv_model._input_file_path)
    typst_compiler.compile(format="pdf", output=pdf_path)

    return pdf_path


def generate_png(
    rendercv_model: RenderCVModel, typst_path: pathlib.Path | None
) -> list[pathlib.Path] | None:
    if rendercv_model.settings.render_command.dont_generate_png or typst_path is None:
        return None
    png_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.png_path
    )
    typst_compiler = get_typst_compiler(typst_path, rendercv_model._input_file_path)
    png_files_bytes = typst_compiler.compile(format="png")

    if not isinstance(png_files_bytes, list):
        png_files_bytes = [png_files_bytes]

    png_files = []
    for i, png_file_bytes in enumerate(png_files_bytes):
        assert png_file_bytes is not None
        png_file = png_path.parent / (png_path.stem + f"_{i + 1}.png")
        png_file.write_bytes(png_file_bytes)
        png_files.append(png_file)

    return png_files if png_files else None


@functools.lru_cache(maxsize=1)
def get_typst_compiler(
    file_path: pathlib.Path,
    input_file_path: pathlib.Path,
) -> typst.Compiler:
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
