import pathlib

import ruamel.yaml
import ruamel.yaml.scanner
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scanner import RoundTripScanner

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


class ScannerNoAlias(RoundTripScanner):
    """Custom Scanner that treats * as a regular character instead of alias syntax."""

    def fetch_alias(self):
        """Treat * as a plain scalar character instead of alias syntax."""
        # Instead of scanning as alias, treat as plain scalar
        self.fetch_plain()


# Monkey-patch the RoundTripScanner to treat * as a regular character:
ruamel.yaml.scanner.RoundTripScanner = ScannerNoAlias  # ty: ignore[invalid-assignment]
yaml = ruamel.yaml.YAML()

# Disable ISO date parsing, keep it as a string:
yaml.constructor.yaml_constructors["tag:yaml.org,2002:timestamp"] = (
    lambda loader, node: loader.construct_scalar(node)
)
