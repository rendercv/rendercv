import datetime

import pydantic

from ..base import BaseModelWithoutExtraKeys
from .render_command import RenderCommand


class RenderCVSettings(BaseModelWithoutExtraKeys):
    date: datetime.date = pydantic.Field(
        default_factory=datetime.date.today,
        title="Date",
        description=(
            "The date that will be used everywhere (e.g., in the output file names,"
            " last updated date, computation of time spans for the events that are"
            " currently happening, etc.). The default value is the today's date."
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
