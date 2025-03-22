"""This script generates the example entry figures and creates an environment for
documentation templates using `mkdocs-macros-plugin`. For example, the content of the
example entries found in
"[Structure of the YAML Input File](https://docs.rendercv.com/user_guide/structure_of_the_yaml_input_file/)"
are coming from this script.
"""

import io
import pathlib
from typing import get_args

import pydantic
import ruamel.yaml

import rendercv.data as data
import rendercv.themes.options as theme_options

repository_root = pathlib.Path(__file__).parent.parent
rendercv_path = repository_root / "rendercv"
image_assets_directory = pathlib.Path(__file__).parent / "assets" / "images"


class SampleEntries(pydantic.BaseModel):
    education_entry: data.EducationEntry
    experience_entry: data.ExperienceEntry
    normal_entry: data.NormalEntry
    publication_entry: data.PublicationEntry
    one_line_entry: data.OneLineEntry
    bullet_entry: data.BulletEntry
    numbered_entry: data.NumberedEntry
    reversed_numbered_entry: data.ReversedNumberedEntry
    text_entry: str


def dictionary_to_yaml(dictionary: dict):
    """Converts a dictionary to a YAML string.

    Args:
        dictionary: The dictionary to be converted to YAML.
    Returns:
        The YAML string.
    """
    yaml_object = ruamel.yaml.YAML()
    yaml_object.width = 60
    yaml_object.indent(mapping=2, sequence=4, offset=2)
    with io.StringIO() as string_stream:
        yaml_object.dump(dictionary, string_stream)
        return string_stream.getvalue()


def define_env(env):
    # See https://mkdocs-macros-plugin.readthedocs.io/en/latest/macros/
    sample_entries = data.read_a_yaml_file(
        repository_root / "docs" / "user_guide" / "sample_entries.yaml"
    )
    # validate the parsed dictionary by creating an instance of SampleEntries:
    SampleEntries(**sample_entries)

    entries_showcase = {}
    for entry_name, entry in sample_entries.items():
        proper_entry_name = entry_name.replace("_", " ").title().replace(" ", "")
        entries_showcase[proper_entry_name] = {
            "yaml": dictionary_to_yaml(entry),
            "figures": [
                {
                    "path": f"../assets/images/{theme}/{entry_name}.png",
                    "alt_text": f"{proper_entry_name} in {theme}",
                    "theme": theme,
                }
                for theme in data.available_themes
            ],
        }

    env.variables["sample_entries"] = entries_showcase

    # For theme templates reference docs
    themes_path = rendercv_path / "themes"
    theme_templates = {}
    for theme in data.available_themes:
        theme_templates[theme] = {}
        for theme_file in themes_path.glob(f"{theme}/*.typ"):
            theme_templates[theme][theme_file.stem] = theme_file.read_text()

        # Update ordering of theme templates, if there are more files, add them to the
        # end
        order = [
            "Preamble.j2",
            "Header.j2",
            "SectionBeginning.j2",
            "SectionEnding.j2",
            "TextEntry.j2",
            "BulletEntry.j2",
            "NumberedEntry.j2",
            "ReversedNumberedEntry.j2",
            "OneLineEntry.j2",
            "EducationEntry.j2",
            "ExperienceEntry.j2",
            "NormalEntry.j2",
            "PublicationEntry.j2",
        ]
        remaining_files = set(theme_templates[theme].keys()) - set(order)
        order += list(remaining_files)
        theme_templates[theme] = {key: theme_templates[theme][key] for key in order}

        if theme != "markdown":
            theme_templates[theme] = {
                f"{key}.typ": value for key, value in theme_templates[theme].items()
            }
        else:
            theme_templates[theme] = {
                f"{key}.md": value for key, value in theme_templates[theme].items()
            }

    env.variables["theme_templates"] = theme_templates

    theme_components = {}
    for theme_file in themes_path.glob("components/*.typ"):
        theme_components[theme_file.stem] = theme_file.read_text()
    theme_components = {f"{key}.typ": value for key, value in theme_components.items()}

    env.variables["theme_components"] = theme_components

    # Available themes strings (put available themes between ``)
    themes = [f"`{theme}`" for theme in data.available_themes]
    env.variables["available_themes"] = ", ".join(themes)

    # Available social networks strings (put available social networks between ``)
    social_networks = [
        f"`{social_network}`" for social_network in data.available_social_networks
    ]
    env.variables["available_social_networks"] = ", ".join(social_networks)

    # Others:
    env.variables["available_page_sizes"] = ", ".join(
        [f"`{page_size}`" for page_size in get_args(theme_options.PageSize)]
    )
    env.variables["available_font_families"] = ", ".join(
        [f"`{font_family}`" for font_family in get_args(theme_options.FontFamily)]
    )
    env.variables["available_text_alignments"] = ", ".join(
        [
            f"`{text_alignment}`"
            for text_alignment in get_args(theme_options.TextAlignment)
        ]
    )
    env.variables["available_header_alignments"] = ", ".join(
        [
            f"`{header_alignment}`"
            for header_alignment in get_args(theme_options.Alignment)
        ]
    )
    env.variables["available_section_title_types"] = ", ".join(
        [
            f"`{section_title_type}`"
            for section_title_type in get_args(
                get_args(theme_options.SectionTitleType)[0]
            )
        ]
    )
    env.variables["available_bullets"] = ", ".join(
        [f"`{bullet}`" for bullet in get_args(theme_options.BulletPoint)]
    )
