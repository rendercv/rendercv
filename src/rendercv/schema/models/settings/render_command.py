import pathlib

import pydantic

from ..base import BaseModelWithoutExtraKeys
from ..path import ExistingPathRelativeToInput, PlannedPathRelativeToInput

file_path_placeholders_description = """The following placeholders can be used:

- OUTPUT_FOLDER: The output folder path (e.g., rendercv_output)
- CURRENT_DATE: The current date in the `single_date` format (e.g., Jan 2024)
- MONTH_NAME: Full name of the month (e.g., January)
- MONTH_ABBREVIATION: Abbreviation of the month (e.g., Jan)
- MONTH: Month as a number (e.g., 1)
- MONTH_IN_TWO_DIGITS: Month as a number in two digits (e.g., 01)
- DAY: Day of the month (e.g., 5)
- DAY_IN_TWO_DIGITS: Day of the month in two digits (e.g., 05)
- DAY_ORDINAL: Day of the month as an ordinal (e.g., 5th)
- YEAR: Year as a number (e.g., 2024)
- YEAR_IN_TWO_DIGITS: Year as a number in two digits (e.g., 24)
- NAME: The name of the CV owner (e.g., John Doe)
- NAME_IN_SNAKE_CASE: The name in snake case (e.g., John_Doe)
- NAME_IN_LOWER_SNAKE_CASE: The name in lower snake case (e.g., john_doe)
- NAME_IN_UPPER_SNAKE_CASE: The name in upper snake case (e.g., JOHN_DOE)
- NAME_IN_KEBAB_CASE: The name in kebab case (e.g., John-Doe)
- NAME_IN_LOWER_KEBAB_CASE: The name in lower kebab case (e.g., john-doe)
- NAME_IN_UPPER_KEBAB_CASE: The name in upper kebab case (e.g., JOHN-DOE)
"""


output_formats = ("typst", "pdf", "markdown", "html", "png", "svg")


class RenderCommand(BaseModelWithoutExtraKeys):
    output_folder: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("rendercv_output"),
        description=(
            "Base output folder for all generated files. The default value is"
            " `rendercv_output`. Referenced as `OUTPUT_FOLDER` in output path"
            " defaults.\n\n"
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
    overlays: list[ExistingPathRelativeToInput] = pydantic.Field(
        default=[],
        description=(
            "Paths to YAML files that are merged over the input file, in order, like"
            " a part of a CV in another file. An overlay has the structure of an"
            " input file: its mappings are merged into the input's, and its other"
            " values (text, lists) replace the input's. Overlays given with"
            " `--overlay` are merged after these. The default value is `[]`."
        ),
    )
    typst_path: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.typ"),
        description=(
            "Output path for the Typst file, relative to the input YAML file. The"
            " default value is `OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.typ`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    pdf_path: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.pdf"),
        description=(
            "Output path for the PDF file, relative to the input YAML file. The default"
            " value is `OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.pdf`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    markdown_path: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.md"),
        title="Markdown Path",
        description=(
            "Output path for the Markdown file, relative to the input YAML file. The"
            " default value is `OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.md`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    html_path: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.html"),
        description=(
            "Output path for the HTML file, relative to the input YAML file. The"
            " default value is `OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.html`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    png_path: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.png"),
        description=(
            "Output path for PNG files, relative to the input YAML file. The default"
            " value is `OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.png`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    svg_path: PlannedPathRelativeToInput = pydantic.Field(
        default=pathlib.Path("OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.svg"),
        title="SVG Path",
        description=(
            "Output path for SVG files, one per page, relative to the input YAML"
            " file. The default value is `OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.svg`.\n\n"
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
            "Skip saving the Typst source file. PDF, PNG, and SVG generation are"
            " unaffected. The default value is `false`."
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
    dont_generate_svg: bool = pydantic.Field(
        default=False,
        title="Don't Generate SVG",
        description="Skip SVG generation. The default value is `false`.",
    )

    @property
    def enabled_outputs(self) -> set[str]:
        """The formats to generate. HTML is made from Markdown, so it needs it."""
        enabled = {
            output_format
            for output_format in output_formats
            if not getattr(self, f"dont_generate_{output_format}")
        }
        if "markdown" not in enabled:
            enabled.discard("html")
        return enabled
