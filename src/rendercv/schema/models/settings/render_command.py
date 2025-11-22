import pathlib

import pydantic

from ..base import BaseModelWithoutExtraKeys
from ..path import ExistingInputRelativePath, PlannedInputRelativePath

file_path_placeholders_description = """The following placeholders can be used:

- FULL_MONTH_NAME: Full name of the month (e.g., January)
- MONTH_ABBREVIATION: Abbreviation of the month (e.g., Jan)
- MONTH: Month as a number (e.g., 1)
- MONTH_IN_TWO_DIGITS: Month as a number in two digits (e.g., 01)
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


class RenderCommand(BaseModelWithoutExtraKeys):
    design: ExistingInputRelativePath | None = pydantic.Field(
        default=None,
        description="The file path to the YAML file that contains the `design` field.",
    )
    locale: ExistingInputRelativePath | None = pydantic.Field(
        default=None,
        description="The file path to the YAML file that contains the `locale` field.",
    )
    typst_path: PlannedInputRelativePath = pydantic.Field(
        default=pathlib.Path("rendercv_output/NAME_IN_SNAKE_CASE_CV.typ"),
        description=(
            "Path to the output Typst file, relative to the input YAML file. The"
            " default value is `rendercv_output/NAME_IN_SNAKE_CASE_CV.typ`.\n\n"
            " `rendercv_output/NAME_IN_SNAKE_CASE_CV.typ`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    pdf_path: PlannedInputRelativePath = pydantic.Field(
        default=pathlib.Path("rendercv_output/NAME_IN_SNAKE_CASE_CV.pdf"),
        description=(
            "Path to the output PDF file, relative to the input YAML file. The default"
            " value is `rendercv_output/NAME_IN_SNAKE_CASE_CV.pdf`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    markdown_path: PlannedInputRelativePath = pydantic.Field(
        default=pathlib.Path("rendercv_output/NAME_IN_SNAKE_CASE_CV.md"),
        title="Markdown Path",
        description=(
            "Path to the output Markdown file, relative to the input YAML file. The"
            " default value is `rendercv_output/NAME_IN_SNAKE_CASE_CV.md`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    html_path: PlannedInputRelativePath = pydantic.Field(
        default=pathlib.Path("rendercv_output/NAME_IN_SNAKE_CASE_CV.html"),
        description=(
            "Path to the output HTML file, relative to the input YAML file. The default"
            " value is `rendercv_output/NAME_IN_SNAKE_CASE_CV.html`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    png_path: PlannedInputRelativePath = pydantic.Field(
        default=pathlib.Path("rendercv_output/NAME_IN_SNAKE_CASE_CV.png"),
        description=(
            "Path to the output PNG file, relative to the input YAML file. The default"
            " value is `rendercv_output/NAME_IN_SNAKE_CASE_CV.png`.\n\n"
            f"{file_path_placeholders_description}"
        ),
    )
    dont_generate_markdown: bool = pydantic.Field(
        default=False,
        title="Don't Generate Markdown",
        description=(
            "If `True`, the Markdown file will not be generated. Disabling Markdown"
            " generation implicitly disables HTML. The default value is"
            " `False`."
        ),
    )
    dont_generate_html: bool = pydantic.Field(
        default=False,
        title="Don't Generate HTML",
        description=(
            "If `True`, the HTML file will not be generated. The default value is"
            " `False`."
        ),
    )
    dont_generate_typst: bool = pydantic.Field(
        default=False,
        title="Don't Generate Typst",
        description=(
            "If `True`, the Typst file will not be generated. Disabling Typst"
            " generation implicitly disables PDF and PNG. The default value is"
            " `False`."
        ),
    )
    dont_generate_pdf: bool = pydantic.Field(
        default=False,
        title="Don't Generate PDF",
        description=(
            "If `True`, the PDF file will not be generated. The default value is"
            " `False`."
        ),
    )
    dont_generate_png: bool = pydantic.Field(
        default=False,
        title="Don't Generate PNG",
        description=(
            "If `True`, the PNG file will not be generated. The default value is"
            " `False`."
        ),
    )
