from enum import StrEnum


class CustomPydanticErrorTypes(StrEnum):
    entry_validation = "rendercv_entry_validation_error"
    other = "rendercv_other_error"
