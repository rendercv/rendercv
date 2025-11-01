import datetime
from typing import Literal

import pydantic

from .base import BaseModelWithoutExtraKeys


class RenderCVSettings(BaseModelWithoutExtraKeys):
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
    render_command: RenderCommandSettings | None = pydantic.Field(
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
    sort_entries: Literal["reverse-chronological", "chronological", "none"] = (
        pydantic.Field(
            default="none",
            title="Sort Entries",
            description=(
                "How the entries should be sorted based on their dates. The available"
                " options are 'reverse-chronological', 'chronological', and 'none'. The"
                " default value is 'none'."
            ),
        )
    )

    @pydantic.field_validator("date")
    @classmethod
    def mock_today(cls, value: datetime.date) -> datetime.date:
        """Mocks the current date for testing."""

        global DATE_INPUT  # NOQA: PLW0603

        DATE_INPUT = value

        return value
