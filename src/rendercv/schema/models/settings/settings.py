import datetime
from typing import Literal

import pydantic

from ..base import BaseModelWithoutExtraKeys
from .render_command import RenderCommand


class Settings(BaseModelWithoutExtraKeys):
    current_date: datetime.date | Literal["today"] = pydantic.Field(
        default="today",
        title="Date",
        description=(
            'The date to use as "current date" for filenames, the "last updated" label,'
            " and time span calculations. Defaults to the actual current date."
        ),
    )
    render_command: RenderCommand = pydantic.Field(
        default_factory=RenderCommand,
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
    pdf_title: str = pydantic.Field(
        default="NAME - CV",
        title="PDF Title",
        description=(
            "Title metadata for the PDF document. This appears in browser tabs and"
            " PDF readers. Available placeholders:\n"
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
    _resolved_current_date: datetime.date = pydantic.PrivateAttr()

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
        return list(set(value))

    @pydantic.model_validator(mode="after")
    def resolve_current_date(self) -> "Settings":
        self._resolved_current_date = (
            datetime.date.today() if self.current_date == "today" else self.current_date
        )
        return self
