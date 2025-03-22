"""This script generates the example entry figures and creates an environment for
documentation templates using `mkdocs-macros-plugin`. For example, the content of the
example entries found in
"[Structure of the YAML Input File](https://docs.rendercv.com/user_guide/structure_of_the_yaml_input_file/)"
are coming from this script.
"""

import pathlib
import shutil
import tempfile

import fitz
import pdfCropMargins
import pydantic

import rendercv.data as data
import rendercv.renderer as renderer

repository_root = pathlib.Path(__file__).parent.parent
rendercv_path = repository_root / "rendercv"
image_assets_directory = repository_root / "docs" / "assets" / "images"


class SampleEntries(pydantic.BaseModel):
    education_entry: data.EducationEntry
    experience_entry: data.ExperienceEntry
    normal_entry: data.NormalEntry
    publication_entry: data.PublicationEntry
    one_line_entry: data.OneLineEntry
    bullet_entry: data.BulletEntry
    numbered_entry: data.NumberedEntry
    reversed_numbered_entry: data.ReversedNumberedEntry
    text_entry: str


def render_pngs_from_pdf(pdf_file_path: pathlib.Path) -> list[pathlib.Path]:
    """Render a PNG file for each page of the given PDF file.

    Args:
        pdf_file_path: The path to the PDF file.

    Returns:
        The paths to the rendered PNG files.
    """
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
        image = page.get_pixmap(dpi=300)  # type: ignore
        png_file_path = png_directory / f"{png_file_name}_{page.number + 1}.png"  # type: ignore
        image.save(png_file_path)
        png_files.append(png_file_path)

    return png_files


def generate_entry_figures():
    """Generate an image for each entry type and theme."""
    # Generate PDF figures for each entry type and theme
    entries = data.read_a_yaml_file(
        repository_root / "docs" / "user_guide" / "sample_entries.yaml"
    )
    entry_types = entries.keys()
    entries = SampleEntries(**entries)
    themes = data.available_themes

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
                data_model = data.RenderCVDataModel(
                    cv=data.CurriculumVitae(
                        sections={entry_type: [getattr(entries, entry_type)]}
                    ),
                    design=design_dictionary,
                )

                # Render
                typst_file_path = renderer.create_a_typst_file_and_copy_theme_files(
                    data_model, temporary_directory_path
                )
                pdf_file_path = renderer.render_a_pdf_from_typst(typst_file_path)

                # Prepare output directory and file path
                output_directory = image_assets_directory / theme
                output_directory.mkdir(parents=True, exist_ok=True)
                output_pdf_file_path = output_directory / f"{entry_type}.pdf"

                # Remove file if it exists
                if output_pdf_file_path.exists():
                    output_pdf_file_path.unlink()

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
                        str(pdf_file_path.absolute()),
                    ]
                )

                # Convert PDF to image
                png_file_path = render_pngs_from_pdf(output_pdf_file_path)[0]
                desired_png_file_path = output_pdf_file_path.with_suffix(".png")

                # If image exists, remove it
                if desired_png_file_path.exists():
                    desired_png_file_path.unlink()

                # Move image to desired location
                png_file_path.rename(desired_png_file_path)

                # Remove PDF file
                output_pdf_file_path.unlink()


def update_index():
    """Update index.md file by copying README.md file."""
    index_file_path = repository_root / "docs" / "index.md"
    readme_file_path = repository_root / "README.md"
    shutil.copy(readme_file_path, index_file_path)


if __name__ == "__main__":
    generate_entry_figures()
    print("Entry figures generated successfully.")  # NOQA: T201
