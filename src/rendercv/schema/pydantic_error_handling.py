import pathlib
from collections.abc import Iterator, Mapping, Sequence
from typing import Any, cast

import pydantic
import pydantic_core
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from rendercv.exception import (
    RenderCVInternalError,
    RenderCVValidationError,
    YamlLocation,
    YamlSource,
)

from .models.custom_error_types import CustomPydanticErrorTypes
from .yaml_reader import read_yaml

error_dictionary = cast(
    dict[str, str],
    read_yaml(pathlib.Path(__file__).parent / "error_dictionary.yaml"),
)


def resolve_location(
    location: tuple[str | int, ...], input_value: Any, *, missing: bool = False
) -> tuple[str | int, ...]:
    """Project Pydantic's path onto keys and indices in the input tree.

    Args:
        location: Raw path, possibly containing union branch labels.
        input_value: Original validation input.
        missing: Whether the final element names an absent required field.

    Returns:
        Existing input path, optionally followed by the missing field name.
    """
    resolved: list[str | int] = []
    for i, part in enumerate(location):
        if contains_location(input_value, (part,)):
            resolved.append(part)
            input_value = input_value[part]
        elif missing and i == len(location) - 1:
            resolved.append(part)
    return tuple(resolved)


def contains_location(document: Any, location: tuple[str | int, ...]) -> bool:
    """Tell whether a document has a value at a location.

    Args:
        document: Mapping or sequence.
        location: Keys and indices.

    Returns:
        Whether every key and index of the location exists.
    """
    for part in location:
        if (isinstance(document, Mapping) and part in document) or (
            isinstance(document, list | tuple)
            and isinstance(part, int)
            and 0 <= part < len(document)
        ):
            document = document[part]
        else:
            return False
    return True


def parse_plain_pydantic_error(
    plain_error: pydantic_core.ErrorDetails,
    input_dictionary: CommentedMap | dict[str, Any],
    sources: Sequence[tuple[YamlSource, CommentedMap]] = (),
) -> RenderCVValidationError:
    """Translate a structured error without modifying Pydantic's error details.

    Why:
        The input is the main file with other files laid over it, in order. A
        value comes from the last of them that has it, so its error is reported in
        that file, at that file's coordinates.

    Args:
        plain_error: Raw Pydantic validation error.
        input_dictionary: Validated input, with optional YAML coordinates.
        sources: The files laid over the main file, in order, with their documents.

    Returns:
        Friendly error with an input path and available source coordinates.
    """
    context = plain_error.get("ctx", {})
    missing = plain_error["type"] == "missing"
    location = resolve_location(plain_error["loc"], input_dictionary, missing=missing)
    value = plain_error["input"]
    template = error_dictionary.get(plain_error["type"])
    if template is not None:
        message = template.format(**context)
    elif plain_error["type"] == "value_error":
        # EmailStr supplies a reason; ordinary validators supply the exception.
        message = str(context.get("reason", context.get("error", plain_error["msg"])))
    elif (
        plain_error["type"] == "string_pattern_mismatch"
        and context.get("pattern") == r"\b10\..*"
    ):
        message = (
            'A DOI prefix should always start with "10.". For example,'
            ' "10.1109/TASC.2023.3340648".'
        )
    else:
        message = plain_error["msg"]
    if not message.endswith((".", "!", "?")):
        message += "."

    yaml_source: YamlSource = "main_yaml_file"
    coord_dict: Any = input_dictionary
    value_location = location[:-1] if missing else location
    for source, document in reversed(sources):
        if value_location and contains_location(document, value_location):
            yaml_source, coord_dict = source, document
            break

    return RenderCVValidationError(
        schema_location=tuple(str(part) for part in location),
        yaml_location=get_coordinates_of_a_key_in_a_yaml_object(
            coord_dict, value_location
        ),
        yaml_source=yaml_source,
        message=message,
        input=str(value) if not isinstance(value, dict | list) else "...",
    )


