import pathlib
from typing import cast

import pydantic
import pydantic_core
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap
from typing_extensions import TypedDict

from .models.custom_error_types import CustomPydanticErrorTypes
from .yaml_reader import read_yaml


class RenderCVValidationError(TypedDict):
    location: tuple[str, ...]
    yaml_location: tuple[tuple[int, int], tuple[int, int]]
    message: str
    input: str


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
    "entries",
)


def parse_plain_pydantic_error(
    plain_error: pydantic_core.ErrorDetails, user_input_as_commented_map: CommentedMap
) -> RenderCVValidationError:
    for unwanted_text in unwanted_texts:
        plain_error["msg"] = plain_error["msg"].replace(unwanted_text, "")

    if "ctx" in plain_error:
        if "input" in plain_error["ctx"]:
            plain_error["input"] = plain_error["ctx"]["input"]

        if "loc" in plain_error["ctx"]:
            plain_error["loc"] = plain_error["ctx"]["loc"]

    location = tuple(
        str(location_element)
        for location_element in plain_error["loc"]
        if location_element not in unwanted_locations
    )
    # Special case for end_date because Pydantic returns multiple end_date errors
    # since it has multiple valid formats:
    if "end_date" in location[-1]:
        plain_error["msg"] = (
            "This is not a valid `end_date`! Please use either YYYY-MM-DD, YYYY-MM,"
            ' or YYYY format or "present"!'
        )

    return {
        "location": location,
        "message": error_dictionary.get(plain_error["msg"], plain_error["msg"]),
        "input": (
            str(plain_error["input"])
            if not isinstance(plain_error["input"], dict | list)
            else "..."
        ),
        "yaml_location": get_coordinates_of_a_key_in_a_yaml_object(
            user_input_as_commented_map,
            location if plain_error["type"] != "missing" else location[:-1],
        ),
    }


def parse_validation_errors(
    exception: pydantic.ValidationError, user_input_as_commented_map: CommentedMap
) -> list[RenderCVValidationError]:
    """Take a Pydantic validation error, parse it, and return a list of error
    dictionaries that contain the error messages, locations, and the input values.

    Pydantic's `ValidationError` object is a complex object that contains a lot of
    information about the error. This function takes a `ValidationError` object and
    extracts the error messages, locations, and the input values.

    Args:
        exception: The Pydantic validation error object.
        user_input_as_commented_map: The user input as a CommentedMap.

    Returns:
        A list of error dictionaries that contain the error messages, locations, and the
        input values.
    """
    all_plain_errors = exception.errors()
    all_final_errors: list[RenderCVValidationError] = []

    for plain_error in all_plain_errors:
        all_final_errors.append(
            parse_plain_pydantic_error(plain_error, user_input_as_commented_map)
        )

        if plain_error["type"] == CustomPydanticErrorTypes.entry_validation.value:
            assert "ctx" in plain_error
            assert "caused_by" in plain_error["ctx"]
            for plain_cause_error in plain_error["ctx"]["caused_by"]:
                plain_cause_error["loc"] = tuple(
                    list(plain_error["loc"]) + list(plain_cause_error["loc"])
                )
                all_final_errors.append(
                    parse_plain_pydantic_error(
                        plain_cause_error, user_input_as_commented_map
                    )
                )

    return all_final_errors


def get_inner_yaml_object_from_its_key(
    yaml_object: CommentedMap, location_key: str
) -> tuple[CommentedMap, tuple[tuple[int, int], tuple[int, int]]]:
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
            raise KeyError(message) from e
    except ValueError as e:
        # Otherwise, the part is a key in a mapping.
        if location_key not in yaml_object:
            message = f"Key '{location_key}' not found in the YAML file."
            raise KeyError(message) from e

        inner_yaml_object = yaml_object[location_key]
        start_line, start_col, end_line, end_col = yaml_object.lc.data[location_key]
        coordinates = ((start_line + 1, start_col + 1), (end_line + 1, end_col))

    return inner_yaml_object, coordinates


def get_coordinates_of_a_key_in_a_yaml_object(
    yaml_object: ruamel.yaml.YAML, location: tuple[str, ...]
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Find the coordinates of a key in a YAML object.

    Args:
        yaml_object: The YAML object.
        location: The location of the key in the YAML object. For example,
            `['cv', 'sections', 'education', '0', 'degree']`.

    Returns:
        The coordinates of the key in the YAML object in the format
        ((start_line, start_column), (end_line, end_column)).
        (Line and column numbers are 0-indexed.)
    """

    current_yaml_object: ruamel.yaml.YAML = yaml_object
    coordinates = ((0, 0), (0, 0))
    # start from the first key and move forward:
    for location_key in location:
        current_yaml_object, coordinates = get_inner_yaml_object_from_its_key(
            current_yaml_object, location_key
        )

    return coordinates
