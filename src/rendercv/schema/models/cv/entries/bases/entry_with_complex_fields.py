import re
from datetime import date as Date
from typing import Annotated, Literal, Self

import pydantic
import pydantic_core

from .....pydantic_error_handling import CustomPydanticErrorTypes
from ....context import get_todays_date
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


def get_date_object(date: str | int, today: Date | None = None) -> Date:
    if isinstance(date, int):
        date_object = Date.fromisoformat(f"{date}-01-01")
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        # Then it is in YYYY-MM-DD format
        date_object = Date.fromisoformat(date)
    elif re.fullmatch(r"\d{4}-\d{2}", date):
        # Then it is in YYYY-MM format
        date_object = Date.fromisoformat(f"{date}-01")
    elif re.fullmatch(r"\d{4}", date):
        # Then it is in YYYY format
        date_object = Date.fromisoformat(f"{date}-01-01")
    elif date == "present":
        if today is None:
            today = Date.today()

        date_object = today
    else:
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "This is not a valid date! Please use either YYYY-MM-DD, YYYY-MM, or"
            " YYYY format.",
            {
                "date": date,
            },
        )

    return date_object


class BaseEntryWithComplexFields(BaseEntryWithDate):
    """Parent class for entry types that uses common fields such as `start_date`,
    `end_date`, `location`, `summary`, and `highlights`. It's not an entry type itself.
    """

    model_config = pydantic.ConfigDict(json_schema_extra={"description": None})

    start_date: ExactDate | None = pydantic.Field(
        default=None,
        description=(
            "The start date. Can be written in YYYY-MM-DD, YYYY-MM, or YYYY format."
        ),
        examples=["2020-09-24", "2020-09", "2020"],
    )
    end_date: ExactDate | Literal["present"] | None = pydantic.Field(
        default=None,
        description=(
            "The end date. Can be written in YYYY-MM-DD, YYYY-MM, or YYYY format. Use"
            ' "present" for ongoing events, or simply omit `end_date` to automatically'
            " indicate the event is ongoing."
        ),
        examples=["2024-05-20", "2024-05", "2024", "present"],
    )
    location: str | None = pydantic.Field(
        default=None,
        examples=["Istanbul, Türkiye", "New York, NY", "Remote"],
    )
    summary: str | None = pydantic.Field(
        default=None,
        examples=[
            "Led a team of 5 engineers to develop innovative solutions.",
            (
                "Completed advanced coursework in machine learning and artificial"
                " intelligence."
            ),
        ],
    )
    highlights: list[str] | None = pydantic.Field(
        default=None,
        description=(
            "A list of bullet points highlighting your key achievements,"
            " responsibilities, or contributions."
        ),
        examples=[
            [
                "Increased system performance by 40% through optimization.",
                "Mentored 3 junior developers and conducted code reviews.",
                "Implemented CI/CD pipeline reducing deployment time by 60%.",
            ]
        ],
    )

    @pydantic.model_validator(mode="after")
    def check_and_adjust_dates(self, info: pydantic.ValidationInfo) -> Self:
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
        elif start_date_is_provided and not end_date_is_provided:
            # If only start_date is provided, assume it is an ongoing event, i.e., the
            # end_date is present:
            self.end_date = "present"

        if self.start_date and self.end_date:
            # Check if the start_date is before the end_date:
            today = get_todays_date(info)
            start_date_object = get_date_object(self.start_date, today)
            end_date_object = get_date_object(self.end_date, today)
            if start_date_object > end_date_object:
                raise pydantic_core.PydanticCustomError(
                    CustomPydanticErrorTypes.other.value,
                    "`start_date` cannot be after `end_date`. The `start_date` is"
                    " {start_date} and the `end_date` is {end_date}.",
                    {
                        "start_date": self.start_date,
                        "end_date": self.end_date,
                    },
                )

        return self
