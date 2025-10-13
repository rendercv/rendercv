"""
The `rendercv.models.rendercv_settings` module contains the data model of the
`rendercv_settings` field of the input file.
"""

import datetime
import pathlib
from typing import Optional

import pydantic

from .base import RenderCVBaseModelWithoutExtraKeys
from .computers import convert_string_to_path, replace_placeholders

file_path_placeholder_description = (
    "The following placeholders can be used:\n- FULL_MONTH_NAME: Full name of the"
    " month\n- MONTH_ABBREVIATION: Abbreviation of the month\n- MONTH: Month as a"
    " number\n- MONTH_IN_TWO_DIGITS: Month as a number in two digits\n- YEAR: Year as a"
    " number\n- YEAR_IN_TWO_DIGITS: Year as a number in two digits\n- NAME: The name of"
    " the CV owner\n- NAME_IN_SNAKE_CASE: The name of the CV owner in snake case\n-"
    " NAME_IN_LOWER_SNAKE_CASE: The name of the CV owner in lower snake case\n-"
    " NAME_IN_UPPER_SNAKE_CASE: The name of the CV owner in upper snake case\n-"
    " NAME_IN_KEBAB_CASE: The name of the CV owner in kebab case\n-"
    " NAME_IN_LOWER_KEBAB_CASE: The name of the CV owner in lower kebab case\n-"
    " NAME_IN_UPPER_KEBAB_CASE: The name of the CV owner in upper kebab case\n-"
    " FULL_MONTH_NAME: Full name of the month\n- MONTH_ABBREVIATION: Abbreviation of"
    " the month\n- MONTH: Month as a number\n- MONTH_IN_TWO_DIGITS: Month as a number"
    " in two digits\n- YEAR: Year as a number\n- YEAR_IN_TWO_DIGITS: Year as a number"
    ' in two digits\nThe default value is "MONTH_ABBREVIATION YEAR".\nThe default value'
    " is null."
)

file_path_placeholder_description_without_default = (
    file_path_placeholder_description.replace("\nThe default value is null.", "")
)

DATE_INPUT = datetime.date.today()


