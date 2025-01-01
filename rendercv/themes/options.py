"""
The `rendercv.themes.common_options_typst_themes` module contains the standard data
models for the Typst themes' design options. To avoid code duplication, the themes
are encouraged to inherit from these data models.
"""

from typing import Annotated, Literal, Optional

import pydantic
import pydantic_extra_types.color as pydantic_color

from ..data.models.base import RenderCVBaseModelWithoutExtraKeys

# Create a custom type called TypstDimension that accepts only strings in a specified
# format.
# This type is used to validate the dimension fields in the design data.
# See https://docs.pydantic.dev/2.5/concepts/types/#custom-types for more information
# about custom types.
TypstDimension = Annotated[
    str,
    pydantic.Field(
        pattern=r"\d+\.?\d*(cm|in|pt|mm|ex|em)",
    ),
]


class Page(RenderCVBaseModelWithoutExtraKeys):
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
    ] = pydantic.Field(
        default="us-letter",
        title="Page Size",
        description='The page size of the CV. The default value is "us-letter".',
    )

    top_margin: TypstDimension = pydantic.Field(
        default="2cm",
        title="Top Margin",
        description=(
            'The top margin of the page with units. The default value is "2cm".'
        ),
    )
    bottom_margin: TypstDimension = pydantic.Field(
        default="2cm",
        title="Bottom Margin",
        description=(
            'The bottom margin of the page with units. The default value is "2cm".'
        ),
    )
    left_margin: TypstDimension = pydantic.Field(
        default="2cm",
        title="Left Margin",
        description=(
            'The left margin of the page with units. The default value is "2cm".'
        ),
    )
    right_margin: TypstDimension = pydantic.Field(
        default="2cm",
        title="Right Margin",
        description=(
            'The right margin of the page with units. The default value is "2cm".'
        ),
    )
    show_page_numbering: bool = pydantic.Field(
        default=True,
        title="Show Page Numbering",
        description=(
            "If this option is set to true, then the page numbering will be shown in"
            ' the footer. The default value is "true".'
        ),
    )
    show_last_updated_date: bool = pydantic.Field(
        default=True,
        title="Show Last Updated Date",
        description=(
            "If this option is set to true, then the last updated date will be shown in"
            ' the top right corner of the CV. The default value is "true".'
        ),
    )


color_common_description = (
    "\nThe color can be specified either with their name"
    " (https://www.w3.org/TR/SVG11/types.html#ColorKeywords), hexadecimal value, RGB"
    " value, or HSL value."
)
color_common_examples = ["Black", "7fffd4", "rgb(0,79,144)", "hsl(270, 60%, 70%)"]


class Colors(RenderCVBaseModelWithoutExtraKeys):
    text: pydantic_color.Color = pydantic.Field(
        default="rgb(0,0,0)",  # type: ignore
        title="Color of Text",
        description=(
            "The color of the text in the CV."
            + color_common_description
            + '\nThe default value is "rgb(0,0,0)".'
        ),
        examples=color_common_examples,
    )
    name: pydantic_color.Color = pydantic.Field(
        default="rgb(0,79,144)",  # type: ignore
        title="Color of Name",
        description=(
            "The color of the name in the header."
            + color_common_description
            + '\nThe default value is "rgb(0,79,144)".'
        ),
        examples=color_common_examples,
    )
    connections: pydantic_color.Color = pydantic.Field(
        default="rgb(0,79,144)",  # type: ignore
        title="Color of Connections",
        description=(
            "The color of the connections in the header."
            + color_common_description
            + '\nThe default value is "rgb(0,79,144)".'
        ),
        examples=color_common_examples,
    )
    section_titles: pydantic_color.Color = pydantic.Field(
        default="rgb(0,79,144)",  # type: ignore
        title="Color of Section Titles",
        description=(
            "The color of the section titles."
            + color_common_description
            + '\nThe default value is "rgb(0,79,144)".'
        ),
        examples=color_common_examples,
    )
    links: pydantic_color.Color = pydantic.Field(
        default="rgb(0,79,144)",  # type: ignore
        title="Color of Links",
        description=(
            "The color of the links."
            + color_common_description
            + '\nThe default value is "rgb(0,79,144)".'
        ),
        examples=color_common_examples,
    )
    last_updated_date_and_page_numbering: pydantic_color.Color = pydantic.Field(
        default="rgb(128,128,128)",  # type: ignore
        title="Color of Last Updated Date and Page Numbering",
        description=(
            "The color of the last updated date and page numbering."
            + color_common_description
            + '\nThe default value is "rgb(128,128,128)".'
        ),
        examples=color_common_examples,
    )


