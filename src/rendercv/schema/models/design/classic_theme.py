from typing import Literal

import pydantic

from ..base import BaseModelWithoutExtraKeys
from .primitives.color import Color
from .primitives.font_family import FontFamily
from .primitives.typst_dimension import TypstDimension

type BulletPoint = Literal["•", "◦", "-", "◆", "★", "■", "—", "○"]
type Alignment = Literal["left", "center", "right"]

_length_common_description = (
    "It can be specified with units (cm, in, pt, mm, ex, em). For example, `0.1cm`."
)


class Page(BaseModelWithoutExtraKeys):
    size: Literal[
        "a0",
        "a1",
        "a2",
        "a3",
        "a4",
        "a5",
        "a6",
        "a7",
        "a8",
        "us-letter",
        "us-legal",
        "us-executive",
        "us-gov-letter",
        "us-gov-legal",
        "us-business-card",
        "presentation-16-9",
        "presentation-4-3",
    ] = "us-letter"
    top_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=_length_common_description + " The default value is `2cm`.",
    )
    bottom_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=_length_common_description + " The default value is `2cm`.",
    )
    left_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=_length_common_description + " The default value is `2cm`.",
    )
    right_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=_length_common_description + " The default value is `2cm`.",
    )
    show_page_numbering: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to show the page numbering at the bottom of the page. The default"
            " value is `true`."
        ),
    )
    show_last_updated_date: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to show the last updated date at the top right corner of the page."
            " The default value is `true`."
        ),
    )


color_common_description = (
    "The color can be specified either with their name"
    " (https://www.w3.org/TR/SVG11/types.html#ColorKeywords), hexadecimal value, RGB"
    " value, or HSL value."
)
color_common_examples = ["Black", "7fffd4", "rgb(0,79,144)", "hsl(270, 60%, 70%)"]


class Colors(BaseModelWithoutExtraKeys):
    text: Color = pydantic.Field(
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
    last_updated_date_and_page_numbering: Color = pydantic.Field(
        default=Color("rgb(128, 128, 128)"),
        description=color_common_description
        + " The default value is `rgb(128, 128, 128)`.",
        examples=color_common_examples,
    )


class Text(BaseModelWithoutExtraKeys):
    font_family: FontFamily = pydantic.Field(
        default="Source Sans 3",
        description="The default value is `Source Sans 3`.",
    )
    font_size: TypstDimension = pydantic.Field(
        default="10pt",
        description="The default value is `10pt`.",
    )
    leading: TypstDimension = pydantic.Field(
        default="0.6em",
        description="The default value is `0.6em`.",
    )
    alignment: Literal["left", "justified", "justified-with-no-hyphenation"] = (
        pydantic.Field(
            default="justified",
            description="The default value is `justified`.",
        )
    )
    date_and_location_column_alignment: Alignment = pydantic.Field(
        default="right",
        description="The default value is `right`.",
    )


class Links(BaseModelWithoutExtraKeys):
    underline: bool = pydantic.Field(
        default=False,
        description="The default value is `false`.",
    )
    use_external_link_icon: bool = pydantic.Field(
        default=True,
        description="The default value is `true`.",
    )


class Header(BaseModelWithoutExtraKeys):
    name_font_family: FontFamily = pydantic.Field(
        default="Source Sans 3",
        description="The default value is `Source Sans 3`.",
    )
    name_font_size: TypstDimension = pydantic.Field(
        default="30pt",
        description="The default value is `30pt`.",
    )
    name_bold: bool = pydantic.Field(
        default=True,
        description="Whether to make the name bold. The default value is `true`.",
    )
    small_caps_for_name: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use small caps for the name. The default value is `false`."
        ),
    )
    photo_width: TypstDimension = pydantic.Field(
        default="3.5cm",
        description=_length_common_description + " The default value is `3.5cm`.",
    )
    vertical_space_between_name_and_connections: TypstDimension = pydantic.Field(
        default="0.7cm",
        description=_length_common_description + " The default value is `0.7cm`.",
    )
    vertical_space_between_connections_and_first_section: TypstDimension = (
        pydantic.Field(
            default="0.7cm",
            description=_length_common_description + " The default value is `0.7cm`.",
        )
    )
    horizontal_space_between_connections: TypstDimension = pydantic.Field(
        default="0.5cm",
        description=_length_common_description + " The default value is `0.5cm`.",
    )
    connections_font_family: FontFamily = pydantic.Field(
        default="Source Sans 3",
        description="The default value is `Source Sans 3`.",
    )
    separator_between_connections: str = pydantic.Field(
        default="",
        description="The separator between the connections. The default value is `''`.",
    )
    use_icons_for_connections: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to use icons for the connections. The default value is `True`."
        ),
    )
    use_urls_as_placeholders_for_connections: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use URLs as placeholders for the connections. The default value"
            " is `False`."
        ),
    )
    make_connections_links: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to make the connections links. The default value is `True`."
        ),
    )
    alignment: Alignment = pydantic.Field(
        default="center",
        description="The default value is `center`.",
    )


