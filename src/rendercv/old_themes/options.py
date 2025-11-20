"""
The `rendercv.themes.options` module contains the standard data models for the Typst
themes' design options. To avoid code duplication, the themes are encouraged to inherit
from these data models.
"""

import pathlib
import re
from typing import Annotated, Literal

import pydantic
import pydantic_extra_types.color as pydantic_color

from ..data.models.base import RenderCVBaseModelWithoutExtraKeys


# Custom field types:
def validate_typst_dimension(dimension: str) -> str:
    """Check if the input string is a valid dimension for the Typst theme.

    Args:
        dimension: The input string to be validated.

    Returns:
        The input string itself if it is a valid dimension.
    """
    if not re.fullmatch(r"\d+\.?\d*(cm|in|pt|mm|ex|em)", dimension):
        message = (
            "The value must be a number followed by a unit (cm, in, pt, mm, ex, em)."
            " For example, 0.1cm."
        )
        raise ValueError(message)
    return dimension


TypstDimension = Annotated[
    str,
    pydantic.AfterValidator(validate_typst_dimension),
]
try:
    import rendercv_fonts

    available_font_families = [
        "Libertinus Serif",
        "New Computer Modern",
        "DejaVu Sans Mono",
        *rendercv_fonts.available_font_families,
        # Common system fonts
        "Arial",
        "Helvetica",
        "Tahoma",
        "Times New Roman",
        "Verdana",
        "Calibri",
        "Georgia",
        "Aptos",
        "Cambria",
        "Inter",
        "Garamond",
        "Montserrat",
        "Candara",
        "Gill Sans",
        "Didot",
        "Playfair Display",
    ]
    if "Font Awesome 6" in available_font_families:
        available_font_families.remove("Font Awesome 6")
    available_font_families = sorted(set(available_font_families))
except ImportError:
    available_font_families = [
        "Libertinus Serif",
        "New Computer Modern",
        "DejaVu Sans Mono",
        "Mukta",
        "Open Sans",
        "Gentium Book Plus",
        "Noto Sans",
        "Lato",
        "Source Sans 3",
        "EB Garamond",
        "Open Sauce Sans",
        "Fontin",
        "Roboto",
        "Ubuntu",
        "Poppins",
        "Raleway",
        "XCharter",
        # Common system fonts
        "Arial",
        "Helvetica",
        "Tahoma",
        "Times New Roman",
        "Verdana",
        "Calibri",
        "Georgia",
        "Aptos",
        "Cambria",
        "Inter",
        "Garamond",
        "Montserrat",
        "Candara",
        "Gill Sans",
        "Didot",
        "Playfair Display",
    ]
    available_font_families = sorted(set[str](available_font_families))
font_family_validator = pydantic.TypeAdapter(
    Literal[tuple[str, ...](available_font_families)]
)


def validate_font_family(font_family: str) -> str:
    """Check if the input string is a valid font family.

    Args:
        font_family: The input string to be validated.

    Returns:
        The input string itself if it is a valid font family.
    """
    if (pathlib.Path("fonts")).exists():
        # Then allow custom font families.
        return font_family

    try:
        font_family_validator.validate_strings(font_family)
    except pydantic.ValidationError as e:
        message = (
            "The font family must be one of the following:"
            f" {', '.join(available_font_families)}."
        )
        raise ValueError(message) from e

    return font_family_validator.validate_strings(font_family)


FontFamily = Annotated[
    str,
    pydantic.PlainValidator(
        validate_font_family,
        json_schema_input_type=Literal[tuple[str, ...](available_font_families)],
    ),
]
BulletPoint = Literal["•", "◦", "-", "◆", "★", "■", "—", "○"]
PageSize = Literal[
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
]
Alignment = Literal["left", "center", "right"]
TextAlignment = Literal["left", "justified", "justified-with-no-hyphenation"]
SectionTitleType = Literal[
    "with-partial-line", "with-full-line", "without-line", "moderncv"
]

length_common_description = (
    "It can be specified with units (cm, in, pt, mm, ex, em). For example, 0.1cm."
)


class Page(RenderCVBaseModelWithoutExtraKeys):
    size: PageSize = "us-letter"
    top_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=length_common_description,
    )
    bottom_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=length_common_description,
    )
    left_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=length_common_description,
    )
    right_margin: TypstDimension = pydantic.Field(
        default="2cm",
        description=length_common_description,
    )
    show_page_numbering: bool = True
    show_last_updated_date: bool = True


color_common_description = (
    "The color can be specified either with their name"
    " (https://www.w3.org/TR/SVG11/types.html#ColorKeywords), hexadecimal value, RGB"
    " value, or HSL value."
)
color_common_examples = ["Black", "7fffd4", "rgb(0,79,144)", "hsl(270, 60%, 70%)"]


