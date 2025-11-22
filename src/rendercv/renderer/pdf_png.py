import functools
import pathlib

import rendercv_fonts
import typst

from rendercv.schema.models.rendercv_model import RenderCVModel

from .path_resolver import resolve_rendercv_file_path


def render_pdf_to_file(
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


def render_png_to_file(
    rendercv_model: RenderCVModel, typst_path: pathlib.Path | None
) -> list[pathlib.Path] | None:
    if rendercv_model.settings.render_command.dont_generate_png or typst_path is None:
        return None
    png_path = resolve_rendercv_file_path(
        rendercv_model, rendercv_model.settings.render_command.png_path
    )
    png_path = png_path.parent / (png_path.stem + "_{p}.png")
    typst_compiler = get_typst_compiler(typst_path, rendercv_model._input_file_path)
    typst_compiler.compile(format="png", output=png_path)
    png_files = list(png_path.parent.glob(f"{png_path.stem.replace('_{p}', '')}_*.png"))
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
