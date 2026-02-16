from typing import Literal

import pydantic

from rendercv.schema.models.base import BaseModelWithoutExtraKeys
from rendercv.schema.models.design.color import Color
from rendercv.schema.models.design.font_family import FontFamily as FontFamilyType
from rendercv.schema.models.design.typst_dimension import TypstDimension

type Bullet = Literal["●", "•", "◦", "-", "◆", "★", "■", "—", "○"]
type BodyAlignment = Literal["left", "justified", "justified-with-no-hyphenation"]
type Alignment = Literal["left", "center", "right"]
type SectionTitleType = Literal[
    "with_partial_line", "with_full_line", "without_line", "moderncv"
]
type PhoneNumberFormatType = Literal["national", "international", "E164"]
type PageSize = Literal["a4", "a5", "us-letter", "us-executive"]

length_common_description = (
    "It can be specified with units (cm, in, pt, mm, ex, em). For example, `0.1cm`."
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
        description="The font size for the headline. The default value is `10pt`.",
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
        description="Whether to make the headline bold. The default value is `false`.",
    )
    connections: bool = pydantic.Field(
        default=False,
        description="Whether to make connections bold. The default value is `false`.",
    )
    section_titles: bool = pydantic.Field(
        default=True,
        description="Whether to make section titles bold. The default value is `true`.",
    )


class Typography(BaseModelWithoutExtraKeys):
    line_spacing: TypstDimension = pydantic.Field(
        default="0.6em",
        description=(
            "Space between lines of text. Larger values create more vertical space. The"
            " default value is `0.6em`."
        ),
    )
    alignment: Literal["left", "justified", "justified-with-no-hyphenation"] = (
        pydantic.Field(
            default="justified",
            description=(
                "Text alignment. Options: 'left', 'justified' (spreads text across full"
                " width), 'justified-with-no-hyphenation' (justified without word"
                " breaks). The default value is `justified`."
            ),
        )
    )
    date_and_location_column_alignment: Alignment = pydantic.Field(
        default="right",
        description=(
            "Alignment for dates and locations in entries. Options: 'left', 'center',"
            " 'right'. The default value is `right`."
        ),
    )
    font_family: FontFamily | FontFamilyType = pydantic.Field(
        default_factory=FontFamily,
        description=(
            "The font family. You can provide a single font name as a string (applies"
            " to all elements), or a dictionary with keys 'body', 'name', 'headline',"
            " 'connections', and 'section_titles' to customize each element. Any system"
            " font can be used."
        ),
    )
    font_size: FontSize = pydantic.Field(
        default_factory=FontSize,
        description="Font sizes for different elements.",
    )
    small_caps: SmallCaps = pydantic.Field(
        default_factory=SmallCaps,
        description="Small caps styling for different elements.",
    )
    bold: Bold = pydantic.Field(
        default_factory=Bold,
        description="Bold styling for different elements.",
    )

    @pydantic.field_validator(
        "font_family", mode="plain", json_schema_input_type=FontFamily | FontFamilyType
    )
    @classmethod
    def validate_font_family(
        cls, font_family: FontFamily | FontFamilyType
    ) -> FontFamily:
        """Convert string font to FontFamily object with uniform styling.

        Why:
            Users can provide simple string "Latin Modern Roman" for all text,
            or specify per-element fonts via FontFamily dict. Validator accepts
            both, expanding strings to full FontFamily objects.

        Args:
            font_family: String font name or FontFamily object.

        Returns:
            FontFamily object with all fields populated.
        """
        if isinstance(font_family, str):
            return FontFamily(
                body=font_family,
                name=font_family,
                headline=font_family,
                connections=font_family,
                section_titles=font_family,
            )

        return FontFamily.model_validate(font_family)


class Links(BaseModelWithoutExtraKeys):
    underline: bool = pydantic.Field(
        default=False,
        description="Underline hyperlinks. The default value is `false`.",
    )
    show_external_link_icon: bool = pydantic.Field(
        default=False,
        description=(
            "Show an external link icon next to URLs. The default value is `false`."
        ),
    )


class Connections(BaseModelWithoutExtraKeys):
    phone_number_format: PhoneNumberFormatType = pydantic.Field(
        default="national",
        description="Phone number format. The default value is `national`.",
    )
    hyperlink: bool = pydantic.Field(
        default=True,
        description=(
            "Make contact information clickable in the PDF. The default value is"
            " `true`."
        ),
    )
    show_icons: bool = pydantic.Field(
        default=True,
        description=(
            "Show icons next to contact information. The default value is `true`."
        ),
    )
    display_urls_instead_of_usernames: bool = pydantic.Field(
        default=False,
        description=(
            "Display full URLs instead of labels. The default value is `false`."
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
            "Horizontal space between contact items. "
            + length_common_description
            + " The default value is `0.5cm`."
        ),
    )