class RenderCommandSettings(RenderCVBaseModelWithoutExtraKeys):
    """This class is the data model of the `render` command's settings."""

    design: Optional[pathlib.Path] = pydantic.Field(
        default=None,
        title="`design` Field's YAML File",
        description=(
            "The file path to the yaml file containing the `design` field separately."
        ),
    )

    rendercv_settings: Optional[pathlib.Path] = pydantic.Field(
        default=None,
        title="`rendercv_settings` Field's YAML File",
        description=(
            "The file path to the yaml file containing the `rendercv_settings` field"
            " separately."
        ),
    )

    locale: Optional[pathlib.Path] = pydantic.Field(
        default=None,
        title="`locale` Field's YAML File",
        description=(
            "The file path to the yaml file containing the `locale` field separately."
        ),
    )

    output_folder_name: str = pydantic.Field(
        default="rendercv_output",
        title="Output Folder Name",
        description=(
            "The name of the folder where the output files will be saved."
            f" {file_path_placeholder_description_without_default}\nThe default value"
            ' is "rendercv_output".'
        ),
    )

    pdf_path: Optional[pathlib.Path] = pydantic.Field(
        default=None,
        title="PDF Path",
        description=(
            "The path to copy the PDF file to. If it is not provided, the PDF file will"
            f" not be copied. {file_path_placeholder_description}"
        ),
    )

    typst_path: Optional[pathlib.Path] = pydantic.Field(
        default=None,
        title="Typst Path",
        description=(
            "The path to copy the Typst file to. If it is not provided, the Typst file"
            f" will not be copied. {file_path_placeholder_description}"
        ),
    )

    html_path: Optional[pathlib.Path] = pydantic.Field(
        default=None,
        title="HTML Path",
        description=(
            "The path to copy the HTML file to. If it is not provided, the HTML file"
            f" will not be copied. {file_path_placeholder_description}"
        ),
    )

    png_path: Optional[pathlib.Path] = pydantic.Field(
        default=None,
        title="PNG Path",
        description=(
            "The path to copy the PNG file to. If it is not provided, the PNG file will"
            f" not be copied. {file_path_placeholder_description}"
        ),
    )

    markdown_path: Optional[pathlib.Path] = pydantic.Field(
        default=None,
        title="Markdown Path",
        description=(
            "The path to copy the Markdown file to. If it is not provided, the Markdown"
            f" file will not be copied. {file_path_placeholder_description}"
        ),
    )

    dont_generate_html: bool = pydantic.Field(
        default=False,
        title="Don't Generate HTML",
        description=(
            "A boolean value to determine whether the HTML file will be generated. The"
            " default value is False."
        ),
    )

    dont_generate_markdown: bool = pydantic.Field(
        default=False,
        title="Don't Generate Markdown",
        description=(
            "A boolean value to determine whether the Markdown file will be generated."
            ' The default value is "false".'
        ),
    )

    dont_generate_pdf: bool = pydantic.Field(
        default=False,
        title="Don't Generate PDF",
        description=(
            "A boolean value to determine whether the PDF file will be generated. The"
            " default value is False."
        ),
    )

    dont_generate_png: bool = pydantic.Field(
        default=False,
        title="Don't Generate PNG",
        description=(
            "A boolean value to determine whether the PNG file will be generated. The"
            " default value is False."
        ),
    )

    watch: bool = pydantic.Field(
        default=False,
        title="Re-run RenderCV When the Input File is Updated",
        description=(
            "A boolean value to determine whether to re-run RenderCV when the input"
            'file is updated. The default value is "false".'
        ),
    )

    @pydantic.field_validator(
        "output_folder_name",
        mode="before",
    )
    @classmethod
    def replace_placeholders(cls, value: str) -> str:
        """Replaces the placeholders in a string with the corresponding values."""
        return replace_placeholders(value)

    @pydantic.field_validator(
        "design",
        "locale",
        "rendercv_settings",
        "pdf_path",
        "typst_path",
        "html_path",
        "png_path",
        "markdown_path",
        mode="before",
    )
    @classmethod
    def convert_string_to_path(cls, value: Optional[str]) -> Optional[pathlib.Path]:
        """Converts a string to a `pathlib.Path` object by replacing the placeholders
        with the corresponding values. If the path is not an absolute path, it is
        converted to an absolute path by prepending the current working directory.
        """
        if value is None:
            return None

        return convert_string_to_path(value)


class RenderCVSettings(RenderCVBaseModelWithoutExtraKeys):
    """This class is the data model of the RenderCV settings."""

    model_config = pydantic.ConfigDict(title="RenderCV Settings")

    date: datetime.date = pydantic.Field(
        default=datetime.date.today(),
        title="Date",
        description=(
            "The date that will be used everywhere (e.g., in the output file names,"
            " last updated date, computation of time spans for the events that are"
            " currently happening, etc.). The default value is the current date."
        ),
        json_schema_extra={
            "default": None,
        },
    )
    render_command: Optional[RenderCommandSettings] = pydantic.Field(
        default=None,
        title="Render Command Settings",
        description=(
            "RenderCV's `render` command settings. They are the same as the command"
            " line arguments. CLI arguments have higher priority than the settings in"
            " the input file."
        ),
    )
    bold_keywords: list[str] = pydantic.Field(
        default=[],
        title="Bold Keywords",
        description=(
            "The keywords that will be bold in the output. The default value is an"
            " empty list."
        ),
    )

    @pydantic.field_validator("date")
    @classmethod
    def mock_today(cls, value: datetime.date) -> datetime.date:
        """Mocks the current date for testing."""

        global DATE_INPUT  # NOQA: PLW0603

        DATE_INPUT = value

        return value