class Text(RenderCVBaseModelWithoutExtraKeys):
    font_family: Literal[
        "Libertinus Serif",
        "New Computer Modern",
        "DejaVu Sans Mono",
        "Source Sans 3",
        "Roboto",
        "Open Sans",
        "Ubuntu",
        "Noto Sans",
        "Mukta",
    ] = pydantic.Field(
        default="Source Sans 3",
        title="Font Family",
        description='The font family of the CV. The default value is "Source Sans 3".',
    )
    font_size: TypstDimension = pydantic.Field(
        default="10pt",
        title="Font Size",
        description='The font size of the CV. The default value is "10pt".',
    )
    leading: TypstDimension = pydantic.Field(
        default="0.6em",
        title="Leading",
        description=(
            "The vertical space between adjacent lines of text. The default value is"
            ' "0.6em".'
        ),
    )
    alignment: Literal["left", "justified", "justified-with-no-hyphenation"] = (
        pydantic.Field(
            default="justified",
            title="Alignment of Text",
            description='The alignment of the text. The default value is "justified".',
        )
    )


class Links(RenderCVBaseModelWithoutExtraKeys):
    underline: bool = pydantic.Field(
        default=False,
        title="Underline Links",
        description=(
            "If this option is set to true, then the links will be underlined. The"
            ' default value is "false".'
        ),
    )
    use_external_link_icon: bool = pydantic.Field(
        default=True,
        title="Use External Link Icon",
        description=(
            "If this option is set to true, then the external link icon will be shown"
            ' next to the links. The default value is "true".'
        ),
    )


class Header(RenderCVBaseModelWithoutExtraKeys):
    name_font_size: TypstDimension = pydantic.Field(
        default="30pt",
        title="Name Font Size",
        description=(
            'The font size of the name in the header. The default value is "30pt".'
        ),
    )
    name_bold: bool = pydantic.Field(
        default=True,
        title="Bold Name",
        description=(
            "If this option is set to true, then the name in the header will be bold."
            ' The default value is "true".'
        ),
    )
    vertical_space_between_name_and_connections: TypstDimension = pydantic.Field(
        default="0.7cm",
        title="Vertical Margin Between the Name and Connections",
        description=(
            "The vertical margin between the name of the person and the connections."
            ' The default value is "0.7cm".'
        ),
    )
    vertical_space_between_connections_and_first_section: TypstDimension = (
        pydantic.Field(
            default="0.7cm",
            title="Vertical Margin Between Connections and First Section",
            description=(
                "The vertical margin between the connections and the first section"
                ' title. The default value is "0.7cm".'
            ),
        )
    )
    horizontal_space_between_connections: TypstDimension = pydantic.Field(
        default="0.5cm",
        title="Space Between Connections",
        description=(
            "The space between the connections (like phone, email, and website). The"
            ' default value is "0.5cm".'
        ),
    )
    separator_between_connections: str = pydantic.Field(
        default="",
        title="Separator Between Connections",
        description=(
            "The separator between the connections in the header. The default value is"
            " an empty string."
        ),
    )
    use_icons_for_connections: bool = pydantic.Field(
        default=True,
        title="Use Icons for Connections",
        description=(
            "If this option is set to true, then icons will be used for the connections"
            " (phone number, email, social networks, etc.) in the header. The default"
            ' value is "true".'
        ),
    )
    alignment: Literal["left", "center", "right"] = pydantic.Field(
        default="center",
        title="Alignment of the Header",
        description='The alignment of the header. The default value is "center".',
    )


class SectionTitles(RenderCVBaseModelWithoutExtraKeys):
    font_size: TypstDimension = pydantic.Field(
        default="1.4em",
        title="Font Size",
        description=(
            'The font size of the section titles. The default value is "1.4em".'
        ),
    )
    bold: bool = pydantic.Field(
        default=True,
        title="Bold Section Titles",
        description=(
            "If this option is set to true, then the section titles will be bold. The"
            ' default value is "true".'
        ),
    )
    line_type: Literal["partial", "full", "none"] = pydantic.Field(
        default="partial",
        title="Line Type",
        description=(
            'The line type of the section titles. The default value is "partial".'
        ),
    )
    line_thickness: TypstDimension = pydantic.Field(
        default="0.5pt",
        title="Line Thickness",
        description=(
            "The thickness of the line under the section titles. The default value is"
            ' "0.5pt".'
        ),
    )
    vertical_space_above: TypstDimension = pydantic.Field(
        default="0.5cm",
        title="Vertical Space Above Section Titles",
        description=(
            'The vertical space above the section titles. The default value is "0.5cm".'
        ),
    )
    vertical_space_below: TypstDimension = pydantic.Field(
        default="0.3cm",
        title="Vertical Space Below Section Titles",
        description=(
            'The vertical space below the section titles. The default value is "0.3cm".'
        ),
    )


