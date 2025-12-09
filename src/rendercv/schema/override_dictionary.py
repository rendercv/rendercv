import copy
from typing import overload

from rendercv.exception import RenderCVUserError


@overload
def update_value_by_location(
    dict_or_list: dict,
    key: str,
    value: str,
    full_key: str,
) -> dict: ...
@overload
def update_value_by_location(
    dict_or_list: list,
    key: str,
    value: str,
    full_key: str,
) -> list: ...
def update_value_by_location(
    dict_or_list: dict | list,
    key: str,
    value: str,
    full_key: str,
) -> dict | list:
    """Navigate nested structure via dotted path and update value.

    Why:
        CLI overrides like `--cv.sections.education.0.institution MIT`
        must modify deeply nested YAML values without requiring users
        to edit files. Recursive traversal handles arbitrary nesting
        with proper index validation and error context.

    Example:
        ```py
        data = {"cv": {"sections": {"education": [{"institution": "A"}]}}}
        result = update_value_by_location(
            data,
            "cv.sections.education.0.institution",
            "MIT",
            "cv.sections.education.0.institution",
        )
        assert result["cv"]["sections"]["education"][0]["institution"] == "MIT"
        ```

    Args:
        dict_or_list: Target structure to modify.
        key: Remaining path segments to traverse.
        value: Replacement value.
        full_key: Original full path for error messages.

    Returns:
        Modified structure.
    """
    keys = key.split(".")
    first_key: str | int = keys[0]
    remaining_key = ".".join(keys[1:])

    # Calculate the parent path for error messages
    processed_count = len(full_key.split(".")) - len(key.split("."))
    previous_key = (
        ".".join(full_key.split(".")[:processed_count]) if processed_count > 0 else ""
    )

    if isinstance(dict_or_list, list):
        try:
            first_key = int(first_key)
        except ValueError as e:
            message = (
                f"`{previous_key}` corresponds to a list, but `{keys[0]}` is not an"
                " integer."
            )
            raise RenderCVUserError(message) from e

        if first_key >= len(dict_or_list):
            message = (
                f"Index {first_key} is out of range for the list `{previous_key}`."
            )
            raise RenderCVUserError(message)
    elif not isinstance(dict_or_list, dict):
        message = (
            f"It seems like there's something wrong with `{full_key}`, but we don't"
            " know what it is."
        )
        raise RenderCVUserError(message)

    if len(keys) == 1:
        new_value = value
    else:
        new_value = update_value_by_location(
            dict_or_list[first_key],  # pyright: ignore[reportArgumentType, reportCallIssue]
            remaining_key,
            value,
            full_key=full_key,
        )

    dict_or_list[first_key] = new_value  # pyright: ignore[reportArgumentType, reportCallIssue]

    return dict_or_list


def apply_overrides_to_dictionary(
    dictionary: dict,
    overrides: dict[str, str],
) -> dict:
    """Apply multiple CLI overrides to dictionary.

    Why:
        Users need to test configuration changes without editing YAML files.
        Batching overrides ensures all modifications happen before validation,
        preventing partial invalid states.

    Example:
        ```py
        data = {"cv": {"name": "John", "phone": "123"}}
        overrides = {"cv.name": "Jane", "cv.phone": "456"}
        result = apply_overrides_to_dictionary(data, overrides)
        assert result["cv"]["name"] == "Jane"
        ```

    Args:
        dictionary: Source dictionary to modify.
        overrides: Map of dotted paths to new values.

    Returns:
        Deep copy with all overrides applied.
    """
    new_dictionary = copy.deepcopy(dictionary)
    for key, value in overrides.items():
        new_dictionary = update_value_by_location(new_dictionary, key, value, key)

    return new_dictionary
