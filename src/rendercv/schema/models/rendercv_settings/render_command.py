import pathlib

import pydantic

from ..base import BaseModelWithoutExtraKeys

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
    design: pathlib.Path | None = pydantic.Field(
        default=None,
        description="The file path to the YAML file that contains the `design` field.",
    )
    locale: pathlib.Path | None = pydantic.Field(
        default=None,
        description="The file path to the YAML file that contains the `locale` field.",
    )
    output_folder_path: pathlib.Path = pydantic.Field(
        default=pathlib.Path("rendercv_output"),
        description=(
            "The path to the folder where the output files will be saved. "
            f"{file_path_placeholders_description}"
        ),
    )
    pdf_path: pathlib.Path | None = pydantic.Field(
        default=None,
        description=(
            "The path to copy the PDF file to. If it is not provided, the PDF file will"
            f" not be copied. {file_path_placeholders_description}"
        ),
    )
    typst_path: pathlib.Path | None = pydantic.Field(
        default=None,
        description=(
            "The path to copy the Typst file to. If it is not provided, the Typst file"
            f" will not be copied. {file_path_placeholders_description}"
        ),
    )
    html_path: pathlib.Path | None = pydantic.Field(
        default=None,
        description=(
            "The path to copy the HTML file to. If it is not provided, the HTML file"
            f" will not be copied. {file_path_placeholders_description}"
        ),
    )
    png_path: pathlib.Path | None = pydantic.Field(
        default=None,
        description=(
            "The path to copy the PNG file to. If it is not provided, the PNG file will"
            f" not be copied. {file_path_placeholders_description}"
        ),
    )
    markdown_path: pathlib.Path | None = pydantic.Field(
        default=None,
        title="Markdown Path",
        description=(
            "The path to copy the Markdown file to. If it is not provided, the Markdown"
            f" file will not be copied. {file_path_placeholders_description}"
        ),
    )

    dont_generate_html: bool = pydantic.Field(
        default=False,
        title="Don't Generate HTML",
        description=(
            "A boolean value to determine whether the HTML file will be generated. The"
            " default value is `False`."
        ),
    )

    dont_generate_markdown: bool = pydantic.Field(
        default=False,
        title="Don't Generate Markdown",
        description=(
            "A boolean value to determine whether the Markdown file will be generated."
            " The default value is `False`."
        ),
    )

    dont_generate_pdf: bool = pydantic.Field(
        default=False,
        title="Don't Generate PDF",
        description=(
            "A boolean value to determine whether the PDF file will be generated. The"
            " default value is `False`."
        ),
    )

    dont_generate_png: bool = pydantic.Field(
        default=False,
        title="Don't Generate PNG",
        description=(
            "A boolean value to determine whether the PNG file will be generated. The"
            " default value is `False`."
        ),
    )
    watch: bool = pydantic.Field(
        default=False,
        title="Re-run RenderCV When the Input File is Updated",
        description=(
            "A boolean value to determine whether to re-run RenderCV when the input"
            "file is updated. The default value is `False`."
        ),
    )