class Entries(RenderCVBaseModelWithoutExtraKeys):
    date_and_location_width: TypstDimension = pydantic.Field(
        default="4.15cm",
        title="Width of Date and Location",
        description=(
            "The width of the date and location in the entries. The default value is"
            ' "4.15cm".'
        ),
    )
    left_and_right_margin: TypstDimension = pydantic.Field(
        default="0.2cm",
        title="Left and Right Margin",
        description=(
            'The left and right margin of the entries. The default value is "0.2cm".'
        ),
    )
    horizontal_space_between_columns: TypstDimension = pydantic.Field(
        default="0.1cm",
        title="Horizontal Space Between Columns",
        description=(
            "The horizontal space between the columns in the entries. The default value"
            ' is "0.1cm".'
        ),
    )
    vertical_space_between_entries: TypstDimension = pydantic.Field(
        default="1.2em",
        title="Vertical Space Between Entries",
        description=(
            'The vertical space between the entries. The default value is "1.2em".'
        ),
    )
    allow_page_break_in_entries: bool = pydantic.Field(
        default=True,
        title="Allow Page Break in Entries",
        description=(
            'If this option is set to "true", then a page break will be allowed in the'
            ' entries. The default value is "true".'
        ),
    )
    short_second_row: bool = pydantic.Field(
        default=False,
        title="Short Second Row",
        description=(
            "If this option is enabled, second row will be shortened to leave the"
            " bottom of the date empty."
        ),
    )
    show_time_spans_in: list[str] = pydantic.Field(
        default=[],
        title="Show Time Spans in",
        description=(
            "The list of section titles where the time spans will be shown in the"
            " entries. The default value is an empty list."
        ),
    )


class Highlights(RenderCVBaseModelWithoutExtraKeys):
    bullet: Literal["•", "●", "◦", "-", "◆", "★", "■", "—"] = pydantic.Field(
        default="•",
        title="Bullet",
        description='The bullet used for the highlights. The default value is "•".',
    )
    top_margin: TypstDimension = pydantic.Field(
        default="0.25cm",
        title="Top Margin",
        description='The top margin of the highlights. The default value is "0.25cm".',
    )
    left_margin: TypstDimension = pydantic.Field(
        default="0.4cm",
        title="Left Margin",
        description='The left margin of the highlights. The default value is "0.4cm".',
    )
    vertical_space_between_highlights: TypstDimension = pydantic.Field(
        default="0.25cm",
        title="Vertical Space Between Highlights",
        description=(
            'The vertical space between the highlights. The default value is "0.25cm".'
        ),
    )
    horizontal_space_between_bullet_and_highlight: TypstDimension = pydantic.Field(
        default="0.5em",
        title="Horizontal Space Between Bullet and Highlight",
        description=(
            "The horizontal space between the bullet and the highlight. The default"
            ' value is "0.5em".'
        ),
    )


class EntryBaseWithDate(RenderCVBaseModelWithoutExtraKeys):
    first_column_second_row_template: str = pydantic.Field(
        default="\nSUMMARY\nHIGHLIGHTS",
        title="First Column, Second Row",
        description=(
            "The content of the second row of the first column. The available"
            " placeholders are SUMMARY and HIGHLIGHTS. The default value is"
            ' "\nSUMMARY\nHIGHLIGHTS".'
        ),
    )
    second_column_template: str = pydantic.Field(
        default="LOCATION\nDATE",
        title="Second Column",
        description=(
            "The content of the second column. The available placeholders are"
            ' LOCATION and DATE. The default value is "LOCATION\nDATE".'
        ),
    )


publication_entry_placeholders = (
    "The available placeholders are TITLE, AUTHORS, URL, and JOURNAL"
)


class PublicationEntry(EntryBaseWithDate):
    first_column_first_row_template: str = pydantic.Field(
        default="**TITLE**",
        title="First Column",
        description=(
            f"The content of the first column. {publication_entry_placeholders}. The"
            ' default value is "**TITLE**".'
        ),
    )
    first_column_second_row_template: str = pydantic.Field(
        default="AUTHORS\nURL (JOURNAL)",
        title="First Column, Second Row",
        description=(
            "The content of the second row of the first column."
            f" {publication_entry_placeholders}. The default value is"
            ' "AUTHORS\nURL (JOURNAL)".'
        ),
    )
    first_column_second_row_without_journal_template: str = pydantic.Field(
        default="AUTHORS\nURL",
        title="First Column, Second Row Without Journal",
        description=(
            "The content of the first column in case the `journal` is not given."
            f" {publication_entry_placeholders}. The default value is"
            ' "AUTHORS\nURL".'
        ),
    )
    first_column_second_row_without_url_template: str = pydantic.Field(
        default="AUTHORS\nJOURNAL",
        title="First Column, Second Row Without URL",
        description=(
            "The content of the first column in case the `url` or `doi` is not given."
            f" {publication_entry_placeholders}. The default value is"
            ' "**TITLE**\nAUTHORS\nJOURNAL".'
        ),
    )


