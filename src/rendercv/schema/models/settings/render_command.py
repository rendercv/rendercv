import pathlib

import pydantic

from ..base import BaseModelWithoutExtraKeys
from ..path import ExistingPathRelativeToInput, PlannedPathRelativeToInput

file_path_placeholders_description = """The following placeholders can be used:

- OUTPUT_FOLDER: The output folder path (e.g., build/en/)
- MONTH_NAME: Full name of the month (e.g., January)
- MONTH_ABBREVIATION: Abbreviation of the month (e.g., Jan)
- MONTH: Month as a number (e.g., 1)
- MONTH_IN_TWO_DIGITS: Month as a number in two digits (e.g., 01)
- DAY: Day of the month (e.g., 5)
- DAY_IN_TWO_DIGITS: Day of the month in two digits (e.g., 05)
- YEAR: Year as a number (e.g., 2024)
- YEAR_IN_TWO_DIGITS: Year as a number in two digits (e.g., 24)
- NAME: The name of the CV owner (e.g., John Doe)
- NAME_IN_SNAKE_CASE: The name of the CV owner in snake case (e.g., John_Doe)
- NAME_IN_LOWER_SNAKE_CASE: The name of the CV owner in lower snake case (e.g., john_doe)
- NAME_IN_UPPER_SNAKE_CASE: The name of the CV owner in upper snake case (e.g., JOHN_DOE)
- NAME_IN_KEBAB_CASE: The name of the CV owner in kebab case (e.g., John-Doe)
- NAME_IN_LOWER_KEBAB_CASE: The name of the CV owner in lower kebab case (e.g., john-doe)
- NAME_IN_UPPER_KEBAB_CASE: The name of the CV owner in upper kebab case (e.g., JOHN-DOE)
"""

DEFAULT_OUTPUT_FOLDER = "rendercv_output"


class RenderCommand(BaseModelWithoutExtraKeys):
    output_folder: pathlib.Path | None = pydantic.Field(
        default=None,
        description=(
            "Base output folder for all generated files. When set, this replaces the "
            "default `rendercv_output` folder in all output paths. Can also be "
            "referenced as `OUTPUT_FOLDER` placeholder in custom paths.\n\n"
            "Example: Setting `output_folder: build/en/` will output files to "
            "`build/en/NAME_IN_SNAKE_CASE_CV.pdf` instead of "
            "`rendercv_output/NAME_IN_SNAKE_CASE_CV.pdf`."
        ),
    )
    design: ExistingPathRelativeToInput | None = pydantic.Field(
        default=None,
        description="Path to a YAML file containing the `design` field.",
    )
    locale: ExistingPathRelativeToInput | None = pydantic.Field(
        default=None,
        description="Path to a YAML file containing the `locale` field.",
    )
    typst_path: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("rendercv_output/NAME_IN_SNAKE_CASE_CV.typ"),
        description=(
            "Output path for the Typst file, relative to the input YAML file. The"
            " default"
            " value is `rendercv_output/NAME_IN_SNAKE_CASE_CV.typ`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    pdf_path: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("rendercv_output/NAME_IN_SNAKE_CASE_CV.pdf"),
        description=(
            "Output path for the PDF file, relative to the input YAML file. The default"
            " value is `rendercv_output/NAME_IN_SNAKE_CASE_CV.pdf`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    markdown_path: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("rendercv_output/NAME_IN_SNAKE_CASE_CV.md"),
        title="Markdown Path",
        description=(
            "Output path for the Markdown file, relative to the input YAML file. The"
            " default value is `rendercv_output/NAME_IN_SNAKE_CASE_CV.md`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    html_path: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("rendercv_output/NAME_IN_SNAKE_CASE_CV.html"),
        description=(
            "Output path for the HTML file, relative to the input YAML file. The"
            " default"
            " value is `rendercv_output/NAME_IN_SNAKE_CASE_CV.html`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    png_path: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("rendercv_output/NAME_IN_SNAKE_CASE_CV.png"),
        description=(
            "Output path for PNG files, relative to the input YAML file. The default"
            " value"
            " is `rendercv_output/NAME_IN_SNAKE_CASE_CV.png`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    dont_generate_markdown: bool = pydantic.Field(
        default=False,
        title="Don't Generate Markdown",
        description=(
            "Skip Markdown generation. This also disables HTML generation. The default"
            " value is `false`."
        ),
    )
    dont_generate_html: bool = pydantic.Field(
        default=False,
        title="Don't Generate HTML",
        description="Skip HTML generation. The default value is `false`.",
    )
    dont_generate_typst: bool = pydantic.Field(
        default=False,
        title="Don't Generate Typst",
        description=(
            "Skip Typst generation. This also disables PDF and PNG generation. The"
            " default value is `false`."
        ),
    )
    dont_generate_pdf: bool = pydantic.Field(
        default=False,
        title="Don't Generate PDF",
        description="Skip PDF generation. The default value is `false`.",
    )
    dont_generate_png: bool = pydantic.Field(
        default=False,
        title="Don't Generate PNG",
        description="Skip PNG generation. The default value is `false`.",
    )

    @pydantic.model_validator(mode="before")
    @classmethod
    def apply_output_folder_to_default_paths(
        cls, data: dict[str, object]
    ) -> dict[str, object]:
        """Apply output_folder to paths that still use the default rendercv_output.

        When output_folder is set, this replaces 'rendercv_output' with the
        specified folder in all output paths that haven't been explicitly customized.
        This allows users to change the output directory with a single option while
        still permitting individual path overrides.

        This runs in 'before' mode to modify paths before they are converted to
        absolute paths by the PlannedPathRelativeToInput validator.
        """
        if not isinstance(data, dict):
            return data

        output_folder = data.get("output_folder")
        if output_folder is None:
            return data

        output_folder_str = str(output_folder)
        path_fields = ["typst_path", "pdf_path", "markdown_path", "html_path", "png_path"]

        for field_name in path_fields:
            path_value = data.get(field_name)

            # If path is not set, use default and apply output_folder
            if path_value is None:
                # Get the default value from field definition
                default_paths = {
                    "typst_path": f"{DEFAULT_OUTPUT_FOLDER}/NAME_IN_SNAKE_CASE_CV.typ",
                    "pdf_path": f"{DEFAULT_OUTPUT_FOLDER}/NAME_IN_SNAKE_CASE_CV.pdf",
                    "markdown_path": f"{DEFAULT_OUTPUT_FOLDER}/NAME_IN_SNAKE_CASE_CV.md",
                    "html_path": f"{DEFAULT_OUTPUT_FOLDER}/NAME_IN_SNAKE_CASE_CV.html",
                    "png_path": f"{DEFAULT_OUTPUT_FOLDER}/NAME_IN_SNAKE_CASE_CV.png",
                }
                default_path = default_paths[field_name]
                data[field_name] = default_path.replace(
                    DEFAULT_OUTPUT_FOLDER, output_folder_str, 1
                )
            else:
                path_str = str(path_value)
                # Replace OUTPUT_FOLDER placeholder
                if "OUTPUT_FOLDER" in path_str:
                    data[field_name] = path_str.replace("OUTPUT_FOLDER", output_folder_str)
                # Replace default rendercv_output folder
                elif path_str.startswith(DEFAULT_OUTPUT_FOLDER + "/") or path_str.startswith(
                    DEFAULT_OUTPUT_FOLDER + "\\"
                ):
                    data[field_name] = path_str.replace(
                        DEFAULT_OUTPUT_FOLDER, output_folder_str, 1
                    )

        return data
