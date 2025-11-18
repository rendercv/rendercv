import pathlib
from typing import Literal

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap


def read_yaml(
    file_path_or_contents: pathlib.Path | str,
    read_type: Literal["safe"] | None = None,
) -> CommentedMap:
    """Read a YAML file and return its content as a dictionary. The YAML file can be
    given as a path to the file or as the contents of the file as a string.

    Args:
        file_path_or_contents: The path to the YAML file or the contents of the YAML
            file as a string.

    Returns:
        The content of the YAML file as a CommentedMap (Python dictionary with
        additional information about the location of the keys in the YAML file).
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

    yaml = ruamel.yaml.YAML(typ=read_type)

    # Disable ISO date parsing, keep it as a string:
    yaml.constructor.yaml_constructors["tag:yaml.org,2002:timestamp"] = (
        lambda loader, node: loader.construct_scalar(node)
    )

    yaml_as_a_dictionary: CommentedMap = yaml.load(file_content)

    if yaml_as_a_dictionary is None:
        message = "The input file is empty!"
        raise ValueError(message)

    return yaml_as_a_dictionary
