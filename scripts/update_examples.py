"""This script generates the `examples` folder in the repository root."""

import pathlib
import shutil
import tempfile

from rendercv.cli.render_command.run_rendercv import run_rendercv_quietly
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.sample_generator import create_sample_yaml_input_file

repository_root = pathlib.Path(__file__).parent.parent
rendercv_path = repository_root / "rendercv"
image_assets_directory = repository_root / "docs" / "assets" / "images"


examples_directory_path = pathlib.Path(__file__).parent.parent / "examples"

# Check if examples directory exists. If not, create it
if not examples_directory_path.exists():
    examples_directory_path.mkdir()

for theme in available_themes:
    yaml_file_path = (
        examples_directory_path / f"John_Doe_{theme.capitalize()}Theme_CV.yaml"
    )
    create_sample_yaml_input_file(
        file_path=yaml_file_path,
        name="John Doe",
        theme=theme,
        locale="english",
    )

    with tempfile.TemporaryDirectory() as temp_directory:
        temp_directory_path = pathlib.Path(temp_directory)
        # copy lib.typ to temp directory
        shutil.copy(
            repository_root / "lib.typ",
            temp_directory_path / "lib.typ",
        )
        run_rendercv_quietly(
            yaml_file_path,
            typst_path=temp_directory_path / f"{yaml_file_path.stem}.typ",
            pdf_path=examples_directory_path / f"{yaml_file_path.stem}.pdf",
            png_path=temp_directory_path / f"{yaml_file_path.stem}.png",
            dont_generate_html=True,
            dont_generate_markdown=True,
        )

        image_assets_directory.mkdir(parents=True, exist_ok=True)
        shutil.copy(
            temp_directory_path / f"{yaml_file_path.stem}_1.png",
            image_assets_directory / f"{theme}.png",
        )


print("Examples generated successfully.")  # NOQA: T201
