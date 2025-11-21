from typing import Literal

import rendercv.old_themes.options as o


class Header(o.Header):
    name_font_family: o.FontFamily = "Fontin"
    name_font_size: o.TypstDimension = "25pt"
    name_bold: bool = False
    alignment: o.Alignment = "left"
    connections_font_family: o.FontFamily = "Fontin"


class Links(o.Links):
    underline: bool = True
    use_external_link_icon: bool = False


class Text(o.Text):
    font_family: o.FontFamily = "Fontin"
    leading: o.TypstDimension = "0.6em"


class SectionTitles(o.SectionTitles):
    font_family: o.FontFamily = "Fontin"
    type: o.SectionTitleType = "moderncv"
    vertical_space_above: o.TypstDimension = "0.55cm"
    vertical_space_below: o.TypstDimension = "0.3cm"
    font_size: o.TypstDimension = "1.4em"
    bold: bool = False
    line_thickness: o.TypstDimension = "0.15cm"


class Entries(o.Entries):
    vertical_space_between_entries: o.TypstDimension = "0.4cm"
    left_and_right_margin: o.TypstDimension = "0cm"
    horizontal_space_between_columns: o.TypstDimension = "0.4cm"


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


class ModerncvThemeOptions(o.ThemeOptions):
    theme: Literal["moderncv"] = "moderncv"
    header: Header = Header()
    highlights: Highlights = Highlights()
    text: Text = Text()
    links: Links = Links()
    entries: Entries = Entries()
    entry_types: EntryOptionsTypes = EntryOptionsTypes()
    section_titles: SectionTitles = SectionTitles()
