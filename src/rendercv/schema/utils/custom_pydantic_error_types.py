from enum import Enum

__all__ = [
    "CustomPydanticErrorTypes",
]


class CustomPydanticErrorTypes(str, Enum):
    entry_validation = "rendercv_entry_validation_error"
    other = "rendercv_other_error"