class SectionTitles(BaseModelWithoutExtraKeys):
    type: Literal["with-partial-line", "with-full-line", "without-line", "moderncv"] = (
        "with-partial-line"
    )
    font_family: FontFamily = pydantic.Field(
        default="Source Sans 3",
        description="The default value is `Source Sans 3`.",
    )
    font_size: TypstDimension = pydantic.Field(
        default="1.4em",
        description="The default value is `1.4em`.",
    )
    bold: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to make the section titles bold. The default value is `true`."
        ),
    )
    small_caps: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use small caps for the section titles. The default value is"
            " `false`."
        ),
    )
    line_thickness: TypstDimension = pydantic.Field(
        default="0.5pt",
        description=_length_common_description + " The default value is `0.5pt`.",
    )
    vertical_space_above: TypstDimension = pydantic.Field(
        default="0.5cm",
        description=_length_common_description + " The default value is `0.5cm`.",
    )
    vertical_space_below: TypstDimension = pydantic.Field(
        default="0.3cm",
        description=_length_common_description + " The default value is `0.3cm`.",
    )


class Entries(BaseModelWithoutExtraKeys):
    date_and_location_width: TypstDimension = pydantic.Field(
        default="4.15cm",
        description=_length_common_description + " The default value is `4.15cm`.",
    )
    left_and_right_margin: TypstDimension = pydantic.Field(
        default="0.2cm",
        description=_length_common_description + " The default value is `0.2cm`.",
    )
    horizontal_space_between_columns: TypstDimension = pydantic.Field(
        default="0.1cm",
        description=_length_common_description + " The default value is `0.1cm`.",
    )
    vertical_space_between_entries: TypstDimension = pydantic.Field(
        default="1.2em",
        description=_length_common_description + " The default value is `1.2em`.",
    )
    allow_page_break_in_sections: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to allow page breaks in sections. The default value is `true`."
        ),
    )
    allow_page_break_in_entries: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to allow page breaks in entries. The default value is `true`."
        ),
    )
    short_second_row: bool = pydantic.Field(
        default=False,
        description=(
            "If this option is `True`, second row will be shortened to leave the bottom"
            " of the date empty. The default value is `False`."
        ),
    )
    show_time_spans_in: list[str] = pydantic.Field(
        default_factory=list,
        description=(
            "The list of section titles where the time spans will be shown in the"
            " entries. The default value is `[]`."
        ),
    )


class Highlights(BaseModelWithoutExtraKeys):
    bullet: BulletPoint = pydantic.Field(
        default="•",
        description="The default value is `•`.",
    )
    nested_bullet: BulletPoint = pydantic.Field(
        default="-",
        description="The default value is `-`.",
    )
    top_margin: TypstDimension = pydantic.Field(
        default="0.25cm",
        description=_length_common_description + " The default value is `0.25cm`.",
    )
    left_margin: TypstDimension = pydantic.Field(
        default="0.4cm",
        description=_length_common_description + " The default value is `0.4cm`.",
    )
    vertical_space_between_highlights: TypstDimension = pydantic.Field(
        default="0.25cm",
        description=_length_common_description + " The default value is `0.25cm`.",
    )
    horizontal_space_between_bullet_and_highlight: TypstDimension = pydantic.Field(
        default="0.5em",
        description=_length_common_description + " The default value is `0.5em`.",
    )
    summary_left_margin: TypstDimension = pydantic.Field(
        default="0cm",
        description=_length_common_description + " The default value is `0cm`.",
    )


template_common_description = (
    "The content of the template. The available placeholders are all the keys used in"
    " the entries in uppercase. For example, **TITLE**."
)


