import pydantic

from .entry import BaseEntry

type ArbitraryDate = int | str


class BaseEntryWithDate(BaseEntry):
    """Parent class for entry types that uses the `date` field. It's not an entry type
    itself.
    """

    model_config = pydantic.ConfigDict(json_schema_extra={"description": None})

    date: ArbitraryDate | None = pydantic.Field(
        default=None,
        description=(
            "The date of this event. Can be in YYYY-MM-DD, YYYY-MM, or YYYY format, or"
            " any custom text like 'Fall 2023' or 'Summer 2020'. Use this for single-day"
            " or imprecise dates. For events with a duration, use `start_date` and"
            " `end_date` instead."
        ),
        examples=["2020-09-24", "2020-09", "2020", "Fall 2023", "Summer 2020"],
    )
