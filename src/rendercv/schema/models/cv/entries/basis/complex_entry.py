from typing import Self

import pydantic

from ....primitive_types.date import EndDate, StartDate, get_date_object
from .entry_with_date import EntryWithDate


class ComplexEntry(EntryWithDate):
    start_date: StartDate = pydantic.Field(
        default=None,
        description="Can be written in the formats YYYY-MM-DD, YYYY-MM, or YYYY.",
        examples=["2020-09-24"],
    )
    end_date: EndDate = pydantic.Field(
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
        date = self.date
        start_date = self.start_date
        end_date = self.end_date

        date_is_provided = date is not None
        start_date_is_provided = start_date is not None
        end_date_is_provided = end_date is not None

        if date_is_provided:
            # If only date is provided, ignore start_date and end_date:
            start_date = None
            end_date = None
        elif not start_date_is_provided and end_date_is_provided:
            # If only end_date is provided, assume it is a one-day event and act like
            # only the date is provided:
            date = end_date
            start_date = None
            end_date = None
        elif start_date_is_provided:
            start_date_object = get_date_object(start_date)
            if not end_date_is_provided:
                # If only start_date is provided, assume it is an ongoing event, i.e.,
                # the end_date is present:
                end_date = "present"

            if end_date != "present":
                end_date_object = get_date_object(end_date)

                if start_date_object > end_date_object:
                    message = '"start_date" can not be after "end_date"!'

                    raise ValueError(
                        message,
                        "start_date",  # This is the location of the error
                        str(start_date),  # This is value of the error
                    )

        self.start_date, self.end_date, self.date = start_date, end_date, date
        return self