def parse_validation_errors(
    exception: pydantic.ValidationError,
    input_dictionary: CommentedMap | dict[str, Any],
    sources: Sequence[tuple[YamlSource, CommentedMap]] = (),
) -> list[RenderCVValidationError]:
    """Expand nested entry errors and remove only identical table rows.

    Args:
        exception: Pydantic validation exception.
        input_dictionary: Validated input with optional YAML coordinates.
        sources: The files laid over the main file, in order, with their documents.

    Returns:
        Errors in validation order, including distinct failures at the same path.
    """
    result: list[RenderCVValidationError] = []
    for error in expand_entry_errors(exception.errors()):
        parsed = parse_plain_pydantic_error(error, input_dictionary, sources)
        if parsed not in result:
            result.append(parsed)
    return result


def expand_entry_errors(
    errors: list[pydantic_core.ErrorDetails],
) -> Iterator[pydantic_core.ErrorDetails]:
    """Yield each error, followed by the errors that caused it, with full locations.

    Why:
        A section validates its entries in a nested validation call and reports
        their errors as the `caused_by` context of a single section error. Their
        locations are relative to that nested call, so they are prefixed with the
        section's location. Expansion is recursive because causes can be section
        errors themselves.

    Args:
        errors: Pydantic error details.

    Yields:
        The errors and their causes in validation order.
    """
    for error in errors:
        yield error
        if error["type"] == CustomPydanticErrorTypes.entry_validation.value:
            for cause in expand_entry_errors(error["ctx"]["caused_by"]):
                prefixed_cause = cause.copy()
                # The nested call's first location element is its `entries` field:
                prefixed_cause["loc"] = error["loc"] + cause["loc"][1:]
                yield prefixed_cause


def get_inner_yaml_object_from_its_key(
    yaml_object: Any, location_key: str | int
) -> tuple[Any, YamlLocation | None]:
    """Navigate by container type, preserving numeric-looking mapping keys.

    Args:
        yaml_object: Mapping or sequence to navigate.
        location_key: Mapping key or list index.

    Returns:
        Child value and its source coordinates, if present.

    Raises:
        RenderCVInternalError: If the requested key or index does not exist.
    """
    if isinstance(yaml_object, list | tuple):
        index = int(location_key)
        if not 0 <= index < len(yaml_object):
            message = f"Index {index} is out of range in the YAML file."
            raise RenderCVInternalError(message)
        location_key = index
    elif not isinstance(yaml_object, Mapping) or location_key not in yaml_object:
        message = f"Key '{location_key}' not found in the YAML file."
        raise RenderCVInternalError(message)

    coordinates = None
    if isinstance(yaml_object, CommentedMap | CommentedSeq):
        metadata = (yaml_object.lc.data or {}).get(location_key)
        if metadata is not None:
            if isinstance(yaml_object, CommentedSeq):
                line, column = metadata
                coordinates = ((line + 1, max(1, column - 1)), (line + 1, column))
            else:
                line, column, end_line, end_column = metadata
                coordinates = ((line + 1, column + 1), (end_line + 1, end_column))
    return yaml_object[location_key], coordinates


def get_coordinates_of_a_key_in_a_yaml_object(
    yaml_object: Any, location: tuple[str | int, ...]
) -> YamlLocation | None:
    """Find source coordinates without inventing positions for injected values.

    Args:
        yaml_object: Source document, possibly containing plain Python containers.
        location: Resolved input path (without an absent required field).

    Returns:
        Source coordinates, or None when the target has no YAML metadata.
    """
    coordinates = None
    if (
        not location
        and isinstance(yaml_object, CommentedMap | CommentedSeq)
        and yaml_object.lc.line is not None
        and yaml_object.lc.col is not None
    ):
        point = (yaml_object.lc.line + 1, yaml_object.lc.col + 1)
        return point, point
    if not contains_location(yaml_object, location):
        return None
    for part in location:
        yaml_object, coordinates = get_inner_yaml_object_from_its_key(yaml_object, part)
    return coordinates