class EducationEntryBase(RenderCVBaseModelWithoutExtraKeys):
    first_column_first_row_template: str = pydantic.Field(
        default="**INSTITUTION**, AREA",
        title="First Column, First Row",
        description=(
            "The content of the first column. The available placeholders are"
            ' INSTITUTION and AREA. The default value is "**INSTITUTION**, AREA".'
        ),
    )
    degree_column_template: Optional[str] = pydantic.Field(
        default="**DEGREE**",
        title="Template of the Degree Column",
        description=(
            "If given, a degree column will be added to the education entry. The"
            ' available placeholders are DEGREE. The default value is "**DEGREE**".'
        ),
    )
    degree_column_width: TypstDimension = pydantic.Field(
        default="1cm",
        title="Width of the Degree Column",
        description=(
            "The width of the degree column if the `degree_column_template` is given."
            ' The default value is "1cm".'
        ),
    )


class EducationEntry(EducationEntryBase, EntryBaseWithDate):
    pass


class NormalEntryBase(RenderCVBaseModelWithoutExtraKeys):
    first_column_first_row_template: str = pydantic.Field(
        default="**NAME**",
        title="First Column, First Row",
        description=(
            "The content of the first column. The available placeholders are NAME,"
            ' SUMMARY, and HIGHLIGHTS. The default value is "**NAME**".'
        ),
    )


class NormalEntry(NormalEntryBase, EntryBaseWithDate):
    pass


class ExperienceEntryBase(RenderCVBaseModelWithoutExtraKeys):
    first_column_first_row_template: str = pydantic.Field(
        default="**COMPANY**, POSITION",
        title="First Column, First Row",
        description=(
            "The content of the first column. The available placeholders are"
            ' COMPANY and POSITION. The default value is"**COMPANY**, POSITION".'
        ),
    )


class ExperienceEntry(ExperienceEntryBase, EntryBaseWithDate):
    pass


class OneLineEntry(RenderCVBaseModelWithoutExtraKeys):
    template: str = pydantic.Field(
        default="**LABEL:** DETAILS",
        title="Template",
        description=(
            "The template of the one-line entry. The available placeholders are"
            " LABEL and DETAILS. The default value is \"'**LABEL:** DETAILS'\""
        ),
    )


class EntryTypes(RenderCVBaseModelWithoutExtraKeys):
    one_line_entry: OneLineEntry = pydantic.Field(
        default=OneLineEntry(),
        title="One-Line Entry",
        description="Options related to one-line entries.",
    )
    education_entry: EducationEntry = pydantic.Field(
        default=EducationEntry(),
        title="Education Entry",
        description="Options related to education entries.",
    )
    normal_entry: NormalEntry = pydantic.Field(
        default=NormalEntry(),
        title="Normal Entry",
        description="Options related to normal entries.",
    )
    experience_entry: ExperienceEntry = pydantic.Field(
        default=ExperienceEntry(),
        title="Experience Entry",
        description="Options related to experience entries.",
    )
    publication_entry: PublicationEntry = pydantic.Field(
        default=PublicationEntry(),
        title="Publication Entry",
        description="Options related to publication entries.",
    )


class ThemeOptions(RenderCVBaseModelWithoutExtraKeys):
    theme: Literal["tobeoverwritten"]
    page: Page = pydantic.Field(
        default=Page(),
        title="Page",
        description="Options related to the page.",
    )
    colors: Colors = pydantic.Field(
        default=Colors(),
        title="Colors",
        description="Color used throughout the CV.",
    )
    text: Text = pydantic.Field(
        default=Text(),
        title="Text",
        description="Options related to text.",
    )
    links: Links = pydantic.Field(
        default=Links(),
        title="Links",
        description="Options related to links.",
    )
    header: Header = pydantic.Field(
        default=Header(),
        title="Headers",
        description="Options related to the header.",
    )
    section_titles: SectionTitles = pydantic.Field(
        default=SectionTitles(),
        title="Section Titles",
        description="Options related to the section titles.",
    )
    entries: Entries = pydantic.Field(
        default=Entries(),
        title="Entries",
        description="Options related to the entries.",
    )
    highlights: Highlights = pydantic.Field(
        default=Highlights(),
        title="Highlights",
        description="Options related to the highlights.",
    )
    entry_types: EntryTypes = pydantic.Field(
        default=EntryTypes(),
        title="Templates",
        description="Options related to the templates.",
    )
