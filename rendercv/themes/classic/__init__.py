from typing import Literal

import pydantic

from rendercv.data.models.base import RenderCVBaseModelWithoutExtraKeys
from rendercv.themes.options import (
    ThemeOptions,
    TypstDimension,
)


class ThemeSpecific(RenderCVBaseModelWithoutExtraKeys):
    show_timespan_in: list[str] = pydantic.Field(
        default=[],
        title="Show Time Span in These Sections",
        description=(
            "The time span will be shown in the date and location column in these"
            " sections. The input should be a list of section titles as strings"
            " (case-sensitive). The default value is [] (no section will show the time"
            " span)."
        ),
    )
    education_degree_width: TypstDimension = pydantic.Field(
        default="1cm",
        title="Date and Location Column Width",
        description=(
            "The width of the degree column in EducationEntry. The default value is"
            ' "1cm".'
        ),
    )


class ClassicThemeOptions(ThemeOptions):
    theme: Literal["classic"]
    theme_specific: ThemeSpecific = pydantic.Field(
        default_factory=ThemeSpecific,
        title="Classic Theme Specific Options",
        description="The options specific to the Classic theme.",
    )
