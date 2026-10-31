from datetime import date as Date
from typing import Annotated, Literal

import pydantic

from ..base import BaseModelWithoutExtraKeys
from ..custom_error_types import invalid_input
from .render_command import RenderCommand


class Settings(BaseModelWithoutExtraKeys):
    current_date: Annotated[
        Date | Literal["today"],
        invalid_input(
            "rendercv_current_date",
            "This is not a valid `current_date`. Please use YYYY-MM-DD format or"
            ' "today".',
        ),
    ] = pydantic.Field(
        default="today",
        title="Date",
        description=(
            'The date to use as "current date" for filenames, the "last updated" label,'
            " and time span calculations. Defaults to the actual current date."
        ),
    )
    render_command: RenderCommand = pydantic.Field(
        # Validated like an input, to resolve its paths from the input file:
        default_factory=dict,
        title="Render Command Settings",
        description=(
            "Settings for the `render` command. These correspond to command-line"
            " arguments. CLI arguments take precedence over these settings."
        ),
    )
    bold_keywords: list[str] = pydantic.Field(
        default=[],
        title="Bold Keywords",
        description="Keywords to automatically bold in the output.",
    )
    sort_entries: Literal["none", "reverse-chronological", "chronological"] = (
        pydantic.Field(
            default="none",
            title="Sort Entries",
            description=(
                "The order of the entries of every section and subsection: as written"
                " (`none`), the most recent first (`reverse-chronological`), or the"
                " oldest first (`chronological`). Entries are ordered by their end"
                " dates, then their start dates, and the ones without dates come last"
                " in their written order. The default value is `none`."
            ),
        )
    )
    pdf_title: Annotated[
        str,
        pydantic.StringConstraints(pattern=r"\S"),
        invalid_input("rendercv_pdf_title", "Provide a nonblank title."),
    ] = pydantic.Field(
        default="NAME - CV",
        title="PDF Title",
        description=(
            "The title of the PDF and HTML documents, which PDF readers and browser"
            " tabs show. Available placeholders:\n"
            "- `NAME`: The CV owner's name from `cv.name`\n"
            "- `CURRENT_DATE`: Formatted date based on"
            " `design.templates.single_date`\n"
            "- `MONTH_NAME`: Full month name (e.g., January)\n"
            "- `MONTH_ABBREVIATION`: Abbreviated month name (e.g., Jan)\n"
            "- `MONTH`: Month number (e.g., 1)\n"
            "- `MONTH_IN_TWO_DIGITS`: Zero-padded month (e.g., 01)\n"
            "- `DAY`: Day of the month (e.g., 5)\n"
            "- `DAY_IN_TWO_DIGITS`: Zero-padded day (e.g., 05)\n"
            "- `YEAR`: Full year (e.g., 2025)\n"
            "- `YEAR_IN_TWO_DIGITS`: Two-digit year (e.g., 25)\n\n"
            "The default value is `NAME - CV`."
        ),
    )
    pdf_profile: Literal["accessible", "standard"] = pydantic.Field(
        default="accessible",
        title="PDF Profile",
        description=(
            "`accessible` makes the PDF conform to PDF/UA-1, the accessibility"
            " standard, which requires `cv.name` and alternative text for images in"
            " Typst code. `standard` makes an ordinary PDF without conformance"
            " checks. The default value is `accessible`."
        ),
    )
    _resolved_current_date: Date = pydantic.PrivateAttr()

    @pydantic.field_validator("bold_keywords")
    @classmethod
    def keep_unique_keywords(cls, value: list[str]) -> list[str]:
        """Remove duplicate keywords from bold list.

        Why:
            Users might accidentally list same keyword multiple times. Deduplication
            prevents redundant bold highlighting operations during rendering.

        Args:
            value: List of keywords potentially with duplicates.

        Returns:
            List with unique keywords only.
        """
        return list(dict.fromkeys(value))

    @pydantic.model_validator(mode="after")
    def resolve_current_date(self) -> "Settings":
        self._resolved_current_date = (
            Date.today() if self.current_date == "today" else self.current_date
        )
        return self
