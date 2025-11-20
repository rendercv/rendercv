from enum import Enum


class CustomPydanticErrorTypes(str, Enum):
    entry_validation = "rendercv_entry_validation_error"
    other = "rendercv_other_error"
