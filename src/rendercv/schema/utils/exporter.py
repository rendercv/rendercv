import io
import json
import pathlib

import ruamel.yaml

from rendercv import __version__

from ..models.cv.cv import Cv
from ..models.design.built_in_design import built_in_design_adapter
from ..models.locale.locale import locale_adapter
from ..models.rendercv_model import RenderCVModel
from . import reader


def dictionary_to_yaml(dictionary: dict) -> str:
    """Converts a dictionary to a YAML string.

    Args:
        dictionary: The dictionary to be converted to YAML.

    Returns:
        The YAML string.
    """

    # Source: https://gist.github.com/alertedsnake/c521bc485b3805aa3839aef29e39f376
    def str_representer(dumper, data):
        if len(data.splitlines()) > 1:  # check for multiline string
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml_object = ruamel.yaml.YAML()
    yaml_object.encoding = "utf-8"
    yaml_object.width = 9999
    yaml_object.indent(mapping=2, sequence=4, offset=2)
    yaml_object.representer.add_representer(str, str_representer)

    with io.StringIO() as string_stream:
        yaml_object.dump(dictionary, string_stream)
        return string_stream.getvalue()


def create_sample_rendercv_pydantic_model(
    name: str = "John Doe", theme: str = "classic", locale: str = "english"
) -> RenderCVModel:
    """Return a sample data model for new users to start with.

    Args:
        name: The name of the person.
        theme: The theme of the CV.
        locale: The locale of the CV.
    Returns:
        A sample data model.
    """
    sample_content = pathlib.Path(__file__).parent / "sample_content.yaml"
    sample_content_dictionary = reader.read_a_yaml_file(sample_content)
    cv = Cv(**sample_content_dictionary)

    name = name.encode().decode("unicode-escape")
    cv.name = name

    design = built_in_design_adapter.validate_python(theme)
    locale = locale_adapter.validate_python(locale)

    return RenderCVModel(cv=cv, design=design, locale=locale)


def create_a_sample_yaml_input_file(
    input_file_path: pathlib.Path | None = None,
    name: str = "John Doe",
    theme: str = "classic",
    locale: str = "english",
) -> str:
    """Create a sample YAML input file and return it as a string. If the input file path
    is provided, then also save the contents to the file.

    Args:
        input_file_path: The path to save the input file. Defaults to None.
        name: The name of the person. Defaults to "John Doe".
        theme: The theme of the CV. Defaults to "classic".

    Returns:
        The sample YAML input file as a string.
    """
    data_model = create_sample_rendercv_pydantic_model(
        name=name, theme=theme, locale=locale
    )

    # Instead of getting the dictionary with data_model.model_dump() directly, we
    # convert it to JSON and then to a dictionary. Because the YAML library we are
    # using sometimes has problems with the dictionary returned by model_dump().

    # We exclude "cv.sections" because the data model automatically generates them.
    # The user's "cv.sections" input is actually "cv.sections_input" in the data
    # model. It is shown as "cv.sections" in the YAML file because an alias is being
    # used. If"cv.sections" were not excluded, the automatically generated
    # "cv.sections" would overwrite the "cv.sections_input". "cv.sections" are
    # automatically generated from "cv.sections_input" to make the templating
    # process easier. "cv.sections_input" exists for the convenience of the user.
    # Also, we don't want to show the cv.photo field in the Web app.
    data_model_as_json = data_model.model_dump_json(
        exclude_none=False,
        by_alias=True,
        exclude={
            "cv": {"sections", "photo"},
            "rendercv_settings": {"render_command"},
        },
    )
    data_model_as_dictionary = json.loads(data_model_as_json)

    yaml_string = dictionary_to_yaml(data_model_as_dictionary)

    # Add a comment to the first line, for JSON Schema:
    comment_to_add = (
        "# yaml-language-server:"
        f" $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v{__version__}/schema.json\n"
    )
    yaml_string = comment_to_add + yaml_string

    if input_file_path is not None:
        input_file_path.write_text(yaml_string, encoding="utf-8")

    return yaml_string
