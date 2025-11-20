import pathlib

from rendercv.schema.models.rendercv_model import RenderCVModel

from .templater.templater import render_full_template


def create_typst_file(rendercv_model: RenderCVModel) -> pathlib.Path:
    typst_contents = render_full_template(rendercv_model, "typst")

    file_name_without_extension = create_a_file_name_without_extension_from_name(
        rendercv_model.cv.name
    )
    file_name = f"{file_name_without_extension}.typ"

    return create_a_file_and_write_contents_to_it(
        typst_contents,
        file_name,
        output_directory,
    )
