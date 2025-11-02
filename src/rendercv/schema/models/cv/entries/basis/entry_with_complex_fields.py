from typing import Annotated, Literal, Self

import pydantic

from .entry_with_date import BaseEntryWithDate

type ExactDate = (
    Annotated[
        str,
        pydantic.Field(
            pattern=r"\d{4}-\d{2}(-\d{2})?",
        ),
    ]
    | int
)


class BaseEntryWithComplexFields(BaseEntryWithDate):
    """Parent class for entry types that uses common fields such as `start_date`,
    `end_date`, `location`, `summary`, and `highlights`. It's not an entry type itself.
    """

    model_config = pydantic.ConfigDict(json_schema_extra={"description": None})

    start_date: ExactDate | None = pydantic.Field(
        default=None,
        description="Can be written in the formats YYYY-MM-DD, YYYY-MM, or YYYY.",
        examples=["2020-09-24"],
    )
    end_date: ExactDate | Literal["present"] | None = pydantic.Field(
        default=None,
        description=(
            "Can be written in the formats YYYY-MM-DD, YYYY-MM, or YYYY. If the event"
            ' is ongoing, write "present" or provide only the `start_date`.'
        ),
        examples=["2020-09-24", "present"],
    )
    location: str | None = pydantic.Field(
        default=None,
        examples=["Istanbul, Türkiye"],
    )
    summary: str | None = pydantic.Field(
        default=None,
        examples=["Did this and that."],
    )
    highlights: list[str] | None = pydantic.Field(
        default=None,
        examples=[["Did this.", "Did that."]],
    )

    @pydantic.model_validator(mode="after")
    def check_and_adjust_dates(self) -> Self:
        date_is_provided = self.date is not None
        start_date_is_provided = self.start_date is not None
        end_date_is_provided = self.end_date is not None

        if date_is_provided:
            # If only date is provided, ignore start_date and end_date:
            self.start_date = None
            self.end_date = None
        elif not start_date_is_provided and end_date_is_provided:
            # If only end_date is provided, assume it is a one-day event and act like
            # only the date is provided:
            self.date = self.end_date
            self.start_date = None
            self.end_date = None
        elif start_date_is_provided and self.end_date is None:
            # If only start_date is provided, assume it is an ongoing event, i.e., the
            # end_date is present:
            self.end_date = "present"

        return self
