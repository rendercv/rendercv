"""
The `rendercv.data.reader` module contains the functions that are used to read the input
file (YAML or JSON) and return them as an instance of `RenderCVDataModel`, which is a
Pydantic data model of RenderCV's data format.
"""

import pathlib
import re
from typing import Optional

import pydantic
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

from . import models
from .models import entry_types


def make_given_keywords_bold_in_sections(
    sections_input: models.Sections, keywords: list[str]
) -> models.Sections:
    """Iterate over the dictionary recursively and make the given keywords bold.

    Args:
        sections_input: The sections input as a Pydantic model.
        keywords: The keywords to make bold.

    Returns:
        The dictionary with the given keywords bold.
    """
    if sections_input is None:
        return None

    for entries in sections_input.values():
        for i, entry in enumerate(entries):
            if isinstance(entry, str):
                entries[i] = entry_types.make_keywords_bold_in_a_string(  # type: ignore
                    entry, keywords
                )
            elif callable(getattr(entry, "make_keywords_bold", None)):
                entries[i] = entry.make_keywords_bold(keywords)  # type: ignore

    return sections_input


def get_error_message_and_location_and_value_from_a_custom_error(
    error_string: str,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Look at a string and figure out if it's a custom error message that has been
    sent from `rendercv.data.reader.read_input_file`. If it is, then return the custom
    message, location, and the input value.

    This is done because sometimes we raise an error about a specific field in the model
    validation level, but Pydantic doesn't give us the exact location of the error
    because it's a model-level error. So, we raise a custom error with three string
    arguments: message, location, and input value. Those arguments then combined into a
    string by Python. This function is used to parse that custom error message and
    return the three values.

    Args:
        error_string: The error message.

    Returns:
        The custom message, location, and the input value.
    """
    pattern = r"""\(['"](.*)['"], '(.*)', '(.*)'\)"""
    match = re.search(pattern, error_string)
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, None


def get_coordinates_of_a_key_in_a_yaml_object(
    yaml_object: ruamel.yaml.YAML, location: list[str]
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

    current_yaml_object: ruamel.yaml.YAML = yaml_object
    coordinates = ((0, 0), (0, 0))
    # start from the first key and move forward:
    for location_key in location:
        current_yaml_object, coordinates = get_inner_yaml_object_from_its_key(
            current_yaml_object, location_key
        )

    return coordinates


def parse_validation_errors(
    exception: pydantic.ValidationError, yaml_file_as_string: Optional[str] = None
) -> list[dict[str, str]]:
    """Take a Pydantic validation error, parse it, and return a list of error
    dictionaries that contain the error messages, locations, and the input values.

    Pydantic's `ValidationError` object is a complex object that contains a lot of
    information about the error. This function takes a `ValidationError` object and
    extracts the error messages, locations, and the input values.

    Args:
        exception: The Pydantic validation error object.
        yaml_file_as_string: The YAML file as a string.

    Returns:
        A list of error dictionaries that contain the error messages, locations, and the
        input values.
    """
    # This dictionary is used to convert the error messages that Pydantic returns to
    # more user-friendly messages.
    error_dictionary: dict[str, str] = {
        "Input should be 'present'": (
            "This is not a valid date! Please use either YYYY-MM-DD, YYYY-MM, or YYYY"
            ' format or "present"!'
        ),
        "Input should be a valid integer, unable to parse string as an integer": (
            "This is not a valid date! Please use either YYYY-MM-DD, YYYY-MM, or YYYY"
            " format!"
        ),
        "String should match pattern '\\d{4}-\\d{2}(-\\d{2})?'": (
            "This is not a valid date! Please use either YYYY-MM-DD, YYYY-MM, or YYYY"
            " format!"
        ),
        "String should match pattern '\\b10\\..*'": (
            'A DOI prefix should always start with "10.". For example,'
            ' "10.1109/TASC.2023.3340648".'
        ),
        "URL scheme should be 'http' or 'https'": "This is not a valid URL!",
        "Field required": "This field is required!",
        "value is not a valid phone number": "This is not a valid phone number!",
        "month must be in 1..12": "The month must be between 1 and 12!",
        "day is out of range for month": "The day is out of range for the month!",
        "Extra inputs are not permitted": (
            "This field is unknown for this object! Please remove it."
        ),
        "Input should be a valid string": (
            "This field should be provided or removed to use the default value!"
        ),
        "Input should be a valid list": (
            "This field should contain a list of items but it doesn't!"
        ),
        "value is not a valid color: value must be tuple, list or string": (
            "This is not a valid color! Here are some examples of valid colors:"
            ' "red", "#ff0000", "rgb(255, 0, 0)", "hsl(0, 100%, 50%)"'
        ),
        "value is not a valid color: string not recognised as a valid color": (
            "This is not a valid color! Here are some examples of valid colors:"
            ' "red", "#ff0000", "rgb(255, 0, 0)", "hsl(0, 100%, 50%)"'
        ),
    }

    unwanted_texts = ["value is not a valid email address: ", "Value error, "]

    # Check if this is a section error. If it is, we need to handle it differently.
    # This is needed because how dm.validate_section_input function raises an exception.
    # This is done to tell the user which which EntryType RenderCV excepts to see.
    errors = exception.errors()
    for error_object in errors.copy():
        if (
            "There are problems with the entries." in error_object["msg"]
            and "ctx" in error_object
        ):
            location = error_object["loc"]
            ctx_object = error_object["ctx"]
            if "error" in ctx_object:
                inner_error_object = ctx_object["error"]
                if hasattr(inner_error_object, "__cause__"):
                    cause_object = inner_error_object.__cause__
                    cause_object_errors = cause_object.errors()
                    for cause_error_object in cause_object_errors:
                        # we use [1:] to avoid `entries` location. It is a location for
                        # RenderCV's own data model, not the user's data model.
                        cause_error_object["loc"] = tuple(
                            list(location) + list(cause_error_object["loc"][1:])
                        )
                    errors.extend(cause_object_errors)

    # some locations are not really the locations in the input file, but some
    # information about the model coming from Pydantic. We need to remove them.
    # (e.g. avoid stuff like .end_date.literal['present'])
    unwanted_locations = ["tagged-union", "list", "literal", "int", "constrained-str"]
    for error_object in errors:
        location = [str(location_element) for location_element in error_object["loc"]]
        new_location = [str(location_element) for location_element in location]
        for location_element in location:
            for unwanted_location in unwanted_locations:
                if unwanted_location in location_element:
                    new_location.remove(location_element)
        error_object["loc"] = new_location  # type: ignore

    # Parse all the errors and create a new list of errors.
    new_errors: list[dict[str, str]] = []
    for error_object in errors:
        message = error_object["msg"]
        location = ".".join(error_object["loc"])  # type: ignore
        input = error_object["input"]

        # Check if this is a custom error message:
        custom_message, custom_location, custom_input_value = (
            get_error_message_and_location_and_value_from_a_custom_error(message)
        )
        if custom_message is not None:
            message = custom_message
            if custom_location:
                # If the custom location is not empty, then add it to the location.
                location = f"{location}.{custom_location}"
            input = custom_input_value

        # Don't show unwanted texts in the error message:
        for unwanted_text in unwanted_texts:
            message = message.replace(unwanted_text, "")

        # Convert the error message to a more user-friendly message if it's in the
        # error_dictionary:
        if message in error_dictionary:
            message = error_dictionary[message]

        # Special case for end_date because Pydantic returns multiple end_date errors
        # since it has multiple valid formats:
        if "end_date" in location:
            message = (
                "This is not a valid end date! Please use either YYYY-MM-DD, YYYY-MM,"
                ' or YYYY format or "present"!'
            )

        # If the input is a dictionary or a list (the model itself fails to validate),
        # then don't show the input. It looks confusing and it is not helpful.
        if isinstance(input, dict | list):
            input = ""

        new_error = {
            "loc": tuple(location.split(".")),
            "msg": message,
            "input": str(input),
        }

        if yaml_file_as_string:
            yaml_object = read_a_yaml_file(yaml_file_as_string)
            coordinates = get_coordinates_of_a_key_in_a_yaml_object(
                yaml_object,
                list(new_error["loc"]),  # type: ignore
            )
            new_error["yaml_loc"] = coordinates

        # if new_error is not in new_errors, then add it to new_errors
        if new_error not in new_errors:
            new_errors.append(new_error)

    return new_errors


def read_a_yaml_file(file_path_or_contents: pathlib.Path | str) -> dict:
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
            user_friendly_accepted_extensions = [
                f"[green]{ext}[/green]" for ext in accepted_extensions
            ]
            user_friendly_accepted_extensions = ", ".join(
                user_friendly_accepted_extensions
            )
            message = (
                "The input file should have one of the following extensions:"
                f" {user_friendly_accepted_extensions}. The input file is"
                f" {file_path_or_contents}."
            )
            raise ValueError(message)

        file_content = file_path_or_contents.read_text(encoding="utf-8")
    else:
        file_content = file_path_or_contents

    yaml_as_a_dictionary: dict = ruamel.yaml.YAML().load(file_content)

    if yaml_as_a_dictionary is None:
        message = "The input file is empty!"
        raise ValueError(message)

    return yaml_as_a_dictionary


def validate_input_dictionary_and_return_the_data_model(
    input_dictionary: dict,
    context: Optional[dict] = None,
) -> models.RenderCVDataModel:
    """Validate the input dictionary by creating an instance of `RenderCVDataModel`,
    which is a Pydantic data model of RenderCV's data format.

    Args:
        input_dictionary: The input dictionary.
        context: The context dictionary that is used to validate the input dictionary.
            It's used to send the input file path with the context object, but it's not
            required.

    Returns:
        The data model.
    """
    # Validate the parsed dictionary by creating an instance of RenderCVDataModel:
    data_model = models.RenderCVDataModel.model_validate(
        input_dictionary, context=context
    )

    # If the `bold_keywords` field is provided in the `rendercv_settings`, make the
    # given keywords bold in the `cv.sections` field:
    if data_model.rendercv_settings and data_model.rendercv_settings.bold_keywords:
        data_model.cv.sections_input = make_given_keywords_bold_in_sections(
            data_model.cv.sections_input,
            data_model.rendercv_settings.bold_keywords,
        )

    return data_model


def read_input_file(
    file_path_or_contents: pathlib.Path | str,
) -> models.RenderCVDataModel:
    """Read the input file (YAML or JSON) and return them as an instance of
    `RenderCVDataModel`, which is a Pydantic data model of RenderCV's data format.

    Args:
        file_path_or_contents: The path to the input file or the contents of the input
            file as a string.

    Returns:
        The data model.
    """
    input_as_dictionary = read_a_yaml_file(file_path_or_contents)

    return validate_input_dictionary_and_return_the_data_model(input_as_dictionary)
