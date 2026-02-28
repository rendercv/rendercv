from typing import Literal

import pydantic_extra_types.color as pydantic_color

import rendercv.themes.options as o


class Colors(o.Colors):
    name: pydantic_color.Color = "rgb(0,0,0)"
    connections: pydantic_color.Color = "rgb(0,0,0)"
    section_titles: pydantic_color.Color = "rgb(0,0,0)"


class Header(o.Header):
    name_font_family: o.FontFamily = "New Computer Modern"
    connections_font_family: o.FontFamily = "New Computer Modern"


class Links(o.Links):
    underline: bool = True
    use_external_link_icon: bool = False


class Text(o.Text):
    font_family: o.FontFamily = "New Computer Modern"


class SectionTitles(o.SectionTitles):
    font_family: o.FontFamily = "New Computer Modern"
    type: o.SectionTitleType = "with-full-line"


class Highlights(o.Highlights):
    bullet: o.BulletPoint = "◦"


class EducationEntryOptions(o.EducationEntryOptions):
    main_column_first_row_template: str = (
        "**INSTITUTION**\n*DEGREE in AREA*"
    )
    degree_column_template: str | None = None
    date_and_location_column_template: str = "*LOCATION*\n*DATE*"


class NormalEntryOptions(o.NormalEntryOptions):
    date_and_location_column_template: str = "*LOCATION*\n*DATE*"


class ExperienceEntryOptions(o.ExperienceEntryOptions):
    main_column_first_row_template: str = "**POSITION**\n*COMPANY*"
    date_and_location_column_template: str = "*LOCATION*\n*DATE*"


class EntryOptionsTypes(o.EntryTypes):
    education_entry: EducationEntryOptions = EducationEntryOptions()
    normal_entry: NormalEntryOptions = NormalEntryOptions()
    experience_entry: ExperienceEntryOptions = ExperienceEntryOptions()


class Sb2novThemeOptions(o.ThemeOptions):
    theme: Literal["sb2nov"] = "sb2nov"
    header: Header = Header()
    links: Links = Links()
    text: Text = Text()
    colors: Colors = Colors()
    highlights: Highlights = Highlights()
    entry_types: EntryOptionsTypes = EntryOptionsTypes()
    section_titles: SectionTitles = SectionTitles()
