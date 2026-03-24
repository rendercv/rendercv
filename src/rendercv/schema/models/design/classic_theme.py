from typing import Literal

import pydantic

from rendercv.schema.models.base import BaseModelWithoutExtraKeys
from rendercv.schema.models.design.color import Color
from rendercv.schema.models.design.header import (
    Header,
    Links,
)
from rendercv.schema.models.design.templates import (
    Templates,
)
from rendercv.schema.models.design.typography import (
    Typography,
)
from rendercv.schema.models.design.typst_dimension import TypstDimension

type Bullet = Literal["●", "•", "◦", "-", "◆", "★", "■", "—", "○"]
type SectionTitleType = Literal[
    "with_partial_line",
    "with_full_line",
    "without_line",
    "moderncv",
    "centered_without_line",
    "centered_with_partial_line",
    "centered_with_centered_partial_line",
    "centered_with_full_line",
]
type PageSize = Literal["a4", "a5", "us-letter", "us-executive"]

length_common_description = (
    "It can be specified with units (cm, in, pt, mm, em). For example, `0.1cm`."
)


class Page(BaseModelWithoutExtraKeys):
    size: PageSize = pydantic.Field(
        default="us-letter",
        description=(
            "The page size. Use 'a4' (international standard) or 'us-letter' (US"
            " standard). The default value is `us-letter`."
        ),
    )
    top_margin: TypstDimension = pydantic.Field(
        default="0.7in",
        description=length_common_description + " The default value is `0.7in`.",
    )
    bottom_margin: TypstDimension = pydantic.Field(
        default="0.7in",
        description=length_common_description + " The default value is `0.7in`.",
    )
    left_margin: TypstDimension = pydantic.Field(
        default="0.7in",
        description=length_common_description + " The default value is `0.7in`.",
    )
    right_margin: TypstDimension = pydantic.Field(
        default="0.7in",
        description=length_common_description + " The default value is `0.7in`.",
    )
    show_footer: bool = pydantic.Field(
        default=True,
        description=(
            "Show the footer at the bottom of pages. The default value is `true`."
        ),
    )
    show_top_note: bool = pydantic.Field(
        default=True,
        description=(
            "Show the top note at the top of the first page. The default value is"
            " `true`."
        ),
    )


color_common_description = (
    "The color can be specified either with their name"
    " (https://www.w3.org/TR/SVG11/types.html#ColorKeywords), hexadecimal value, RGB"
    " value, or HSL value."
)
color_common_examples = ["Black", "7fffd4", "rgb(0,79,144)", "hsl(270, 60%, 70%)"]


class Colors(BaseModelWithoutExtraKeys):
    body: Color = pydantic.Field(
        default=Color("rgb(0, 0, 0)"),
        description=(
            color_common_description + " The default value is `rgb(0, 0, 0)`."
        ),
        examples=color_common_examples,
    )
    name: Color = pydantic.Field(
        default=Color("rgb(0, 79, 144)"),
        description=color_common_description
        + " The default value is `rgb(0, 79, 144)`.",
        examples=color_common_examples,
    )
    headline: Color = pydantic.Field(
        default=Color("rgb(0, 79, 144)"),
        description=color_common_description
        + " The default value is `rgb(0, 79, 144)`.",
        examples=color_common_examples,
    )
    connections: Color = pydantic.Field(
        default=Color("rgb(0, 79, 144)"),
        description=color_common_description
        + " The default value is `rgb(0, 79, 144)`.",
        examples=color_common_examples,
    )
    section_titles: Color = pydantic.Field(
        default=Color("rgb(0, 79, 144)"),
        description=color_common_description
        + " The default value is `rgb(0, 79, 144)`.",
        examples=color_common_examples,
    )
    links: Color = pydantic.Field(
        default=Color("rgb(0, 79, 144)"),
        description=color_common_description
        + " The default value is `rgb(0, 79, 144)`.",
        examples=color_common_examples,
    )
    footer: Color = pydantic.Field(
        default=Color("rgb(128, 128, 128)"),
        description=color_common_description
        + " The default value is `rgb(128, 128, 128)`.",
        examples=color_common_examples,
    )
    top_note: Color = pydantic.Field(
        default=Color("rgb(128, 128, 128)"),
        description=color_common_description
        + " The default value is `rgb(128, 128, 128)`.",
        examples=color_common_examples,
    )


class SectionTitles(BaseModelWithoutExtraKeys):
    type: SectionTitleType = pydantic.Field(
        default="with_partial_line",
        description=(
            "Section title visual style. Use 'with_partial_line' for a line next to the"
            " title, 'with_full_line' for a line across the page, 'without_line' for no"
            " line, 'moderncv' for the ModernCV style, 'centered_without_line' for a"
            " centered title with no line, 'centered_with_partial_line' for a centered"
            " title with baseline partial lines on both sides,"
            " 'centered_with_centered_partial_line' for a centered title with"
            " middle-aligned lines on both sides, or 'centered_with_full_line' for a"
            " full-width line underneath. The default value is `with_partial_line`."
        ),
    )
    line_thickness: TypstDimension = pydantic.Field(
        default="0.5pt",
        description=length_common_description + " The default value is `0.5pt`.",
    )
    space_above: TypstDimension = pydantic.Field(
        default="0.5cm",
        description=length_common_description + " The default value is `0.5cm`.",
    )
    space_below: TypstDimension = pydantic.Field(
        default="0.3cm",
        description=length_common_description + " The default value is `0.3cm`.",
    )


