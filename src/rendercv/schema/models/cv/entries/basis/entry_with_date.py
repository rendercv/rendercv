import pydantic

from ....primitive_types.date import ArbitraryDate
from .entry import Entry


class EntryWithDate(Entry):
    """Parent class for entry types that uses the `date` field. It's not an entry type
    itself.
    """

    model_config = pydantic.ConfigDict(json_schema_extra={"description": None})

    date: ArbitraryDate = pydantic.Field(
        default=None,
        description=(
            "Can be written in the formats YYYY-MM-DD, YYYY-MM, or YYYY, or as an"
            " arbitrary string such as 'Fall 2023.'"
        ),
        examples=["2020-09-24", "Fall 2023"],
    )
