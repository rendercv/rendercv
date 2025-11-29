from typing import Literal

import pydantic

from rendercv.schema.models.base import BaseModelWithoutExtraKeys
from rendercv.schema.models.design.color import Color
from rendercv.schema.models.design.font_family import FontFamily as FontFamilyType
from rendercv.schema.models.design.typst_dimension import TypstDimension

type BulletPoint = Literal["●", "•", "◦", "-", "◆", "★", "■", "—", "○"]
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
        default="0.7in",
        description=length_common_description + " The default value is `2cm`.",
    )
    bottom_margin: TypstDimension = pydantic.Field(
        default="0.7in",
        description=length_common_description + " The default value is `2cm`.",
    )
    left_margin: TypstDimension = pydantic.Field(
        default="0.7in",
        description=length_common_description + " The default value is `2cm`.",
    )
    right_margin: TypstDimension = pydantic.Field(
        default="0.7in",
        description=length_common_description + " The default value is `2cm`.",
    )
    show_footer: bool = pydantic.Field(
        default=True,
        description="Whether to show the footer. The default value is `true`.",
    )
    show_top_note: bool = pydantic.Field(
        default=True,
        description="Whether to show the top note. The default value is `true`.",
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


class FontFamily(BaseModelWithoutExtraKeys):
    body: FontFamilyType = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for body text. The default value is `Source Sans 3`."
        ),
    )
    name: FontFamilyType = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for the name. The default value is `Source Sans 3`."
        ),
    )
    headline: FontFamilyType = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for the headline. The default value is `Source Sans 3`."
        ),
    )
    connections: FontFamilyType = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for connections. The default value is `Source Sans 3`."
        ),
    )
    section_titles: FontFamilyType = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for section titles. The default value is `Source Sans 3`."
        ),
    )


class FontSize(BaseModelWithoutExtraKeys):
    body: TypstDimension = pydantic.Field(
        default="10pt",
        description="The font size for body text. The default value is `10pt`.",
    )
    name: TypstDimension = pydantic.Field(
        default="30pt",
        description="The font size for the name. The default value is `30pt`.",
    )
    headline: TypstDimension = pydantic.Field(
        default="10pt",
        description="The font size for the headline. The default value is `20pt`.",
    )
    connections: TypstDimension = pydantic.Field(
        default="10pt",
        description="The font size for connections. The default value is `10pt`.",
    )
    section_titles: TypstDimension = pydantic.Field(
        default="1.4em",
        description="The font size for section titles. The default value is `1.4em`.",
    )


class SmallCaps(BaseModelWithoutExtraKeys):
    name: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use small caps for the name. The default value is `false`."
        ),
    )
    headline: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use small caps for the headline. The default value is `false`."
        ),
    )
    connections: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use small caps for connections. The default value is `false`."
        ),
    )
    section_titles: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use small caps for section titles. The default value is"
            " `false`."
        ),
    )


class Bold(BaseModelWithoutExtraKeys):
    name: bool = pydantic.Field(
        default=True,
        description="Whether to make the name bold. The default value is `true`.",
    )
    headline: bool = pydantic.Field(
        default=False,
        description="Whether to make the headline bold. The default value is `true`.",
    )
    connections: bool = pydantic.Field(
        default=False,
        description="Whether to make connections bold. The default value is `true`.",
    )
    section_titles: bool = pydantic.Field(
        default=True,
        description="Whether to make section titles bold. The default value is `true`.",
    )


class Typography(BaseModelWithoutExtraKeys):
    line_spacing: TypstDimension = pydantic.Field(
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
    font_family: FontFamily = pydantic.Field(
        default_factory=FontFamily,
        description="Font family settings for different elements.",
    )
    font_size: FontSize = pydantic.Field(
        default_factory=FontSize,
        description="Font size settings for different elements.",
    )
    small_caps: SmallCaps = pydantic.Field(
        default_factory=SmallCaps,
        description="Small caps settings for different elements.",
    )
    bold: Bold = pydantic.Field(
        default_factory=Bold,
        description="Bold settings for different elements.",
    )


class Links(BaseModelWithoutExtraKeys):
    underline: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to underline hyperlinks in your CV. The default value is `false`."
        ),
    )
    show_external_link_icon: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to show an external link icon next to URLs. The default value is"
            " `true`."
        ),
    )


