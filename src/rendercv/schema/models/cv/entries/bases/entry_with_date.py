import re
from datetime import date as Date
from typing import Annotated, TypeAlias

import pydantic

from .entry import BaseEntry


def validate_arbitrary_date(date: int | str) -> int | str:
    """Validate date format while allowing flexible user input.

    Why:
        Users enter dates like "Fall 2023" or "2020-09" for events. Strict
        dates (YYYY-MM-DD/YYYY-MM/YYYY) get validated via ISO parsing, while
        custom text passes through for template rendering.

    Args:
        date: Date value to validate.

    Returns:
        Original date if valid.
    """
    date_str = str(date)

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        Date.fromisoformat(date_str)
    elif re.fullmatch(r"\d{4}-\d{2}", date_str):
        Date.fromisoformat(f"{date_str}-01")

    return date


ArbitraryDate: TypeAlias = Annotated[
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
