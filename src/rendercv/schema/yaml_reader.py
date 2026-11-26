import pathlib

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scanner import RoundTripScanner

from rendercv.exception import RenderCVUserError


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

    yaml_as_dictionary: CommentedMap = build_yaml_parser().load(file_content)

    if yaml_as_dictionary is None:
        message = "The input file is empty!"
        raise RenderCVUserError(message)

    if not isinstance(yaml_as_dictionary, CommentedMap):
        message = (
            "The input must be a YAML mapping of `key: value` pairs (e.g. starting"
            " with `cv:`), not a single value or a list."
        )
        if isinstance(yaml_as_dictionary, str):
            message += (
                " If you meant to pass a file path, pass it as a `pathlib.Path`"
                " instead of a string."
            )
        raise RenderCVUserError(message)

    return yaml_as_dictionary


class ScannerNoAlias(RoundTripScanner):
    """Custom Scanner that treats * as a regular character instead of alias syntax.

    Why:
        CV content frequently contains literal * characters (e.g., in Markdown bold
        syntax). Standard YAML interprets * as an alias indicator, causing parse
        errors. This subclass overrides alias handling to treat * as plain text.
    """

    def fetch_alias(self) -> None:
        """Treat * as a plain scalar character instead of alias syntax."""
        self.fetch_plain()


def build_yaml_parser() -> ruamel.yaml.YAML:
    """Build a fresh ruamel YAML parser for one parse operation.

    Why:
        A ruamel `YAML` object keeps mutable parser/composer state between
        calls, so a shared module-level instance is not thread-safe: two
        threads parsing concurrently (as the web API's threadpool does)
        corrupt that state and crash with errors like
        `AttributeError: 'NoneType' object has no attribute 'id'`.
        Constructing a parser per call is cheap and makes every caller
        safe regardless of threading model.

    Returns:
        A configured parser with the no-alias scanner and string dates.
    """
    parser = ruamel.yaml.YAML()
    parser.Scanner = ScannerNoAlias

    # Disable ISO date parsing, keep it as a string:
    parser.constructor.yaml_constructors["tag:yaml.org,2002:timestamp"] = (
        lambda loader, node: loader.construct_scalar(node)
    )
    return parser