class Connections(BaseModelWithoutExtraKeys):
    phone_number_format: Literal["national", "international", "E164"] = pydantic.Field(
        default="national",
        description="The format for phone numbers. The default value is `national`.",
    )
    hyperlink: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to make contact information clickable links in the PDF. The"
            " default value is `true`."
        ),
    )
    show_icons: bool = pydantic.Field(
        default=True,
        description=(
            "Whether to show icons (phone, email, etc.) next to contact information."
            " The default value is `true`."
        ),
    )
    display_urls_instead_of_usernames: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to display full URLs instead of labels for connections. The"
            " default value is `false`."
        ),
    )
    separator: str = pydantic.Field(
        default="",
        description=(
            "Character(s) to separate contact items (e.g., '|' or '•'). Leave empty for"
            " no separator. The default value is `''`."
        ),
    )
    space_between_connections: TypstDimension = pydantic.Field(
        default="0.5cm",
        description=(
            "Horizontal space between each contact info item (email, phone, etc.). "
        )
        + length_common_description
        + " The default value is `0.5cm`.",
    )


class Header(BaseModelWithoutExtraKeys):
    alignment: Alignment = pydantic.Field(
        default="center",
        description=(
            "Alignment of header content (left, center, or right). The default value is"
            " `center`."
        ),
    )
    photo_width: TypstDimension = pydantic.Field(
        default="3.5cm",
        description="The width of your photo in the header. "
        + length_common_description
        + " The default value is `3.5cm`.",
    )
    space_below_name: TypstDimension = pydantic.Field(
        default="0.7cm",
        description="Space below your name. "
        + length_common_description
        + " The default value is `0.7cm`.",
    )
    space_below_headline: TypstDimension = pydantic.Field(
        default="0.7cm",
        description="Space below the headline. "
        + length_common_description
        + " The default value is `0.7cm`.",
    )
    space_below_connections: TypstDimension = pydantic.Field(
        default="0.7cm",
        description="Space below contact information. "
        + length_common_description
        + " The default value is `0.7cm`.",
    )
    connections: Connections = pydantic.Field(
        default_factory=Connections,
        description="Settings for contact information in the header.",
    )


class SectionTitles(BaseModelWithoutExtraKeys):
    type: Literal["with_partial_line", "with_full_line", "without_line", "moderncv"] = (
        pydantic.Field(
            default="with_partial_line",
            description=(
                "The visual style of section titles. 'with_partial_line' shows a line"
                " next to the title, 'with_full_line' extends the line across the page,"
                " 'without_line' shows no line, 'moderncv' uses the ModernCV style. The"
                " default value is `with_partial_line`."
            ),
        )
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
            "Whether to allow page breaks within sections. If false, each section will"
            " start on a new page if it doesn't fit. The default value is `true`."
        ),
    )
    space_between_regular_entries: TypstDimension = pydantic.Field(
        default="1.2em",
        description=(
            "Vertical space between separate entries in a section. "
            + length_common_description
            + " The default value is `1.2em`."
        ),
    )
    space_between_text_based_entries: TypstDimension = pydantic.Field(
        default="0.3em",
        description=(
            "Vertical space between separate text entries in a section. "
            + length_common_description
            + " The default value is `0.3em`."
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


class Summary(BaseModelWithoutExtraKeys):
    space_above: TypstDimension = pydantic.Field(
        default="0cm",
        description=(
            "Space above the summary text. "
            + length_common_description
            + " The default value is `0cm`."
        ),
    )
    space_left: TypstDimension = pydantic.Field(
        default="0cm",
        description=(
            "Left margin for the summary text (appears before highlights). "
            + length_common_description
            + " The default value is `0cm`."
        ),
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
        default="•",
        description=(
            "The bullet character for nested (sub-level) highlights. The default value"
            " is `-`."
        ),
    )
    space_left: TypstDimension = pydantic.Field(
        default="0.15cm",
        description=(
            "Left indentation for highlights. "
            + length_common_description
            + " The default value is `0.4cm`."
        ),
    )
    space_above: TypstDimension = pydantic.Field(
        default="0cm",
        description=(
            "Space above the highlights section. "
            + length_common_description
            + " The default value is `0.25cm`."
        ),
    )
    space_between_items: TypstDimension = pydantic.Field(
        default="0cm",
        description=(
            "Vertical space between each highlight bullet point. "
            + length_common_description
            + " The default value is `0.25cm`."
        ),
    )
    space_between_bullet_and_text: TypstDimension = pydantic.Field(
        default="0.5em",
        description=(
            "Space between the bullet point and the highlight text. "
            + length_common_description
            + " The default value is `0.5em`."
        ),
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
    side_space: TypstDimension = pydantic.Field(
        default="0.2cm",
        description=(
            "Left and right margins for entry content. "
            + length_common_description
            + " The default value is `0.2cm`."
        ),
    )
    space_between_columns: TypstDimension = pydantic.Field(
        default="0.1cm",
        description=(
            "Space between the main content column and the date/location column. "
            + length_common_description
            + " The default value is `0.1cm`."
        ),
    )
    allow_page_break: bool = pydantic.Field(
        default=False,
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
            " of the date/location column. The default value is `false`."
        ),
    )
    summary: Summary = pydantic.Field(
        default_factory=Summary,
        description="Settings for entry summary text.",
    )
    highlights: Highlights = pydantic.Field(
        default_factory=Highlights,
        description="Settings for entry highlights/bullet points.",
    )


template_common_description = (
    "The content of the template. The available placeholders are all the keys used in"
    " the entries in uppercase. For example, **TITLE**."
)


class OneLineEntry(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**LABEL:** DETAILS",
        description=template_common_description
        + " The default value is `**LABEL:** DETAILS`.",
    )


class EducationEntry(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**INSTITUTION**, AREA\nSUMMARY\nHIGHLIGHTS",
        description=template_common_description
        + " The default value is `**INSTITUTION**, AREA\\nSUMMARY\\nHIGHLIGHTS`.",
    )
    degree_column: str | None = pydantic.Field(
        default="**DEGREE**",
        description=(
            'If given, a degree column will be added to the education entry. If "null",'
            " no degree column will be shown. The available placeholders are all the"
            " keys used in the entries (in uppercase). The default value is"
            " `**DEGREE**`."
        ),
    )
    date_and_location_column: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=template_common_description
        + " The default value is `LOCATION\\nDATE`.",
    )


class NormalEntry(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**NAME**\nSUMMARY\nHIGHLIGHTS",
        description=template_common_description
        + " The default value is `**NAME**\\nSUMMARY\\nHIGHLIGHTS`.",
    )
    date_and_location_column: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=template_common_description
        + " The default value is `LOCATION\\nDATE`.",
    )


