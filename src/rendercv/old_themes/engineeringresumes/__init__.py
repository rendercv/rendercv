from typing import Literal

import pydantic_extra_types.color as pydantic_color

import rendercv.old_themes.options as o


class Page(o.Page):
    show_page_numbering: bool = False


class Header(o.Header):
    name_font_family: o.FontFamily = "XCharter"
    name_font_size: o.TypstDimension = "25pt"
    name_bold: bool = False
    separator_between_connections: str = "|"
    use_icons_for_connections: bool = False
    use_urls_as_placeholders_for_connections: bool = True
    connections_font_family: o.FontFamily = "XCharter"


class Colors(o.Colors):
    name: pydantic_color.Color = pydantic_color.Color("rgb(0,0,0)")
    connections: pydantic_color.Color = pydantic_color.Color("rgb(0,0,0)")
    section_titles: pydantic_color.Color = pydantic_color.Color("rgb(0,0,0)")
    links: pydantic_color.Color = pydantic_color.Color("rgb(0,0,0)")


class Links(o.Links):
    underline: bool = True
    use_external_link_icon: bool = False


class Text(o.Text):
    font_family: o.FontFamily = "XCharter"
    leading: o.TypstDimension = "0.6em"


class SectionTitles(o.SectionTitles):
    font_family: o.FontFamily = "XCharter"
    type: o.SectionTitleType = "with-full-line"
    vertical_space_above: o.TypstDimension = "0.55cm"
    vertical_space_below: o.TypstDimension = "0.3cm"
    font_size: o.TypstDimension = "1.2em"


class Entries(o.Entries):
    vertical_space_between_entries: o.TypstDimension = "0.4cm"
    left_and_right_margin: o.TypstDimension = "0cm"


class Highlights(o.Highlights):
    left_margin: o.TypstDimension = "0cm"
    top_margin: o.TypstDimension = "0.25cm"
    horizontal_space_between_bullet_and_highlight: o.TypstDimension = "0.3em"
    vertical_space_between_highlights: o.TypstDimension = "0.19cm"


class EducationEntryOptions(o.EducationEntryOptions):
    main_column_first_row_template: str = "**INSTITUTION**, DEGREE in AREA -- LOCATION"
    degree_column_template: str | None = None
    date_and_location_column_template: str = "DATE"


class NormalEntryOptions(o.NormalEntryOptions):
    main_column_first_row_template: str = "**NAME** -- **LOCATION**"
    date_and_location_column_template: str = "DATE"


class ExperienceEntryOptions(o.ExperienceEntryOptions):
    main_column_first_row_template: str = "**POSITION**, COMPANY -- LOCATION"
    date_and_location_column_template: str = "DATE"


class EntryOptionsTypes(o.EntryTypes):
    education_entry: EducationEntryOptions = EducationEntryOptions()
    normal_entry: NormalEntryOptions = NormalEntryOptions()
    experience_entry: ExperienceEntryOptions = ExperienceEntryOptions()


class EngineeringresumesThemeOptions(o.ThemeOptions):
    theme: Literal["engineeringresumes"] = "engineeringresumes"
    page: Page = Page()
    header: Header = Header()
    highlights: Highlights = Highlights()
    text: Text = Text()
    colors: Colors = Colors()
    links: Links = Links()
    entries: Entries = Entries()
    entry_types: EntryOptionsTypes = EntryOptionsTypes()
    section_titles: SectionTitles = SectionTitles()
