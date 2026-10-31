import re
from datetime import date as Date
from typing import Annotated

import pydantic
from pydantic_core import PydanticCustomError

from .entry import BaseEntry


def validate_arbitrary_date(date: int | str) -> int | str:
    """Validate date format while allowing flexible user input.

    Why:
        Users enter dates like "Fall 2023" or "2020-09" for events. Strict
        dates (YYYY-MM-DD/YYYY-MM/YYYY) get validated via ISO parsing, while
        custom text passes through for template rendering. Invalid calendar
        components produce domain errors independently of Python's error wording.

    Args:
        date: Date value to validate.

    Returns:
        Original date if valid.
    """
    date_str = str(date)

    if re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", date_str):
        parts = [int(part) for part in date_str.split("-")]
        year, month = parts[:2]
        try:
            Date.fromisoformat(date_str if len(parts) == 3 else f"{date_str}-01")
        except ValueError as error:
            if not date_str.isascii():
                message = "Use ASCII digits in YYYY-MM-DD or YYYY-MM format."
            elif not 1 <= year <= 9999:
                message = "The year must be between 1 and 9999."
            elif not 1 <= month <= 12:
                message = "The month must be between 1 and 12."
            else:
                message = "The day is out of range for the month."
            raise PydanticCustomError("rendercv_calendar_date", message) from error

    return date


type ArbitraryDate = Annotated[
    int | str, pydantic.AfterValidator(validate_arbitrary_date)
]


class BaseEntryWithDate(BaseEntry):
    model_config = pydantic.ConfigDict(json_schema_extra={"description": None})

    date: ArbitraryDate | None = pydantic.Field(
        default=None,
        description=(
            "The date of this event in YYYY-MM-DD, YYYY-MM, or YYYY format, or any"
            " custom text like 'Fall 2023'. Use this for single-day or imprecise dates."
            " For date ranges, use `start_date` and `end_date` instead."
        ),
        examples=["2020-09-24", "2020-09", "2020", "Fall 2023", "Summer 2020"],
    )
