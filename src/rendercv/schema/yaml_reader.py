import pathlib

import ruamel.yaml
import ruamel.yaml.composer
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.composer import Composer
from ruamel.yaml.nodes import ScalarNode

from rendercv.exception import RenderCVInternalError, RenderCVUserError


def read_yaml(file_path_or_contents: pathlib.Path | str) -> CommentedMap:
    """Parse YAML/JSON content from file path or string.

    Why:
        Validation errors must point to exact YAML locations. CommentedMap
        preserves source coordinates that map Pydantic errors back to input
        lines, enabling user-friendly error tables showing exactly where
        mistakes occur in the input file.

    Example:
        ```py
        data = read_yaml(pathlib.Path("cv.yaml"))
        name = data["cv"]["name"]  # Regular dict access
        # Line info also available: data.lc.data["cv"][0] = (line, col)
        ```

    Args:
        file_path_or_contents: File path or raw YAML string.
        read_type: Parsing mode passed to ruamel.yaml.

    Returns:
        Dictionary with line/column metadata for error reporting.
    """
    if isinstance(file_path_or_contents, pathlib.Path):
        # Check if the file exists:
        if not file_path_or_contents.exists():
            message = f"The input file `{file_path_or_contents}` doesn't exist!"
            raise RenderCVUserError(message)

        # Check the file extension:
        accepted_extensions = [".yaml", ".yml", ".json", ".json5"]
        if file_path_or_contents.suffix not in accepted_extensions:
            message = (
                "The input file should have one of the following extensions:"
                f" {', '.join(accepted_extensions)}. The input file is"
                f" {file_path_or_contents.name}."
            )
            raise RenderCVUserError(message)

        file_content = file_path_or_contents.read_text(encoding="utf-8")
    else:
        file_content = file_path_or_contents

    yaml_as_dictionary: CommentedMap = yaml.load(file_content)

    if yaml_as_dictionary is None:
        message = "The input file is empty!"
        raise RenderCVUserError(message)

    if isinstance(yaml_as_dictionary, str):
        message = (
            "You probably meant to pass a path to the YAML file, but you passed as a"
            " string and RenderCV interpreted it as the contents of the YAML file."
            f" Pass the path using `pathlib.Path({file_path_or_contents})`."
        )
        raise RenderCVInternalError(message)

    return yaml_as_dictionary


class ComposerNoAlias(Composer):
    """Custom Composer that treats YAML aliases (*) as literal strings."""

    def compose_node(self, parent, index):
        """Override to handle alias events as literal strings."""
        if self.parser.check_event(ruamel.yaml.events.AliasEvent):
            event = self.parser.get_event()
            anchor = event.anchor
            # Return a scalar node with the literal "*anchor" value and position info
            return ScalarNode(
                tag="tag:yaml.org,2002:str",
                value=f"*{anchor}",
                start_mark=event.start_mark,
                end_mark=event.end_mark,
            )
        return super().compose_node(parent, index)


# Monkey-patch the Composer to treat aliases as literal strings:
ruamel.yaml.composer.Composer = ComposerNoAlias
yaml = ruamel.yaml.YAML()

# Disable ISO date parsing, keep it as a string:
yaml.constructor.yaml_constructors["tag:yaml.org,2002:timestamp"] = (
    lambda loader, node: loader.construct_scalar(node)
)