class Header(BaseModelWithoutExtraKeys):
    alignment: Alignment = pydantic.Field(
        default="center",
        description=(
            "Header alignment. Options: 'left', 'center', 'right'. The default value is"
            " `center`."
        ),
    )
    photo_width: TypstDimension = pydantic.Field(
        default="3.5cm",
        description="Photo width. "
        + length_common_description
        + " The default value is `3.5cm`.",
    )
    photo_position: Literal["left", "right"] = pydantic.Field(
        default="left",
        description="Photo position (left or right). The default value is `left`.",
    )
    photo_space_left: TypstDimension = pydantic.Field(
        default="0.4cm",
        description=(
            "Space to the left of the photo. "
            + length_common_description
            + " The default value is `0.4cm`."
        ),
    )
    photo_space_right: TypstDimension = pydantic.Field(
        default="0.4cm",
        description=(
            "Space to the right of the photo. "
            + length_common_description
            + " The default value is `0.4cm`."
        ),
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
        description="Contact information settings.",
    )


class SectionTitles(BaseModelWithoutExtraKeys):
    type: SectionTitleType = pydantic.Field(
        default="with_partial_line",
        description=(
            "Section title visual style. Use 'with_partial_line' for a line next to the"
            " title, 'with_full_line' for a line across the page, 'without_line' for no"
            " line, or 'moderncv' for the ModernCV style. The default value is"
            " `with_partial_line`."
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
    # page_break_before: list[str] = pydantic.Field(
    #     default=[],
    #     description=(
    #         "Section titles before which a page break should be inserted. The default"
    #         " value is `[]`."
    #     ),
    #     examples=[["Experience"], ["Education"]],
    # )
    show_time_spans_in: list[str] = pydantic.Field(
        default=["experience"],
        description=(
            "Section titles where time spans (e.g., '2 years 3 months') should be"
            " displayed. The default value is `['experience']`."
        ),
        examples=[["Experience"], ["Experience", "Education"]],
    )

    @pydantic.field_validator(
        # "page_break_before",
        "show_time_spans_in",
        mode="after",
    )
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
    summary: Summary = pydantic.Field(
        default_factory=Summary,
        description="Summary text settings.",
    )
    highlights: Highlights = pydantic.Field(
        default_factory=Highlights,
        description="Highlights settings.",
    )


class OneLineEntry(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**LABEL:** DETAILS",
        description=(
            "Template for one-line entries. Available placeholders:\n- `LABEL`: The"
            ' label text (e.g., "Languages", "Citizenship")\n- `DETAILS`: The details'
            ' text (e.g., "English (native), Spanish (fluent)")\n\nYou can also add'
            " arbitrary keys to entries and use them as UPPERCASE placeholders.\n\nThe"
            " default value is `**LABEL:** DETAILS`."
        ),
    )


class EducationEntry(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**INSTITUTION**, AREA\nSUMMARY\nHIGHLIGHTS",
        description=(
            "Template for education entry main column. Available placeholders:\n-"
            " `INSTITUTION`: Institution name\n- `AREA`: Field of study/major\n-"
            " `DEGREE`: Degree type (e.g., BS, PhD)\n- `SUMMARY`: Summary text\n-"
            " `HIGHLIGHTS`: Bullet points list\n- `LOCATION`: Location text\n- `DATE`:"
            " Formatted date or date range\n\nYou can also add arbitrary keys to"
            " entries and use them as UPPERCASE placeholders.\n\nThe default value is"
            " `**INSTITUTION**, AREA\\nSUMMARY\\nHIGHLIGHTS`."
        ),
    )
    degree_column: str | None = pydantic.Field(
        default="**DEGREE**",
        description=(
            "Optional degree column template. If provided, displays degree in separate"
            " column. If `null`, no degree column is shown. Available placeholders:\n-"
            " `INSTITUTION`: Institution name\n- `AREA`: Field of study/major\n-"
            " `DEGREE`: Degree type (e.g., BS, PhD)\n- `SUMMARY`: Summary text\n-"
            " `HIGHLIGHTS`: Bullet points list\n- `LOCATION`: Location text\n- `DATE`:"
            " Formatted date or date range\n\nYou can also add arbitrary keys to"
            " entries and use them as UPPERCASE placeholders.\n\nThe default value is"
            " `**DEGREE**`."
        ),
    )
    date_and_location_column: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=(
            "Template for education entry date/location column. Available"
            " placeholders:\n- `INSTITUTION`: Institution name\n- `AREA`: Field of"
            " study/major\n- `DEGREE`: Degree type (e.g., BS, PhD)\n- `SUMMARY`:"
            " Summary text\n- `HIGHLIGHTS`: Bullet points list\n- `LOCATION`: Location"
            " text\n- `DATE`: Formatted date or date range\n\nYou can also add"
            " arbitrary keys to entries and use them as UPPERCASE placeholders.\n\nThe"
            " default value is `LOCATION\\nDATE`."
        ),
    )


class NormalEntry(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**NAME**\nSUMMARY\nHIGHLIGHTS",
        description=(
            "Template for normal entry main column. Available placeholders:\n- `NAME`:"
            " Entry name/title\n- `SUMMARY`: Summary text\n- `HIGHLIGHTS`: Bullet"
            " points list\n- `LOCATION`: Location text\n- `DATE`: Formatted date or"
            " date range\n\nYou can also add arbitrary keys to entries and use them as"
            " UPPERCASE placeholders.\n\nThe default value is"
            " `**NAME**\\nSUMMARY\\nHIGHLIGHTS`."
        ),
    )
    date_and_location_column: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=(
            "Template for normal entry date/location column. Available placeholders:\n-"
            " `NAME`: Entry name/title\n- `SUMMARY`: Summary text\n- `HIGHLIGHTS`:"
            " Bullet points list\n- `LOCATION`: Location text\n- `DATE`: Formatted date"
            " or date range\n\nYou can also add arbitrary keys to entries and use them"
            " as UPPERCASE placeholders.\n\nThe default value is `LOCATION\\nDATE`."
        ),
    )