class Colors(RenderCVBaseModelWithoutExtraKeys):
    text: pydantic_color.Color = pydantic.Field(
        default=pydantic_color.Color("rgb(0,0,0)"),
        description=color_common_description,
        examples=color_common_examples,
    )
    name: pydantic_color.Color = pydantic.Field(
        default=pydantic_color.Color("rgb(0,79,144)"),
        description=color_common_description,
        examples=color_common_examples,
    )
    connections: pydantic_color.Color = pydantic.Field(
        default=pydantic_color.Color("rgb(0,79,144)"),
        description=color_common_description,
        examples=color_common_examples,
    )
    section_titles: pydantic_color.Color = pydantic.Field(
        default=pydantic_color.Color("rgb(0,79,144)"),
        description=color_common_description,
        examples=color_common_examples,
    )
    links: pydantic_color.Color = pydantic.Field(
        default=pydantic_color.Color("rgb(0,79,144)"),
        description=color_common_description,
        examples=color_common_examples,
    )
    last_updated_date_and_page_numbering: pydantic_color.Color = pydantic.Field(
        default=pydantic_color.Color("rgb(128,128,128)"),
        description=color_common_description,
        examples=color_common_examples,
    )

    @pydantic.field_serializer(
        "text",
        "name",
        "connections",
        "section_titles",
        "links",
        "last_updated_date_and_page_numbering",
    )
    def serialize_color(self, value: pydantic_color.Color) -> str:
        return value.as_rgb()


class Text(RenderCVBaseModelWithoutExtraKeys):
    font_family: FontFamily = "Source Sans 3"
    font_size: TypstDimension = "10pt"
    leading: TypstDimension = pydantic.Field(
        default="0.6em",
        description="The vertical space between adjacent lines of text.",
    )
    alignment: TextAlignment = pydantic.Field(default="justified")
    date_and_location_column_alignment: Alignment = pydantic.Field(default="right")


class Links(RenderCVBaseModelWithoutExtraKeys):
    underline: bool = False
    use_external_link_icon: bool = True


class Header(RenderCVBaseModelWithoutExtraKeys):
    name_font_family: FontFamily = "Source Sans 3"
    name_font_size: TypstDimension = "30pt"
    name_bold: bool = True
    small_caps_for_name: bool = False
    photo_width: TypstDimension = "3.5cm"
    vertical_space_between_name_and_connections: TypstDimension = "0.7cm"
    vertical_space_between_connections_and_first_section: TypstDimension = "0.7cm"
    horizontal_space_between_connections: TypstDimension = "0.5cm"
    connections_font_family: FontFamily = "Source Sans 3"
    separator_between_connections: str = ""
    use_icons_for_connections: bool = True
    use_urls_as_placeholders_for_connections: bool = False
    make_connections_links: bool = True
    alignment: Alignment = "center"


class SectionTitles(RenderCVBaseModelWithoutExtraKeys):
    type: SectionTitleType = "with-partial-line"
    font_family: FontFamily = "Source Sans 3"
    font_size: TypstDimension = "1.4em"
    bold: bool = True
    small_caps: bool = False
    line_thickness: TypstDimension = "0.5pt"
    vertical_space_above: TypstDimension = "0.5cm"
    vertical_space_below: TypstDimension = "0.3cm"


class Entries(RenderCVBaseModelWithoutExtraKeys):
    date_and_location_width: TypstDimension = pydantic.Field(
        default="4.15cm",
        description=length_common_description,
    )
    left_and_right_margin: TypstDimension = pydantic.Field(
        default="0.2cm",
        description=length_common_description,
    )
    horizontal_space_between_columns: TypstDimension = pydantic.Field(
        default="0.1cm",
        description=length_common_description,
    )
    vertical_space_between_entries: TypstDimension = pydantic.Field(
        default="1.2em",
        description=length_common_description,
    )
    allow_page_break_in_sections: bool = True
    allow_page_break_in_entries: bool = True
    short_second_row: bool = pydantic.Field(
        default=False,
        description=(
            'If this option is "true", second row will be shortened to leave the bottom'
            " of the date empty."
        ),
    )
    show_time_spans_in: list[str] = pydantic.Field(
        default_factory=list,
        description=(
            "The list of section titles where the time spans will be shown in the"
            " entries."
        ),
    )


