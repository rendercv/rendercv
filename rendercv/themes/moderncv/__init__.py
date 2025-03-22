from typing import Literal, Optional

import rendercv.themes.options as o

o.header_name_font_family_field_info.default = "Fontin"
o.header_name_bold_field_info.default = False
o.header_name_font_size_field_info = "25pt"
o.header_alignment_field_info.default = "left"
o.header_connections_font_family_field_info.default = "Fontin"


class Header(o.Header):
    name_font_family: o.FontFamily = o.header_name_font_family_field_info
    name_font_size: o.TypstDimension = o.header_name_font_size_field_info
    name_bold: bool = o.header_name_bold_field_info
    alignment: o.Alignment = o.header_alignment_field_info
    connections_font_family: o.FontFamily = o.header_connections_font_family_field_info


o.links_underline_field_info.default = True
o.links_use_external_link_icon_field_info.default = False


class Links(o.Links):
    underline: bool = o.links_underline_field_info
    use_external_link_icon: bool = o.links_use_external_link_icon_field_info


o.text_font_family_field_info.default = "Fontin"
o.text_leading_field_info.default = "0.6em"


class Text(o.Text):
    font_family: o.FontFamily = o.text_font_family_field_info
    leading: o.TypstDimension = o.text_leading_field_info


o.section_titles_type_field_info.default = "moderncv"
o.section_titles_bold_field_info.default = False
o.section_titles_vertical_space_above_field_info.default = "0.55cm"
o.section_titles_vertical_space_below_field_info.default = "0.3cm"
o.section_titles_font_size_field_info.default = "1.4em"
o.section_titles_line_thickness_field_info.default = "0.15cm"
o.section_titles_font_family_field_info.default = "Fontin"


class SectionTitles(o.SectionTitles):
    font_family: o.FontFamily = o.section_titles_font_family_field_info
    type: o.SectionTitleType = o.section_titles_type_field_info
    vertical_space_above: o.TypstDimension = (
        o.section_titles_vertical_space_above_field_info
    )
    vertical_space_below: o.TypstDimension = (
        o.section_titles_vertical_space_below_field_info
    )
    font_size: o.TypstDimension = o.section_titles_font_size_field_info
    bold: bool = o.section_titles_bold_field_info
    line_thickness: o.TypstDimension = o.section_titles_line_thickness_field_info


o.entries_vertical_space_between_entries_field_info.default = "0.4cm"
o.entries_left_and_right_margin_field_info.default = "0cm"
o.entries_horizontal_space_between_columns_field_info.default = "0.4cm"


class Entries(o.Entries):
    vertical_space_between_entries: o.TypstDimension = (
        o.entries_vertical_space_between_entries_field_info
    )
    left_and_right_margin: o.TypstDimension = o.entries_left_and_right_margin_field_info
    horizontal_space_between_columns: o.TypstDimension = (
        o.entries_horizontal_space_between_columns_field_info
    )


o.highlights_left_margin_field_info.default = "0cm"
o.highlights_top_margin_field_info.default = "0.25cm"
o.highlights_vertical_space_between_highlights_field_info.default = "0.19cm"
o.highlights_horizontal_space_between_bullet_and_highlight_field_info.default = "0.3em"


class Highlights(o.Highlights):
    left_margin: o.TypstDimension = o.highlights_left_margin_field_info
    top_margin: o.TypstDimension = o.highlights_top_margin_field_info
    horizontal_space_between_bullet_and_highlight: o.TypstDimension = (
        o.highlights_horizontal_space_between_bullet_and_highlight_field_info
    )
    vertical_space_between_highlights: o.TypstDimension = (
        o.highlights_vertical_space_between_highlights_field_info
    )


o.education_entry_main_column_first_row_template_field_info.default = (
    "**INSTITUTION**, DEGREE in AREA -- LOCATION"
)
o.education_entry_degree_column_template_field_info.default = None
o.entry_base_with_date_date_and_location_column_template_field_info.default = "DATE"


class EducationEntryOptions(o.EducationEntryOptions):
    main_column_first_row_template: str = (
        o.education_entry_main_column_first_row_template_field_info
    )
    degree_column_template: Optional[str] = (
        o.education_entry_degree_column_template_field_info
    )
    date_and_location_column_template: str = (
        o.entry_base_with_date_date_and_location_column_template_field_info
    )


o.normal_entry_main_column_first_row_template_field_info.default = (
    "**NAME** -- **LOCATION**"
)


class NormalEntryOptions(o.NormalEntryOptions):
    main_column_first_row_template: str = (
        o.normal_entry_main_column_first_row_template_field_info
    )
    date_and_location_column_template: str = (
        o.entry_base_with_date_date_and_location_column_template_field_info
    )


o.experience_entry_main_column_first_row_template_field_info.default = (
    "**POSITION**, COMPANY -- LOCATION"
)


class ExperienceEntryOptions(o.ExperienceEntryOptions):
    main_column_first_row_template: str = (
        o.experience_entry_main_column_first_row_template_field_info
    )
    date_and_location_column_template: str = (
        o.entry_base_with_date_date_and_location_column_template_field_info
    )


o.entry_types_education_entry_field_info.default = EducationEntryOptions()
o.entry_types_normal_entry_field_info.default = NormalEntryOptions()
o.entry_types_experience_entry_field_info.default = ExperienceEntryOptions()


class EntryOptionsTypes(o.EntryTypes):
    education_entry: EducationEntryOptions = o.entry_types_education_entry_field_info
    normal_entry: NormalEntryOptions = o.entry_types_normal_entry_field_info
    experience_entry: ExperienceEntryOptions = o.entry_types_experience_entry_field_info


o.theme_options_theme_field_info.default = "moderncv"
o.theme_options_header_field_info.default = Header()
o.theme_options_text_field_info.default = Text()
o.theme_options_entry_types_field_info.default = EntryOptionsTypes()
o.theme_options_section_titles_field_info.default = SectionTitles()
o.theme_options_highlights_field_info.default = Highlights()
o.theme_options_links_field_info.default = Links()
o.theme_options_entries_field_info.default = Entries()


class ModerncvThemeOptions(o.ThemeOptions):
    theme: Literal["moderncv"] = o.theme_options_theme_field_info
    header: Header = o.theme_options_header_field_info
    highlights: Highlights = o.theme_options_highlights_field_info
    text: Text = o.theme_options_text_field_info
    links: Links = o.theme_options_links_field_info
    entries: Entries = o.theme_options_entries_field_info
    entry_types: EntryOptionsTypes = o.theme_options_entry_types_field_info
    section_titles: SectionTitles = o.theme_options_section_titles_field_info