class ExperienceEntry(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**COMPANY**, POSITION\nSUMMARY\nHIGHLIGHTS",
        description=(
            "Template for experience entry main column. Available placeholders:\n-"
            " `COMPANY`: Company name\n- `POSITION`: Job title/position\n- `SUMMARY`:"
            " Summary text\n- `HIGHLIGHTS`: Bullet points list\n- `LOCATION`: Location"
            " text\n- `DATE`: Formatted date or date range\n\nYou can also add"
            " arbitrary keys to entries and use them as UPPERCASE placeholders.\n\nThe"
            " default value is `**COMPANY**, POSITION\\nSUMMARY\\nHIGHLIGHTS`."
        ),
    )
    date_and_location_column: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=(
            "Template for experience entry date/location column. Available"
            " placeholders:\n- `COMPANY`: Company name\n- `POSITION`: Job"
            " title/position\n- `SUMMARY`: Summary text\n- `HIGHLIGHTS`: Bullet points"
            " list\n- `LOCATION`: Location text\n- `DATE`: Formatted date or date"
            " range\n\nYou can also add arbitrary keys to entries and use them as"
            " UPPERCASE placeholders.\n\nThe default value is `LOCATION\\nDATE`."
        ),
    )


class PublicationEntry(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**TITLE**\nSUMMARY\nAUTHORS\nURL (JOURNAL)",
        description=(
            "Template for publication entry main column. Available placeholders:\n-"
            " `TITLE`: Publication title\n- `AUTHORS`: List of authors (formatted as"
            " comma-separated string)\n- `SUMMARY`: Summary/abstract text\n- `DOI`:"
            " Digital Object Identifier\n- `URL`: Publication URL (if DOI not"
            " provided)\n- `JOURNAL`: Journal/conference/venue name\n- `DATE`:"
            " Formatted date\n\nYou can also add arbitrary keys to entries and use them"
            " as UPPERCASE placeholders.\n\nThe default value is"
            " `**TITLE**\\nSUMMARY\\nAUTHORS\\nURL (JOURNAL)`."
        ),
    )
    date_and_location_column: str = pydantic.Field(
        default="DATE",
        description=(
            "Template for publication entry date column. Available placeholders:\n-"
            " `TITLE`: Publication title\n- `AUTHORS`: List of authors (formatted as"
            " comma-separated string)\n- `SUMMARY`: Summary/abstract text\n- `DOI`:"
            " Digital Object Identifier\n- `URL`: Publication URL (if DOI not"
            " provided)\n- `JOURNAL`: Journal/conference/venue name\n- `DATE`:"
            " Formatted date\n\nYou can also add arbitrary keys to entries and use them"
            " as UPPERCASE placeholders.\n\nThe default value is `DATE`."
        ),
    )


