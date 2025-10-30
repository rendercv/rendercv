import re
from datetime import date as Date
from typing import Annotated, Literal

import pydantic


def get_date_input() -> Date:
    """Return the date input.

    Returns:
        The date input.
    """
    return Date.today()


def get_date_object(date: str | int) -> Date:
    """Parse a date string in YYYY-MM-DD, YYYY-MM, or YYYY format and return a
    `datetime.date` object. This function is used throughout the validation process of
    the data models.

    Args:
        date: The date string to parse.

    Returns:
        The parsed date.
    """
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
        date_object = get_date_input()
    else:
        message = (
            "This is not a valid date! Please use either YYYY-MM-DD, YYYY-MM, or"
            " YYYY format."
        )
        raise ValueError(message)

    return date_object


def validate_date_field(date: int | str | None) -> int | str | None:
    """Check if the `date` field is provided correctly.

    Args:
        date: The date to validate.

    Returns:
        The validated date.
    """
    date_is_provided = date is not None

    if date_is_provided:
        if isinstance(date, str):
            if re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", date):
                # Then it is in YYYY-MM-DD or YYYY-MM format
                # Check if it is a valid date:
                get_date_object(date)
            elif re.fullmatch(r"\d{4}", date):
                # Then it is in YYYY format, so, convert it to an integer:

                # This is not required for start_date and end_date because they
                # can't be casted into a general string. For date, this needs to
                # be done manually, because it can be a general string.
                date = int(date)

        elif isinstance(date, Date):
            # Pydantic parses YYYY-MM-DD dates as datetime.date objects. We need to
            # convert them to strings because that is how RenderCV uses them.
            date = date.isoformat()

    return date


def validate_start_and_end_date_fields(
    date: str | Date,
) -> str:
    """Check if the `start_date` and `end_date` fields are provided correctly.

    Args:
        date: The date to validate.

    Returns:
        The validated date.
    """
    date_is_provided = date is not None

    if date_is_provided:
        if isinstance(date, Date):
            # Pydantic parses YYYY-MM-DD dates as datetime.date objects. We need to
            # convert them to strings because that is how RenderCV uses them.
            date = date.isoformat()

        elif date != "present":
            # Validate the date:
            get_date_object(date)

    return date



# See https://docs.pydantic.dev/2.7/concepts/types/#custom-types and
# https://docs.pydantic.dev/2.7/concepts/validators/#annotated-validators
# for more information about custom types.

# ExactDate that accepts only strings in YYYY-MM-DD or YYYY-MM format:
type ExactDate = Annotated[
    str,
    pydantic.Field(
        pattern=r"\d{4}-\d{2}(-\d{2})?",
    ),
]

# ArbitraryDate that accepts either an integer or a string, but it is validated with
# `validate_date_field` function:
type ArbitraryDate = Annotated[
    int | str | None,
    pydantic.BeforeValidator(validate_date_field),
]

# StartDate that accepts either an integer or an ExactDate, but it is validated with
# `validate_start_and_end_date_fields` function:
type StartDate = Annotated[
    int | ExactDate | None,
    pydantic.BeforeValidator(validate_start_and_end_date_fields),
]

# EndDate that accepts either an integer, the string "present", or an ExactDate, but it
# is validated with `validate_start_and_end_date_fields` function:
type EndDate = Annotated[
    Literal["present"] | int | ExactDate | None,
    pydantic.BeforeValidator(validate_start_and_end_date_fields),
]
