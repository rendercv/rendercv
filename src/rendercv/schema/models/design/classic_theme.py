from typing import Literal

import pydantic

from rendercv.schema.models.base import BaseModelWithoutExtraKeys
from rendercv.schema.models.design.color import Color
from rendercv.schema.models.design.font_family import FontFamily
from rendercv.schema.models.design.typst_dimension import TypstDimension

type BulletPoint = Literal["•", "◦", "-", "◆", "★", "■", "—", "○"]
type Alignment = Literal["left", "center", "right"]

length_common_description = (
    "It can be specified with units (cm, in, pt, mm, ex, em). For example, `0.1cm`."
)


class Page(BaseModelWithoutExtraKeys):
    size: Literal["a4", "a5", "us-letter", "us-executive"] = pydantic.Field(
        default="us-letter",
        description=(
            "The page size of your CV. Common options: 'a4' (international standard),"
            " 'us-letter' (US standard). The default value is `us-letter`."
        ),
    )
    top_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=length_common_description + " The default value is `2cm`.",
    )
    bottom_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=length_common_description + " The default value is `2cm`.",
    )
    left_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=length_common_description + " The default value is `2cm`.",
    )
    right_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=length_common_description + " The default value is `2cm`.",
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
        description=(
            "The font family for body text in your CV. The default value is `Source"
            " Sans 3`."
        ),
    )
    font_size: TypstDimension = pydantic.Field(
        default="10pt",
        description=(
            "The base font size for body text. Affects overall readability. The default"
            " value is `10pt`."
        ),
    )
    leading: TypstDimension = pydantic.Field(
        default="0.6em",
        description=(
            "The line spacing (space between lines of text). Larger values create more"
            " vertical space. The default value is `0.6em`."
        ),
    )
    alignment: Literal["left", "justified", "justified-with-no-hyphenation"] = (
        pydantic.Field(
            default="justified",
            description=(
                "How text is aligned. 'justified' spreads text across the full width,"
                " 'left' aligns to the left edge. The default value is `justified`."
            ),
        )
    )
    date_and_location_column_alignment: Alignment = pydantic.Field(
        default="right",
        description=(
            "Alignment for the date and location column (the right column in entries)."
            " The default value is `right`."
        ),
    )


class Links(BaseModelWithoutExtraKeys):
    underline: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to underline hyperlinks in your CV. The default value is `false`."
        ),
    )
    use_external_link_icon: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to show an external link icon next to URLs. The default value is"
            " `true`."
        ),
    )


class Header(BaseModelWithoutExtraKeys):
    name_font_family: FontFamily = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for your name in the header. The default value is `Source"
            " Sans 3`."
        ),
    )
    name_font_size: TypstDimension = pydantic.Field(
        default="30pt",
        description=(
            "The font size for your name in the header. The default value is `30pt`."
        ),
    )
    name_bold: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to make your name bold in the header. The default value is `true`."
        ),
    )
    small_caps_for_name: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use small caps styling for your name. The default value is"
            " `false`."
        ),
    )
    photo_width: TypstDimension = pydantic.Field(
        default="3.5cm",
        description="The width of your photo in the header. "
        + length_common_description
        + " The default value is `3.5cm`.",
    )
    vertical_space_between_name_and_connections: TypstDimension = pydantic.Field(
        default="0.7cm",
        description="Space between your name and contact information. "
        + length_common_description
        + " The default value is `0.7cm`.",
    )
    vertical_space_between_connections_and_first_section: TypstDimension = (
        pydantic.Field(
            default="0.7cm",
            description="Space between contact information and first CV section. "
            + length_common_description
            + " The default value is `0.7cm`.",
        )
    )
    horizontal_space_between_connections: TypstDimension = pydantic.Field(
        default="0.5cm",
        description=(
            "Horizontal space between each contact info item (email, phone, etc.). "
        )
        + length_common_description
        + " The default value is `0.5cm`.",
    )
    connections_font_family: FontFamily = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for contact information. The default value is `Source"
            " Sans 3`."
        ),
    )
    separator_between_connections: str = pydantic.Field(
        default="",
        description=(
            "Character(s) to separate contact items (e.g., '|' or '•'). Leave empty for"
            " no separator. The default value is `''`."
        ),
    )
    use_icons_for_connections: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to show icons (phone, email, etc.) next to contact information."
            " The default value is `True`."
        ),
    )
    use_urls_as_placeholders_for_connections: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to display full URLs instead of labels for connections. The"
            " default value is `False`."
        ),
    )
    make_connections_links: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to make contact information clickable links in the PDF. The"
            " default value is `True`."
        ),
    )
    alignment: Alignment = pydantic.Field(
        default="center",
        description=(
            "Alignment of header content (left, center, or right). The default value is"
            " `center`."
        ),
    )


class SectionTitles(BaseModelWithoutExtraKeys):
    type: Literal["with-partial-line", "with-full-line", "without-line", "moderncv"] = (
        pydantic.Field(
            default="with-partial-line",
            description=(
                "The visual style of section titles. 'with-partial-line' shows a line"
                " next to the title, 'with-full-line' extends the line across the page,"
                " 'without-line' shows no line, 'moderncv' uses the ModernCV style. The"
                " default value is `with-partial-line`."
            ),
        )
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
        description=length_common_description + " The default value is `0.5pt`.",
    )
    vertical_space_above: TypstDimension = pydantic.Field(
        default="0.5cm",
        description=length_common_description + " The default value is `0.5cm`.",
    )
    vertical_space_below: TypstDimension = pydantic.Field(
        default="0.3cm",
        description=length_common_description + " The default value is `0.3cm`.",
    )


