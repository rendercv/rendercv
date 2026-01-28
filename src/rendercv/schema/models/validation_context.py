import pathlib
from datetime import date as Date
from typing import cast

import pydantic


class ValidationContext(pydantic.BaseModel):
    input_file_path: pathlib.Path | None = None
    current_date: Date | None = None


def get_input_file_path(info: pydantic.ValidationInfo) -> pathlib.Path | None:
    """Extract input file path from validation context.

    Why:
        Relative paths in YAML (like photo references) must resolve relative
        to the input file's directory. Validators access this path via context
        to compute absolute paths during validation.

    Args:
        info: Pydantic validation info containing context.

    Returns:
        Input file path if available, otherwise None.
    """
    if isinstance(info.context, dict):
        context = cast(ValidationContext, info.context["context"])
        if context.input_file_path:
            return context.input_file_path
    return None


def get_current_date(info: pydantic.ValidationInfo) -> Date:
    """Extract current date from validation context or default to today.

    Why:
        Date calculations (like months of experience) must use consistent
        reference dates. Users can override via settings.current_date for
        reproducible builds, otherwise defaults to today.

    Args:
        info: Pydantic validation info containing context.

    Returns:
        Current date from context or Date.today().
    """
    if isinstance(info.context, dict):
        context = cast(ValidationContext, info.context["context"])
        return context.current_date or Date.today()
    return Date.today()
