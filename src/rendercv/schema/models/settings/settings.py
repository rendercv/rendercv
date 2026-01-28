import datetime

import pydantic

from ..base import BaseModelWithoutExtraKeys
from .render_command import RenderCommand


class Settings(BaseModelWithoutExtraKeys):
    current_date: datetime.date = pydantic.Field(
        default_factory=datetime.date.today,
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