class BaseEntryWithDateOptions(BaseModelWithoutExtraKeys):
    main_column_second_row_template: str = pydantic.Field(
        default="SUMMARY\nHIGHLIGHTS",
        description=template_common_description
        + " The default value is `SUMMARY\nHIGHLIGHTS`.",
    )
    date_and_location_column_template: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=template_common_description
        + " The default value is `LOCATION\nDATE`.",
    )


class PublicationEntryOptions(BaseModelWithoutExtraKeys):
    main_column_first_row_template: str = pydantic.Field(
        default="**TITLE**",
        description=template_common_description + " The default value is `**TITLE**`.",
    )
    main_column_second_row_template: str = pydantic.Field(
        default="AUTHORS\nURL (JOURNAL)",
        description=template_common_description
        + " The default value is `AUTHORS\nURL (JOURNAL)`.",
    )
    main_column_second_row_without_journal_template: str = pydantic.Field(
        default="AUTHORS\nURL",
        description=template_common_description
        + " The default value is `AUTHORS\nURL`.",
    )
    main_column_second_row_without_url_template: str = pydantic.Field(
        default="AUTHORS\nJOURNAL",
        description=template_common_description
        + " The default value is `AUTHORS\nJOURNAL`.",
    )
    date_and_location_column_template: str = pydantic.Field(
        default="DATE",
        description=template_common_description + " The default value is `DATE`.",
    )


class BaseEducationEntryOptions(BaseModelWithoutExtraKeys):
    main_column_first_row_template: str = pydantic.Field(
        default="**INSTITUTION**, AREA",
        description=template_common_description
        + " The default value is `**INSTITUTION**, AREA`.",
    )
    degree_column_template: str | None = pydantic.Field(
        default="**DEGREE**",
        description=(
            'If given, a degree column will be added to the education entry. If "null",'
            " no degree column will be shown. The available placeholders are all the"
            " keys used in the entries (in uppercase). The default value is"
            " `**DEGREE**`."
        ),
    )
    degree_column_width: TypstDimension = pydantic.Field(
        default="1cm",
        description=_length_common_description + " The default value is `1cm`.",
    )


class EducationEntryOptions(BaseEntryWithDateOptions, BaseEducationEntryOptions):
    pass


class BaseNormalEntryOptions(BaseModelWithoutExtraKeys):
    main_column_first_row_template: str = pydantic.Field(
        default="**NAME**",
        description=template_common_description + " The default value is `**NAME**`.",
    )


class NormalEntryOptions(BaseEntryWithDateOptions, BaseNormalEntryOptions):
    pass


class BaseExperienceEntryOptions(BaseModelWithoutExtraKeys):
    main_column_first_row_template: str = pydantic.Field(
        default="**COMPANY**, POSITION",
        description=template_common_description
        + " The default value is `**COMPANY**, POSITION`.",
    )


class ExperienceEntryOptions(BaseEntryWithDateOptions, BaseExperienceEntryOptions):
    pass


class OneLineEntryOptions(BaseModelWithoutExtraKeys):
    template: str = pydantic.Field(
        default="**LABEL:** DETAILS",
        description=template_common_description
        + " The default value is `**LABEL:** DETAILS`.",
    )


class EntryTypes(BaseModelWithoutExtraKeys):
    one_line_entry: OneLineEntryOptions = pydantic.Field(
        default_factory=OneLineEntryOptions
    )
    education_entry: EducationEntryOptions = pydantic.Field(
        default_factory=EducationEntryOptions
    )
    normal_entry: NormalEntryOptions = pydantic.Field(
        default_factory=NormalEntryOptions
    )
    experience_entry: ExperienceEntryOptions = pydantic.Field(
        default_factory=ExperienceEntryOptions
    )
    publication_entry: PublicationEntryOptions = pydantic.Field(
        default_factory=PublicationEntryOptions
    )


class ClassicTheme(BaseModelWithoutExtraKeys):
    theme: Literal["classic"] = "classic"
    page: Page = pydantic.Field(default_factory=Page)
    colors: Colors = pydantic.Field(default_factory=Colors)
    text: Text = pydantic.Field(default_factory=Text)
    links: Links = pydantic.Field(default_factory=Links)
    header: Header = pydantic.Field(default_factory=Header)
    section_titles: SectionTitles = pydantic.Field(default_factory=SectionTitles)
    entries: Entries = pydantic.Field(default_factory=Entries)
    highlights: Highlights = pydantic.Field(default_factory=Highlights)
    entry_types: EntryTypes = pydantic.Field(default_factory=EntryTypes)