class Sections(BaseModelWithoutExtraKeys):
    allow_page_break: bool = pydantic.Field(
        default=True,
        description=(
            "Allow page breaks within sections. If false, sections that don't fit will"
            " start on a new page. The default value is `true`."
        ),
    )
    space_between_regular_entries: TypstDimension = pydantic.Field(
        default="1.2em",
        description=(
            "Vertical space between entries. "
            + length_common_description
            + " The default value is `1.2em`."
        ),
    )
    space_between_text_based_entries: TypstDimension = pydantic.Field(
        default="0.3em",
        description=(
            "Vertical space between text-based entries. "
            + length_common_description
            + " The default value is `0.3em`."
        ),
    )
    show_time_spans_in: list[str] = pydantic.Field(
        default=["experience"],
        description=(
            "Section titles where time spans (e.g., '2 years 3 months') should be"
            " displayed. The default value is `['experience']`."
        ),
        examples=[["Experience"], ["Experience", "Education"]],
    )

    @pydantic.field_validator("show_time_spans_in", mode="after")
    @classmethod
    def convert_section_titles_to_snake_case(cls, value: list[str]) -> list[str]:
        return [section_title.lower().replace(" ", "_") for section_title in value]


class Summary(BaseModelWithoutExtraKeys):
    space_above: TypstDimension = pydantic.Field(
        default="0cm",
        description=(
            "Space above summary text. "
            + length_common_description
            + " The default value is `0cm`."
        ),
    )
    space_left: TypstDimension = pydantic.Field(
        default="0cm",
        description=(
            "Left margin for summary text. "
            + length_common_description
            + " The default value is `0cm`."
        ),
    )


class Highlights(BaseModelWithoutExtraKeys):
    bullet: Bullet = pydantic.Field(
        default="•",
        description="Bullet character for highlights. The default value is `•`.",
    )
    nested_bullet: Bullet = pydantic.Field(
        default="•",
        description="Bullet character for nested highlights. The default value is `•`.",
    )
    space_left: TypstDimension = pydantic.Field(
        default="0.15cm",
        description=(
            "Left indentation. "
            + length_common_description
            + " The default value is `0.15cm`."
        ),
    )
    space_above: TypstDimension = pydantic.Field(
        default="0cm",
        description=(
            "Space above highlights. "
            + length_common_description
            + " The default value is `0cm`."
        ),
    )
    space_between_items: TypstDimension = pydantic.Field(
        default="0cm",
        description=(
            "Space between highlight items. "
            + length_common_description
            + " The default value is `0cm`."
        ),
    )
    space_between_bullet_and_text: TypstDimension = pydantic.Field(
        default="0.5em",
        description=(
            "Space between bullet and text. "
            + length_common_description
            + " The default value is `0.5em`."
        ),
    )


class Entries(BaseModelWithoutExtraKeys):
    date_and_location_width: TypstDimension = pydantic.Field(
        default="4.15cm",
        description=(
            "Width of the date/location column. "
            + length_common_description
            + " The default value is `4.15cm`."
        ),
    )
    side_space: TypstDimension = pydantic.Field(
        default="0.2cm",
        description=(
            "Left and right margins. "
            + length_common_description
            + " The default value is `0.2cm`."
        ),
    )
    space_between_columns: TypstDimension = pydantic.Field(
        default="0.1cm",
        description=(
            "Space between main content and date/location columns. "
            + length_common_description
            + " The default value is `0.1cm`."
        ),
    )
    allow_page_break: bool = pydantic.Field(
        default=False,
        description=(
            "Allow page breaks within entries. If false, entries that don't fit will"
            " move to a new page. The default value is `false`."
        ),
    )
    short_second_row: bool = pydantic.Field(
        default=True,
        description=(
            "Shorten the second row to align with the date/location column. The default"
            " value is `true`."
        ),
    )
    degree_width: TypstDimension = pydantic.Field(
        default="1cm",
        description=(
            "Width of the degree column. "
            + length_common_description
            + " The default value is `1cm`."
        ),
    )
    summary: Summary = pydantic.Field(
        default_factory=Summary,
        description="Summary text settings.",
    )
    highlights: Highlights = pydantic.Field(
        default_factory=Highlights,
        description="Highlights settings.",
    )


class ClassicTheme(BaseModelWithoutExtraKeys):
    theme: Literal["classic"] = "classic"
    page: Page = pydantic.Field(default_factory=Page)
    colors: Colors = pydantic.Field(default_factory=Colors)
    typography: Typography = pydantic.Field(default_factory=Typography)
    links: Links = pydantic.Field(default_factory=Links)
    header: Header = pydantic.Field(default_factory=Header)
    section_titles: SectionTitles = pydantic.Field(default_factory=SectionTitles)
    sections: Sections = pydantic.Field(default_factory=Sections)
    entries: Entries = pydantic.Field(default_factory=Entries)
    templates: Templates = pydantic.Field(default_factory=Templates)
