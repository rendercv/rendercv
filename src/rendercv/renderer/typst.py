import pathlib
import shutil

from rendercv.schema.models.rendercv_model import RenderCVModel

from .templater.templater import render_full_template


def generate_typst(
    rendercv_model: RenderCVModel, source: str | None = None
) -> pathlib.Path | None:
    """Save the Typst source of a CV, unless disabled.

    Args:
        rendercv_model: Validated CV model.
        source: The Typst source, if already rendered.

    Returns:
        Path to the Typst file, or None if its generation is disabled.
    """
    if rendercv_model.settings.render_command.dont_generate_typst:
        return None
    typst_path = rendercv_model._output_plan.paths["typst"]
    typst_path.parent.mkdir(parents=True, exist_ok=True)
    if source is None:
        source = render_full_template(rendercv_model, "typst")
    typst_path.write_text(source, encoding="utf-8")
    copy_photo_next_to_typst_file(rendercv_model, typst_path.parent)
    return typst_path


def copy_photo_next_to_typst_file(
    rendercv_model: RenderCVModel, directory: pathlib.Path
) -> None:
    """Copy the CV's photo into the directory of its Typst file.

    Why:
        The Typst source refers to the photo by the name that the output plan gives
        it, so that a saved Typst file compiles on its own, wherever the photo came
        from.

    Args:
        rendercv_model: CV model whose photo, if any, is a local file.
        directory: Directory of the Typst file.
    """
    photo = rendercv_model.cv.photo
    name = rendercv_model._output_plan.photo
    if not isinstance(photo, pathlib.Path) or name is None:
        return
    copy = directory / name
    if not (copy.exists() and copy.samefile(photo)):
        shutil.copy(photo, copy)
