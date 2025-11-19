import datetime

import pydantic

from ..base import BaseModelWithoutExtraKeys
from .render_command import RenderCommand


class Settings(BaseModelWithoutExtraKeys):
    current_date: datetime.date = pydantic.Field(
        default_factory=datetime.date.today,
        title="Date",
        description=(
            'The date RenderCV should treat as "today."It is used for output filenames,'
            ' the "last updated" label, and any calculations that depend on the current'
            " date (such as ongoing time spans). Defaults to the real current date."
        ),
        json_schema_extra={
            "default": None,
        },
    )
    render_command: RenderCommand | None = pydantic.Field(
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

    @pydantic.field_validator("bold_keywords")
    @classmethod
    def keep_unique_keywords(cls, value: list[str]) -> list[str]:
        return list(set(value))
