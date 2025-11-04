import pathlib
from datetime import date as Date

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

from ..models.rendercv_model import RenderCVModel
from .context import ValidationContext


def read_input_file(file_path_or_contents: pathlib.Path | str) -> RenderCVModel:
    """Read the input file (YAML or JSON) and return them as an instance of
    `RenderCVDataModel`, which is a Pydantic data model of RenderCV's data format.

    Args:
        file_path_or_contents: The path to the input file or the contents of the input
            file as a string.

    Returns:
        The data model.
    """
    input_as_dictionary = read_a_yaml_file(file_path_or_contents)
    
    return validate_input_dictionary_and_return_rendercv_pydantic_model(
        input_as_dictionary
    )


def validate_input_dictionary_and_return_rendercv_pydantic_model(
    input_dictionary: dict,
    input_file_path: pathlib.Path | None = None,
) -> RenderCVModel:
    """Validate the input dictionary by creating an instance of `RenderCVModel`,
    which is a Pydantic data model of RenderCV's data format.

    Args:
        input_dictionary: The input dictionary.
        input_file_path: The path to the input file, to pass to the validation context.

    Returns:
        The data model.
    """
    return RenderCVModel.model_validate(
        input_dictionary,
        context={
            "context": ValidationContext(
                input_file_path=input_file_path or pathlib.Path(),
                date_today=input_dictionary.get("rendercv_settings", {}).get(
                    "date", Date.today()
                ),
            )
        },
    )


def read_a_yaml_file(
    file_path_or_contents: pathlib.Path | str,
) -> CommentedMap:
    """Read a YAML file and return its content as a dictionary. The YAML file can be
    given as a path to the file or as the contents of the file as a string.

    Args:
        file_path_or_contents: The path to the YAML file or the contents of the YAML
            file as a string.

    Returns:
        The content of the YAML file as a dictionary.
    """

    if isinstance(file_path_or_contents, pathlib.Path):
        # Check if the file exists:
        if not file_path_or_contents.exists():
            message = f"The input file {file_path_or_contents} doesn't exist!"
            raise FileNotFoundError(message)

        # Check the file extension:
        accepted_extensions = [".yaml", ".yml", ".json", ".json5"]
        if file_path_or_contents.suffix not in accepted_extensions:
            message = (
                "The input file should have one of the following extensions:"
                f" {', '.join(accepted_extensions)}. The input file is"
                f" {file_path_or_contents}."
            )
            raise ValueError(message)

        file_content = file_path_or_contents.read_text(encoding="utf-8")
    else:
        file_content = file_path_or_contents

    yaml = ruamel.yaml.YAML()

    # Disable ISO date parsing, keep it as a string:
    yaml.constructor.yaml_constructors["tag:yaml.org,2002:timestamp"] = (
        lambda loader, node: loader.construct_scalar(node)
    )

    yaml_as_a_dictionary: CommentedMap = yaml.load(file_content)

    if yaml_as_a_dictionary is None:
        message = "The input file is empty!"
        raise ValueError(message)

    return yaml_as_a_dictionary
