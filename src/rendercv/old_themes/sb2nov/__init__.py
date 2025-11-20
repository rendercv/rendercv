from typing import Literal

import pydantic
import pydantic_extra_types.color as pydantic_color

import rendercv.themes.options as o


class Colors(o.Colors):
    name: pydantic_color.Color = pydantic.Field(
        default=pydantic_color.Color("rgb(0,0,0)"),
        description=o.color_common_description,
        examples=o.color_common_examples,
    )
    connections: pydantic_color.Color = pydantic.Field(
        default=pydantic_color.Color("rgb(0,0,0)"),
    )
    section_titles: pydantic_color.Color = pydantic.Field(
        default=pydantic_color.Color("rgb(0,0,0)"),
        description=o.color_common_description,
        examples=o.color_common_examples,
    )


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
    main_column_first_row_template: str = pydantic.Field(
        default="**INSTITUTION**\n*DEGREE in AREA*",
        description=o.template_common_description,
    )
    degree_column_template: str | None = pydantic.Field(
        default=None,
        description=o.template_common_description,
    )
    date_and_location_column_template: str = pydantic.Field(
        default="*LOCATION*\n*DATE*",
        description=o.template_common_description,
    )


class NormalEntryOptions(o.NormalEntryOptions):
    date_and_location_column_template: str = pydantic.Field(
        default="*LOCATION*\n*DATE*",
        description=o.template_common_description,
    )


class ExperienceEntryOptions(o.ExperienceEntryOptions):
    main_column_first_row_template: str = pydantic.Field(
        default="**POSITION**\n*COMPANY*",
        description=o.template_common_description,
    )
    date_and_location_column_template: str = pydantic.Field(
        default="*LOCATION*\n*DATE*",
        description=o.template_common_description,
    )


class EntryOptionsTypes(o.EntryTypes):
    education_entry: EducationEntryOptions = pydantic.Field(
        default_factory=EducationEntryOptions,
    )
    normal_entry: NormalEntryOptions = pydantic.Field(
        default_factory=NormalEntryOptions,
    )
    experience_entry: ExperienceEntryOptions = pydantic.Field(
        default_factory=ExperienceEntryOptions,
    )


class Sb2novThemeOptions(o.ThemeOptions):
    theme: Literal["sb2nov"] = "sb2nov"
    header: Header = pydantic.Field(
        default_factory=Header,
    )
    links: Links = pydantic.Field(
        default_factory=Links,
    )
    text: Text = pydantic.Field(
        default_factory=Text,
    )
    colors: Colors = pydantic.Field(
        default_factory=Colors,
    )
    highlights: Highlights = pydantic.Field(
        default_factory=Highlights,
    )
    entry_types: EntryOptionsTypes = pydantic.Field(
        default_factory=EntryOptionsTypes,
    )
    section_titles: SectionTitles = pydantic.Field(
        default_factory=SectionTitles,
    )
