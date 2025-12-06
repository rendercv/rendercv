import pathlib
from typing import cast

import pydantic
import pydantic_core
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

from rendercv.exception import RenderCVInternalError, RenderCVValidationError

from .models.custom_error_types import CustomPydanticErrorTypes
from .yaml_reader import read_yaml

error_dictionary = cast(
    dict[str, str],
    read_yaml(pathlib.Path(__file__).parent / "error_dictionary.yaml"),
)
unwanted_texts = ("value is not a valid email address: ", "Value error, ")
unwanted_locations = (
    "tagged-union",
    "list",
    "literal",
    "int",
    "constrained-str",
    "function-after",
)


def parse_plain_pydantic_error(
    plain_error: pydantic_core.ErrorDetails, user_input_as_commented_map: CommentedMap
) -> RenderCVValidationError:
    """Transform raw Pydantic error into user-friendly validation error with YAML coordinates.

    Why:
        Pydantic errors contain technical jargon and generic locations unsuitable
        for end users. This converts them to plain English messages with exact
        YAML line numbers, mapped via error_dictionary.yaml.

    Args:
        plain_error: Raw Pydantic validation error.
        user_input_as_commented_map: YAML dict with line/column metadata.

    Returns:
        Structured error with location tuple, friendly message, and YAML coordinates.
    """
    for unwanted_text in unwanted_texts:
        plain_error["msg"] = plain_error["msg"].replace(unwanted_text, "")

    if plain_error["loc"][0] in ["design", "locale"]:
        # Skip the second key because it's the discriminator value.
        plain_error["loc"] = plain_error["loc"][:1] + plain_error["loc"][2:]

    if "ctx" in plain_error:
        if "input" in plain_error["ctx"]:
            plain_error["input"] = plain_error["ctx"]["input"]

        if "loc" in plain_error["ctx"]:
            plain_error["loc"] = plain_error["ctx"]["loc"]

    location = tuple(
        str(location_element)
        for location_element in plain_error["loc"]
        if not any(item in str(location_element) for item in unwanted_locations)
    )
    # Special case for end_date because Pydantic returns multiple end_date errors
    # since it has multiple valid formats:
    if "end_date" in location[-1]:
        plain_error["msg"] = (
            "This is not a valid `end_date`! Please use either YYYY-MM-DD, YYYY-MM,"
            ' or YYYY format or "present"!'
        )

    error_message = error_dictionary.get(plain_error["msg"], plain_error["msg"])
    if not error_message.endswith("."):
        error_message += "."

    return RenderCVValidationError(
        location=location,
        message=error_message,
        input=(
            str(plain_error["input"])
            if not isinstance(plain_error["input"], dict | list)
            else "..."
        ),
        yaml_location=get_coordinates_of_a_key_in_a_yaml_object(
            user_input_as_commented_map,
            location if plain_error["type"] != "missing" else location[:-1],
        ),
    )


def parse_validation_errors(
    exception: pydantic.ValidationError,
    rendercv_dictionary_as_commented_map: CommentedMap,
) -> list[RenderCVValidationError]:
    """Extract all validation errors from Pydantic exception with deduplication.

    Why:
        Single Pydantic ValidationError contains multiple sub-errors. Entry
        validation errors include nested causes that must be flattened and
        deduplicated before display. This aggregates all errors into a single
        list for table rendering.

    Args:
        exception: Pydantic validation exception.
        rendercv_dictionary_as_commented_map: YAML dict with location metadata.

    Returns:
        Deduplicated list of user-friendly validation errors.
    """
    all_plain_errors = exception.errors()
    all_final_errors: list[RenderCVValidationError] = []

    for plain_error in all_plain_errors:
        all_final_errors.append(
            parse_plain_pydantic_error(
                plain_error, rendercv_dictionary_as_commented_map
            )
        )

        if plain_error["type"] == CustomPydanticErrorTypes.entry_validation.value:
            assert "ctx" in plain_error
            assert "caused_by" in plain_error["ctx"]
            for plain_cause_error in plain_error["ctx"]["caused_by"]:
                loc = plain_cause_error["loc"][1:]  # Omit `entries` location
                plain_cause_error["loc"] = plain_error["loc"] + loc
                all_final_errors.append(
                    parse_plain_pydantic_error(
                        plain_cause_error, rendercv_dictionary_as_commented_map
                    )
                )

    # Remove duplicates from all_final_errors:
    error_locations = set()
    errors_without_duplicates = []
    for error in all_final_errors:
        location = error.location
        if location not in error_locations:
            error_locations.add(location)
            errors_without_duplicates.append(error)

    return errors_without_duplicates


def get_inner_yaml_object_from_its_key(
    yaml_object: CommentedMap, location_key: str
) -> tuple[CommentedMap, tuple[tuple[int, int], tuple[int, int]]]:
    """Navigate one level into YAML structure and extract coordinates.

    Why:
        Error locations are dotted paths like `cv.sections.education.0.degree`.
        Each traversal step must extract both the nested object and its exact
        source coordinates for error highlighting.

    Args:
        yaml_object: Current YAML object being traversed.
        location_key: Single key or list index as string.

    Returns:
        Tuple of nested object and ((start_line, start_col), (end_line, end_col)).
    """
    # If the part is numeric, interpret it as a list index:
    try:
        index = int(location_key)
        try:
            inner_yaml_object = yaml_object[index]
            # Get the coordinates from the list's lc.data (which is a list of tuples).
            start_line, start_col = yaml_object.lc.data[index]
            end_line, end_col = start_line, start_col
            coordinates = ((start_line + 1, start_col - 1), (end_line + 1, end_col))
        except IndexError as e:
            message = f"Index {index} is out of range in the YAML file."
            raise RenderCVInternalError(message) from e
    except ValueError as e:
        # Otherwise, the part is a key in a mapping.
        if location_key not in yaml_object:
            message = f"Key '{location_key}' not found in the YAML file."
            raise RenderCVInternalError(message) from e

        inner_yaml_object = yaml_object[location_key]
        start_line, start_col, end_line, end_col = yaml_object.lc.data[location_key]
        coordinates = ((start_line + 1, start_col + 1), (end_line + 1, end_col))

    return inner_yaml_object, coordinates


def get_coordinates_of_a_key_in_a_yaml_object(
    yaml_object: ruamel.yaml.YAML, location: tuple[str, ...]
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Resolve dotted location path to exact YAML source coordinates.

    Why:
        Error tables must show users exactly which line/column contains
        the invalid value. Recursive traversal through CommentedMap's
        lc.data preserves coordinates at every nesting level.

    Example:
        ```py
        data = read_yaml(pathlib.Path("cv.yaml"))
        coords = get_coordinates_of_a_key_in_a_yaml_object(
            data, ("cv", "sections", "education", "0", "degree")
        )
        # coords = ((12, 4), (12, 10)) for line 12, columns 4-10
        ```

    Args:
        yaml_object: Root YAML object with location metadata.
        location: Path segments from root to target key.

    Returns:
        ((start_line, start_col), (end_line, end_col)) in 1-indexed coordinates.
    """

    current_yaml_object: ruamel.yaml.YAML = yaml_object
    coordinates = ((0, 0), (0, 0))
    # start from the first key and move forward:
    for location_key in location:
        current_yaml_object, coordinates = get_inner_yaml_object_from_its_key(
            current_yaml_object, location_key
        )

    return coordinates