class ExperienceEntry(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**COMPANY**, POSITION\nSUMMARY\nHIGHLIGHTS",
        description=template_common_description
        + " The default value is `**COMPANY**, POSITION\\nSUMMARY\\nHIGHLIGHTS`.",
    )
    date_and_location_column: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=template_common_description
        + " The default value is `LOCATION\\nDATE`.",
    )


class PublicationEntry(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**TITLE**\nAUTHORS\nURL (JOURNAL)",
        description=template_common_description
        + " The default value is `**TITLE**\\nAUTHORS\\nURL (JOURNAL)`.",
    )
    date_and_location_column: str = pydantic.Field(
        default="DATE",
        description=template_common_description + " The default value is `DATE`.",
    )


class Templates(BaseModelWithoutExtraKeys):
    footer: str = pydantic.Field(
        default="*NAME -- PAGE_NUMBER/TOTAL_PAGES*",
        description=(
            "Template for the footer. Available placeholders: NAME, PAGE_NUMBER,"
            " TOTAL_PAGES. The default value is `*NAME -- PAGE_NUMBER/TOTAL_PAGES*`."
        ),
    )
    top_note: str = pydantic.Field(
        default="*LAST_UPDATED CURRENT_DATE*",
        description=(
            "Template for the top note. Available placeholders: LAST_UPDATED,"
            " CURRENT_DATE. The default value is `*LAST_UPDATED CURRENT_DATE*`."
        ),
    )
    single_date: str = pydantic.Field(
        default="MONTH_ABBREVIATION YEAR",
        description=(
            "Template for single dates. Available placeholders: MONTH_ABBREVIATION,"
            " YEAR. The default value is `MONTH_ABBREVIATION YEAR`."
        ),
    )
    date_range: str = pydantic.Field(
        default="START_DATE – END_DATE",
        description=(
            "Template for date ranges. Available placeholders: START_DATE, END_DATE."
            " The default value is `START_DATE – END_DATE`."
        ),
    )
    time_span: str = pydantic.Field(
        default="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
        description=(
            "Template for time spans. Available placeholders: HOW_MANY_YEARS, YEARS,"
            " HOW_MANY_MONTHS, MONTHS. The default value is `HOW_MANY_YEARS YEARS"
            " HOW_MANY_MONTHS MONTHS`."
        ),
    )
    one_line_entry: OneLineEntry = pydantic.Field(
        default_factory=OneLineEntry,
        description="Template for one-line entries.",
    )
    education_entry: EducationEntry = pydantic.Field(
        default_factory=EducationEntry,
        description="Template for education entries.",
    )
    normal_entry: NormalEntry = pydantic.Field(
        default_factory=NormalEntry,
        description="Template for normal entries.",
    )
    experience_entry: ExperienceEntry = pydantic.Field(
        default_factory=ExperienceEntry,
        description="Template for experience entries.",
    )
    publication_entry: PublicationEntry = pydantic.Field(
        default_factory=PublicationEntry,
        description="Template for publication entries.",
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
