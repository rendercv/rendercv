import re
from datetime import date as Date
from typing import Annotated

import pydantic

from .entry import BaseEntry


def validate_arbitrary_date(date: int | str) -> int | str:
    date_str = str(date)

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        Date.fromisoformat(date_str)
    elif re.fullmatch(r"\d{4}-\d{2}", date_str):
        Date.fromisoformat(f"{date_str}-01")

    return date


type ArbitraryDate = Annotated[
    int | str, pydantic.AfterValidator(validate_arbitrary_date)
]


class BaseEntryWithDate(BaseEntry):
    """Base for entries with a single date. For ranges, use BaseEntryWithComplexFields."""

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
