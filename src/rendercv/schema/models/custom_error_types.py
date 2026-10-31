from enum import StrEnum

import pydantic
from pydantic_core import core_schema


class CustomPydanticErrorTypes(StrEnum):
    entry_validation = "rendercv_entry_validation_error"
    other = "rendercv_other_error"


def invalid_input(error_type: str, message: str) -> "pydantic.GetPydanticSchema":
    """Give a semantic type one diagnostic for all its validation failures.

    Args:
        error_type: Machine-readable domain error code.
        message: Explanation of the type's accepted values.

    Returns:
        Annotated metadata preserving validation and JSON schema behavior.
    """
    return pydantic.GetPydanticSchema(
        lambda source, handler: core_schema.custom_error_schema(
            handler(source), custom_error_type=error_type, custom_error_message=message
        )
    )
