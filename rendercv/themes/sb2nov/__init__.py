from typing import Literal, Optional

import pydantic_extra_types.color as pydantic_color

import rendercv.themes.options as o

o.colors_name_field_info.default = "rgb(0,0,0)"
o.colors_connections_field_info.default = "rgb(0,0,0)"
o.colors_section_titles_field_info.default = "rgb(0,0,0)"


class Colors(o.Colors):
    name: pydantic_color.Color = o.colors_name_field_info
    connections: pydantic_color.Color = o.colors_connections_field_info
    section_titles: pydantic_color.Color = o.colors_section_titles_field_info


o.text_font_family_field_info.default = "New Computer Modern"


class Text(o.Text):
    font_family: o.FontFamily = o.text_font_family_field_info


o.section_titles_type_field_info.default = "with-full-line"


class SectionTitles(o.SectionTitles):
    line_type: o.SectionTitleType = o.section_titles_type_field_info


o.highlights_bullet_field_info.default = "◦"


class Highlights(o.Highlights):
    bullet: o.BulletPoint = o.highlights_bullet_field_info


o.education_entry_main_column_first_row_template_field_info.default = (
    "**INSTITUTION**\n*DEGREE in AREA*"
)
o.education_entry_degree_column_template_field_info.default = None
o.entry_base_with_date_date_and_location_column_template_field_info.default = (
    "*LOCATION*\n*DATE*"
)


class EducationEntry(o.EducationEntry):
    main_column_first_row_template: str = (
        o.education_entry_main_column_first_row_template_field_info
    )
    degree_column_template: Optional[str] = (
        o.education_entry_degree_column_template_field_info
    )
    date_and_location_column_template: str = (
        o.entry_base_with_date_date_and_location_column_template_field_info
    )


class NormalEntry(o.NormalEntry):
    date_and_location_column_template: str = (
        o.entry_base_with_date_date_and_location_column_template_field_info
    )


o.experience_entry_main_column_first_row_template_field_info.default = (
    "**POSITION**\n*COMPANY*"
)


class ExperienceEntry(o.ExperienceEntry):
    main_column_first_row_template: str = (
        o.experience_entry_main_column_first_row_template_field_info
    )
    date_and_location_column_template: str = (
        o.entry_base_with_date_date_and_location_column_template_field_info
    )


o.entry_types_education_entry_field_info.default = EducationEntry()
o.entry_types_normal_entry_field_info.default = NormalEntry()
o.entry_types_experience_entry_field_info.default = ExperienceEntry()


class EntryTypes(o.EntryTypes):
    education_entry: EducationEntry = o.entry_types_education_entry_field_info
    normal_entry: NormalEntry = o.entry_types_normal_entry_field_info
    experience_entry: ExperienceEntry = o.entry_types_experience_entry_field_info


o.theme_options_text_field_info.default = Text()
o.theme_options_colors_field_info.default = Colors()
o.theme_options_highlights_field_info.default = Highlights()
o.theme_options_entry_types_field_info.default = EntryTypes()
o.theme_options_section_titles_field_info.default = SectionTitles()
o.theme_options_theme_field_info.default = "sb2nov"


class Sb2novThemeOptions(o.ThemeOptions):
    theme: Literal["sb2nov"] = o.theme_options_theme_field_info
    text: Text = o.theme_options_text_field_info
    colors: Colors = o.theme_options_colors_field_info
    highlights: Highlights = o.theme_options_highlights_field_info
    entry_types: EntryTypes = o.theme_options_entry_types_field_info
    section_titles: SectionTitles = o.theme_options_section_titles_field_info
