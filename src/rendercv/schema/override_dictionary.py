import copy
from typing import overload


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
    """Set or update a value in a dictionary for the given key. For example, a key can
    be `cv.sections.education.3.institution` and the value can be "Bogazici University".

    Args:
        dictionary: The dictionary to set or update the value.
        key: The key to set or update the value.
        value: The value to set or update.
        sub_dictionary: The sub dictionary to set or update the value. This is used for
            recursive calls. Defaults to None.
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
            raise ValueError(message) from e

        if first_key >= len(dict_or_list):
            message = (
                f"Index {first_key} is out of range for the list `{previous_key}`."
            )
            raise IndexError(message)
    elif not isinstance(dict_or_list, dict):
        message = f"It seems like there's something wrong with {full_key}."
        raise ValueError(message)

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
    new_dictionary = copy.deepcopy(dictionary)
    for key, value in overrides.items():
        new_dictionary = update_value_by_location(new_dictionary, key, value, key)

    return new_dictionary
