import re
from datetime import date as Date
from typing import Annotated

import pydantic

from .entry import BaseEntry


def validate_arbitrary_date(date: int | str) -> int | str:
    """Validate an arbitrary date.

    Args:
        date: The date to validate.

    Returns:
        The validated date.
    """
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(date)):
        # Then it is in YYYY-MM-DD format
        Date.fromisoformat(str(date))
    elif re.fullmatch(r"\d{4}-\d{2}", str(date)):
        # Then it is in YYYY-MM format
        Date.fromisoformat(f"{date}-01")

    return date


type ArbitraryDate = Annotated[
    int | str, pydantic.AfterValidator(validate_arbitrary_date)
]


class BaseEntryWithDate(BaseEntry):
    """Parent class for entry types that uses the `date` field. It's not an entry type
    itself.
    """

    model_config = pydantic.ConfigDict(json_schema_extra={"description": None})

    date: ArbitraryDate | None = pydantic.Field(
        default=None,
        description=(
            "The date of this event. Can be in YYYY-MM-DD, YYYY-MM, or YYYY format, or"
            " any custom text like 'Fall 2023' or 'Summer 2020'. Use this for"
            " single-day or imprecise dates. For events with a duration, use"
            " `start_date` and `end_date` instead."
        ),
        examples=["2020-09-24", "2020-09", "2020", "Fall 2023", "Summer 2020"],
    )