class Highlights(RenderCVBaseModelWithoutExtraKeys):
    bullet: BulletPoint = "•"
    nested_bullet: BulletPoint = "-"
    top_margin: TypstDimension = pydantic.Field(
        default="0.25cm",
        description=length_common_description,
    )
    left_margin: TypstDimension = pydantic.Field(
        default="0.4cm",
        description=length_common_description,
    )
    vertical_space_between_highlights: TypstDimension = pydantic.Field(
        default="0.25cm",
        description=length_common_description,
    )
    horizontal_space_between_bullet_and_highlight: TypstDimension = pydantic.Field(
        default="0.5em",
        description=length_common_description,
    )
    summary_left_margin: TypstDimension = pydantic.Field(
        default="0cm",
        description=length_common_description,
    )


template_common_description = (
    "The content of the template. The available placeholders are all the keys used in"
    " the entries (in uppercase)."
)


class EntryBaseWithDate(RenderCVBaseModelWithoutExtraKeys):
    main_column_second_row_template: str = pydantic.Field(
        default="SUMMARY\nHIGHLIGHTS",
        description=template_common_description,
    )
    date_and_location_column_template: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=template_common_description,
    )


class PublicationEntryOptions(RenderCVBaseModelWithoutExtraKeys):
    main_column_first_row_template: str = pydantic.Field(
        default="**TITLE**",
        description=template_common_description,
    )
    main_column_second_row_template: str = pydantic.Field(
        default="AUTHORS\nURL (JOURNAL)",
        description=template_common_description,
    )
    main_column_second_row_without_journal_template: str = pydantic.Field(
        default="AUTHORS\nURL",
        description=template_common_description,
    )
    main_column_second_row_without_url_template: str = pydantic.Field(
        default="AUTHORS\nJOURNAL",
        description=template_common_description,
    )
    date_and_location_column_template: str = pydantic.Field(
        default="DATE",
        description=template_common_description,
    )


class EducationEntryBase(RenderCVBaseModelWithoutExtraKeys):
    main_column_first_row_template: str = pydantic.Field(
        default="**INSTITUTION**, AREA",
        description=template_common_description,
    )
    degree_column_template: str | None = pydantic.Field(
        default="**DEGREE**",
        description=(
            'If given, a degree column will be added to the education entry. If "null",'
            " no degree column will be shown. The available placeholders are all the"
            " keys used in the entries (in uppercase)."
        ),
    )
    degree_column_width: TypstDimension = pydantic.Field(
        default="1cm",
        description=length_common_description,
    )


class EducationEntryOptions(EntryBaseWithDate, EducationEntryBase):
    pass


class NormalEntryBase(RenderCVBaseModelWithoutExtraKeys):
    main_column_first_row_template: str = pydantic.Field(
        default="**NAME**",
        description=template_common_description,
    )


class NormalEntryOptions(EntryBaseWithDate, NormalEntryBase):
    pass


class ExperienceEntryBase(RenderCVBaseModelWithoutExtraKeys):
    main_column_first_row_template: str = pydantic.Field(
        default="**COMPANY**, POSITION",
        description=template_common_description,
    )


class ExperienceEntryOptions(EntryBaseWithDate, ExperienceEntryBase):
    pass


class OneLineEntryOptions(RenderCVBaseModelWithoutExtraKeys):
    template: str = pydantic.Field(
        default="**LABEL:** DETAILS",
        description=template_common_description,
    )


class EntryTypes(RenderCVBaseModelWithoutExtraKeys):
    one_line_entry: OneLineEntryOptions = pydantic.Field(
        default_factory=OneLineEntryOptions,
    )
    education_entry: EducationEntryOptions = pydantic.Field(
        default_factory=EducationEntryOptions,
    )
    normal_entry: NormalEntryOptions = pydantic.Field(
        default_factory=NormalEntryOptions,
    )
    experience_entry: ExperienceEntryOptions = pydantic.Field(
        default_factory=ExperienceEntryOptions,
    )
    publication_entry: PublicationEntryOptions = pydantic.Field(
        default_factory=PublicationEntryOptions,
    )


class ThemeOptions(RenderCVBaseModelWithoutExtraKeys):
    theme: str
    page: Page = pydantic.Field(
        default_factory=Page,
    )
    colors: Colors = pydantic.Field(
        default_factory=Colors,
    )
    text: Text = pydantic.Field(
        default_factory=Text,
    )
    links: Links = pydantic.Field(
        default_factory=Links,
    )
    header: Header = pydantic.Field(
        default_factory=Header,
    )
    section_titles: SectionTitles = pydantic.Field(
        default_factory=SectionTitles,
    )
    entries: Entries = pydantic.Field(
        default_factory=Entries,
    )
    highlights: Highlights = pydantic.Field(
        default_factory=Highlights,
    )
    entry_types: EntryTypes = pydantic.Field(
        default_factory=EntryTypes,
    )