class Templates(BaseModelWithoutExtraKeys):
    footer: str = pydantic.Field(
        default="*NAME -- PAGE_NUMBER/TOTAL_PAGES*",
        description=(
            "Template for the footer. Available placeholders:\n"
            "- `NAME`: The CV owner's name from `cv.name`\n"
            "- `PAGE_NUMBER`: Current page number\n"
            "- `TOTAL_PAGES`: Total number of pages\n"
            "- `CURRENT_DATE`: Formatted date based on `design.templates.single_date`\n"
            "- `MONTH_NAME`: Full month name (e.g., January)\n"
            "- `MONTH_ABBREVIATION`: Abbreviated month name (e.g., Jan)\n"
            "- `MONTH`: Month number (e.g., 1)\n"
            "- `MONTH_IN_TWO_DIGITS`: Zero-padded month (e.g., 01)\n"
            "- `DAY`: Day of the month (e.g., 5)\n"
            "- `DAY_IN_TWO_DIGITS`: Zero-padded day (e.g., 05)\n"
            "- `YEAR`: Full year (e.g., 2025)\n"
            "- `YEAR_IN_TWO_DIGITS`: Two-digit year (e.g., 25)\n\n"
            "The default value is `*NAME -- PAGE_NUMBER/TOTAL_PAGES*`."
        ),
    )
    top_note: str = pydantic.Field(
        default="*LAST_UPDATED CURRENT_DATE*",
        description=(
            "Template for the top note. Available placeholders:\n- `LAST_UPDATED`:"
            ' Localized "last updated" text from `locale.last_updated`\n-'
            " `CURRENT_DATE`: Formatted date based on `design.templates.single_date`\n-"
            " `NAME`: The CV owner's name from `cv.name`\n- `MONTH_NAME`: Full month"
            " name (e.g., January)\n- `MONTH_ABBREVIATION`: Abbreviated month name"
            " (e.g., Jan)\n- `MONTH`: Month number (e.g., 1)\n- `MONTH_IN_TWO_DIGITS`:"
            " Zero-padded month (e.g., 01)\n- `DAY`: Day of the month (e.g., 5)\n-"
            " `DAY_IN_TWO_DIGITS`: Zero-padded day (e.g., 05)\n- `YEAR`: Full year"
            " (e.g., 2025)\n- `YEAR_IN_TWO_DIGITS`: Two-digit year (e.g., 25)\n\n"
            "The default value is `*LAST_UPDATED CURRENT_DATE*`."
        ),
    )
    single_date: str = pydantic.Field(
        default="MONTH_ABBREVIATION YEAR",
        description=(
            "Template for single dates. Available placeholders:\n"
            "- `MONTH_NAME`: Full month name (e.g., January)\n"
            "- `MONTH_ABBREVIATION`: Abbreviated month name (e.g., Jan)\n"
            "- `MONTH`: Month number (e.g., 1)\n"
            "- `MONTH_IN_TWO_DIGITS`: Zero-padded month (e.g., 01)\n"
            "- `DAY`: Day of the month (e.g., 5)\n"
            "- `DAY_IN_TWO_DIGITS`: Zero-padded day (e.g., 05)\n"
            "- `YEAR`: Full year (e.g., 2025)\n"
            "- `YEAR_IN_TWO_DIGITS`: Two-digit year (e.g., 25)\n\n"
            "The default value is `MONTH_ABBREVIATION YEAR`."
        ),
    )
    date_range: str = pydantic.Field(
        default="START_DATE – END_DATE",
        description=(
            "Template for date ranges. Available placeholders:\n- `START_DATE`:"
            " Formatted start date based on `design.templates.single_date`\n-"
            " `END_DATE`: Formatted end date based on `design.templates.single_date`"
            ' (or "present"/"ongoing" for current positions)\n\nThe default value is'
            " `START_DATE – END_DATE`."
        ),
    )
    time_span: str = pydantic.Field(
        default="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
        description=(
            "Template for time spans (duration calculations). Available"
            " placeholders:\n- `HOW_MANY_YEARS`: Number of years (e.g., 2)\n- `YEARS`:"
            ' Localized word for "years" from `locale.years` (or singular "year")\n-'
            " `HOW_MANY_MONTHS`: Number of months (e.g., 3)\n- `MONTHS`: Localized word"
            ' for "months" from `locale.months` (or singular "month")\n\nThe default'
            " value is `HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS`."
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