class Entries(BaseModelWithoutExtraKeys):
    date_and_location_width: TypstDimension = pydantic.Field(
        default="4.15cm",
        description=(
            "Width of the right column (for dates and locations). "
            + length_common_description
            + " The default value is `4.15cm`."
        ),
    )
    left_and_right_margin: TypstDimension = pydantic.Field(
        default="0.2cm",
        description=(
            "Left and right margins for entry content. "
            + length_common_description
            + " The default value is `0.2cm`."
        ),
    )
    horizontal_space_between_columns: TypstDimension = pydantic.Field(
        default="0.1cm",
        description=(
            "Space between the main content column and the date/location column. "
            + length_common_description
            + " The default value is `0.1cm`."
        ),
    )
    vertical_space_between_entries: TypstDimension = pydantic.Field(
        default="1.2em",
        description=(
            "Vertical space between separate entries in a section. "
            + length_common_description
            + " The default value is `1.2em`."
        ),
    )
    allow_page_break_in_sections: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to allow page breaks within sections. If false, each section will"
            " start on a new page if it doesn't fit. The default value is `true`."
        ),
    )
    allow_page_break_in_entries: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to allow page breaks within individual entries. If false, each"
            " entry will move to a new page if it doesn't fit. The default value is"
            " `true`."
        ),
    )
    short_second_row: bool = pydantic.Field(
        default=False,
        description=(
            "If true, the second row of entries will be shortened to align with the top"
            " of the date/location column. The default value is `False`."
        ),
    )
    show_time_spans_in: list[str] = pydantic.Field(
        default_factory=list,
        description=(
            "List of section titles where time spans (duration) should be displayed in"
            " entries. For example, ['Experience', 'Education'] will show '2 years 3"
            " months' for applicable entries. The default value is `[]`."
        ),
        examples=[["Experience"], ["Experience", "Education"]],
    )


class Highlights(BaseModelWithoutExtraKeys):
    bullet: BulletPoint = pydantic.Field(
        default="•",
        description=(
            "The bullet character for highlights (your key"
            " achievements/responsibilities). The default value is `•`."
        ),
    )
    nested_bullet: BulletPoint = pydantic.Field(
        default="-",
        description=(
            "The bullet character for nested (sub-level) highlights. The default value"
            " is `-`."
        ),
    )
    top_margin: TypstDimension = pydantic.Field(
        default="0.25cm",
        description=(
            "Space above the highlights section. "
            + length_common_description
            + " The default value is `0.25cm`."
        ),
    )
    left_margin: TypstDimension = pydantic.Field(
        default="0.4cm",
        description=(
            "Left indentation for highlights. "
            + length_common_description
            + " The default value is `0.4cm`."
        ),
    )
    vertical_space_between_highlights: TypstDimension = pydantic.Field(
        default="0.25cm",
        description=(
            "Vertical space between each highlight bullet point. "
            + length_common_description
            + " The default value is `0.25cm`."
        ),
    )
    horizontal_space_between_bullet_and_highlight: TypstDimension = pydantic.Field(
        default="0.5em",
        description=(
            "Space between the bullet point and the highlight text. "
            + length_common_description
            + " The default value is `0.5em`."
        ),
    )
    summary_left_margin: TypstDimension = pydantic.Field(
        default="0cm",
        description=(
            "Left margin for the summary text (appears before highlights). "
            + length_common_description
            + " The default value is `0cm`."
        ),
    )


template_common_description = (
    "The content of the template. The available placeholders are all the keys used in"
    " the entries in uppercase. For example, **TITLE**."
)


class BaseEntryWithDateOptions(BaseModelWithoutExtraKeys):
    date_and_location_column_template: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=template_common_description
        + " The default value is `LOCATION\nDATE`.",
    )


class PublicationEntryOptions(BaseModelWithoutExtraKeys):
    main_column_template: str = pydantic.Field(
        default="**TITLE**\nAUTHORS\nURL (JOURNAL)",
        description=template_common_description + " The default value is `**TITLE**`.",
    )
    date_and_location_column_template: str = pydantic.Field(
        default="DATE",
        description=template_common_description + " The default value is `DATE`.",
    )


class BaseEducationEntryOptions(BaseModelWithoutExtraKeys):
    main_column_template: str = pydantic.Field(
        default="**INSTITUTION**, AREA\nSUMMARY\nHIGHLIGHTS",
        description=template_common_description
        + " The default value is `**INSTITUTION**, AREA\nSUMMARY\nHIGHLIGHTS`.",
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
        description=length_common_description + " The default value is `1cm`.",
    )


class EducationEntryOptions(BaseEntryWithDateOptions, BaseEducationEntryOptions):
    pass


class BaseNormalEntryOptions(BaseModelWithoutExtraKeys):
    main_column_template: str = pydantic.Field(
        default="**NAME**\nSUMMARY\nHIGHLIGHTS",
        description=template_common_description
        + " The default value is `**NAME**\nSUMMARY\nHIGHLIGHTS`.",
    )


class NormalEntryOptions(BaseEntryWithDateOptions, BaseNormalEntryOptions):
    pass


class BaseExperienceEntryOptions(BaseModelWithoutExtraKeys):
    main_column_template: str = pydantic.Field(
        default="**COMPANY**, POSITION\nSUMMARY\nHIGHLIGHTS",
        description=template_common_description
        + " The default value is `**COMPANY**, POSITION\nSUMMARY\nHIGHLIGHTS`.",
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
