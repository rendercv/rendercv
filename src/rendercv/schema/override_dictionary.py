import copy

from rendercv.exception import RenderCVUserError


def update_value_by_location[T: dict | list](
    dict_or_list: T,
    key: str,
    value: str,
    full_key: str,
) -> T:
    """Navigate nested structure via dotted path and update value.

    Why:
        CLI overrides like `--cv.sections.education.0.institution MIT`
        must modify deeply nested YAML values without requiring users
        to edit files. Recursive traversal handles arbitrary nesting
        with proper index validation and error context. Missing keys are
        added, and so is a list item at the index after the last one.

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
    first_key, separator, remaining_key = key.partition(".")
    previous_key = full_key.removesuffix(key).rstrip(".")

    def updated(child: object) -> object:
        if not separator:
            return value
        if not isinstance(child, (dict, list)):
            message = (
                f"Cannot descend into `{full_key}`: `{first_key}` is not a mapping"
                " or list."
            )
            raise RenderCVUserError(message)
        return update_value_by_location(child, remaining_key, value, full_key)

    if isinstance(dict_or_list, list):
        try:
            index = int(first_key)
        except ValueError as error:
            message = (
                f"`{previous_key}` corresponds to a list, but `{first_key}` is not an"
                " integer."
            )
            raise RenderCVUserError(message) from error
        if not 0 <= index <= len(dict_or_list):
            message = (
                f"Index {index} is out of range for the list `{previous_key}`,"
                f" which has {len(dict_or_list)} items. Use {len(dict_or_list)} to"
                " add an item."
            )
            raise RenderCVUserError(message)
        if index == len(dict_or_list):
            dict_or_list.append(updated({}))
        else:
            dict_or_list[index] = updated(dict_or_list[index])
    elif isinstance(dict_or_list, dict):
        dict_or_list[first_key] = updated(dict_or_list.get(first_key, {}))
    else:
        message = f"Cannot apply `{full_key}` to a value that is not a mapping or list."
        raise RenderCVUserError(message)

    return dict_or_list


def merge_overlay(dictionary: dict, overlay: dict) -> None:
    """Merge an overlay into a dictionary, in place.

    Why:
        An overlay is a part of an input (for example, the private `cv.email` and
        `cv.phone` of a CV that is public with placeholders), so its mappings are
        merged into the input's, and its other values (text, lists) replace the
        input's. Replacement values are copied so later merges or CLI overrides
        cannot mutate an overlay that may be reused for another CV.

    Example:
        ```py
        data = {"cv": {"name": "John Doe", "email": "john@example.com"}}
        merge_overlay(data, {"cv": {"email": "john@private.com"}})
        assert data == {"cv": {"name": "John Doe", "email": "john@private.com"}}
        ```

    Args:
        dictionary: Input to merge into.
        overlay: Overlay to merge.
    """
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(dictionary.get(key), dict):
            merge_overlay(dictionary[key], value)
        else:
            dictionary[key] = copy.deepcopy(value)


def apply_overrides_to_dictionary[T: dict](
    dictionary: T,
    overrides: dict[str, str],
) -> T:
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
