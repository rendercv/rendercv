import re
from typing import Optional

import pydantic


def make_given_keywords_bold_in_a_dictionary(
    dictionary: dict, keywords: list[str]
) -> dict:
    """Iterate over the dictionary recursively and make the given keywords bold.

    Args:
        dictionary: The dictionary to make the keywords bold.
        keywords: The keywords to make bold.

    Returns:
        The dictionary with the given keywords bold.
    """
    new_dictionary = dictionary.copy()
    for keyword in keywords:
        for key, value in dictionary.items():
            if isinstance(value, str):
                # Find all occurrences of the keyword as a whole word in the value:
                new_dictionary[key] = re.sub(rf"\b{keyword}\b", f"**{keyword}**", value)
            elif isinstance(value, dict):
                new_dictionary[key] = make_given_keywords_bold_in_a_dictionary(
                    value, keywords
                )
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        new_dictionary[key][i] = item.replace(keyword, f"**{keyword}**")
                    elif isinstance(item, dict):
                        new_dictionary[key][i] = (
                            make_given_keywords_bold_in_a_dictionary(item, keywords)
                        )
    return new_dictionary


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


def parse_validation_errors(
    exception: pydantic.ValidationError,
) -> list[dict[str, str]]:
    """Take a Pydantic validation error, parse it, and return a list of error
    dictionaries that contain the error messages, locations, and the input values.

    Pydantic's `ValidationError` object is a complex object that contains a lot of
    information about the error. This function takes a `ValidationError` object and
    extracts the error messages, locations, and the input values.

    Args:
        exception: The Pydantic validation error object.

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
        "Input should be a valid string": "This field should be a string!",
        "Input should be a valid list": (
            "This field should contain a list of items but it doesn't!"
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
            "loc": str(location),
            "msg": message,
            "input": str(input),
        }

        # if new_error is not in new_errors, then add it to new_errors
        if new_error not in new_errors:
            new_errors.append(new_error)

    return new_errors
