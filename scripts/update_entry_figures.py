import pathlib
import tempfile

import fitz
import pdfCropMargins

from rendercv.renderer.pdf_png import generate_pdf
from rendercv.renderer.typst import generate_typst
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.rendercv_model_builder import build_rendercv_dictionary_and_model
from rendercv.schema.yaml_reader import read_yaml

repository_root = pathlib.Path(__file__).parent.parent
rendercv_path = repository_root / "rendercv"
image_assets_directory = repository_root / "docs" / "assets" / "images"


def pdf_to_png(pdf_file_path: pathlib.Path) -> list[pathlib.Path]:
    # check if the file exists:
    if not pdf_file_path.is_file():
        message = f"The file {pdf_file_path} doesn't exist!"
        raise FileNotFoundError(message)

    # convert the PDF to PNG:
    png_directory = pdf_file_path.parent
    png_file_name = pdf_file_path.stem
    png_files = []
    pdf = fitz.open(pdf_file_path)  # open the PDF file
    for page in pdf:  # iterate the pages
        image = page.get_pixmap(dpi=300)
        assert page.number is not None
        png_file_path = png_directory / f"{png_file_name}_{page.number + 1}.png"
        image.save(png_file_path)
        png_files.append(png_file_path)

    return png_files


entries = read_yaml(repository_root / "docs" / "user_guide" / "sample_entries.yaml")
entry_types = entries.keys()
themes = available_themes

with tempfile.TemporaryDirectory() as temporary_directory:
    # Create temporary directory
    temporary_directory_path = pathlib.Path(temporary_directory)
    for theme in themes:
        design_dictionary = {
            "theme": theme,
            "page": {
                "show_page_numbering": False,
                "show_last_updated_date": False,
            },
        }

        for entry_type in entry_types:
            # Create data model with only one section and one entry
            typst_path = temporary_directory_path / "typst.typ"
            pdf_path = temporary_directory_path / "pdf.pdf"
            _, model = build_rendercv_dictionary_and_model(
                RenderCVModel(
                    cv=Cv(sections={entry_type: [entries[entry_type]]}),
                ).model_dump_json(),
                typst_path=typst_path,
                pdf_path=pdf_path,
                overrides={
                    "design": {  # pyright: ignore[reportArgumentType]
                        "theme": theme,
                        "page": {"show_footer": False, "show_top_note": False},
                    }
                },
            )

            # Render
            generate_typst(model)
            generate_pdf(model, typst_path)

            # Prepare output directory and file path
            output_directory = image_assets_directory / theme
            output_directory.mkdir(parents=True, exist_ok=True)

            output_pdf_file_path = temporary_directory_path / f"{entry_type}.pdf"
            # Crop margins
            pdfCropMargins.crop(
                argv_list=[
                    "-p4",
                    "100",
                    "0",
                    "100",
                    "0",
                    "-a4",
                    "0",
                    "-30",
                    "0",
                    "-30",
                    "-o",
                    str(output_pdf_file_path.absolute()),
                    str(pdf_path.absolute()),
                ]
            )

            # Convert PDF to image
            png_file_path = pdf_to_png(output_pdf_file_path)[0]
            desired_png_file_path = image_assets_directory / theme / f"{entry_type}.png"

            # If image exists, remove it
            if desired_png_file_path.exists():
                desired_png_file_path.unlink()

            # Move image to desired location
            png_file_path.rename(desired_png_file_path)


print("Entry figures generated successfully.")  # NOQA: T201
