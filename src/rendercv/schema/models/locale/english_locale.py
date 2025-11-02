from typing import Annotated, Literal

import annotated_types as at
import pydantic

from ..base import BaseModelWithoutExtraKeys


class EnglishLocale(BaseModelWithoutExtraKeys):
    """Base class for all locale variants.

    All fields are required to ensure that each locale implementation provides
    complete translations and formatting.
    """

    language: Literal["english"] = pydantic.Field(
        default="english",
        description="The language of the locale. The default value is 'english'.",
    )
    phone_number_format: Literal["national", "international", "E164"] | None = (
        pydantic.Field(
            default="national",
            description=(
                "If 'national', phone numbers are formatted without the country code."
                " If 'international', phone numbers are formatted with the country"
                " code. The default value is 'national'."
            ),
        )
    )
    page_numbering_template: str = pydantic.Field(
        default="NAME - Page PAGE_NUMBER of TOTAL_PAGES",
        description=(
            "The template of the page numbering at the bottom of the page."
            "\n\nThe following placeholders can be used:"
            "\n- NAME: The name of the person"
            "\n- PAGE_NUMBER: The current page number"
            "\n- TOTAL_PAGES: The total number of pages"
            "\n- TODAY: Today's date with `locale.date_template`"
        ),
    )
    last_updated_date_template: str = pydantic.Field(
        default="Last updated in TODAY",
        description=(
            "The template of the last updated date at the top right corner of the"
            " page.\n\nThe following placeholders can be used:"
            "\n- NAME: The name of the person"
            "\n- PAGE_NUMBER: The current page number"
            "\n- TOTAL_PAGES: The total number of pages"
            "\n- TODAY: Today's date with `locale.date_template`"
        ),
    )
    date_template: str | None = pydantic.Field(
        default="MONTH_ABBREVIATION YEAR",
        description=(
            "The template of the date.\n\nThe following placeholders can be used:"
            "\n- FULL_MONTH_NAME: Full name of the month (e.g., January)"
            "\n- MONTH_ABBREVIATION: Abbreviation of the month (e.g., Jan)"
            "\n- MONTH: Month as a number (e.g., 1)"
            "\n- MONTH_IN_TWO_DIGITS: Month as a number in two digits (e.g., 01)"
            "\n- YEAR: Year as a number (e.g., 2024)"
            "\n- YEAR_IN_TWO_DIGITS: Year as a number in two digits (e.g., 24)"
        ),
    )
    month: str | None = pydantic.Field(
        default="month",
        description='Translation of the word "month" in the locale.',
    )
    months: str | None = pydantic.Field(
        default="months",
        description='Translation of the word "months" in the locale.',
    )
    year: str | None = pydantic.Field(
        default="year",
        description='Translation of the word "year" in the locale.',
    )
    years: str | None = pydantic.Field(
        default="years",
        description='Translation of the word "years" in the locale.',
    )
    present: str | None = pydantic.Field(
        default="present",
        description='Translation of the word "present" in the locale.',
    )
    to: str | None = pydantic.Field(
        default="–",
        description=(
            "The word or character used to indicate a range in the locale (e.g.,"
            ' "2020 - 2021").'
        ),
    )
    # From https://web.library.yale.edu/cataloging/months
    abbreviations_for_months: (
        Annotated[list[str], at.Len(min_length=12, max_length=12)] | None
    ) = pydantic.Field(
        default=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "June",
            "July",
            "Aug",
            "Sept",
            "Oct",
            "Nov",
            "Dec",
        ],
        description="Abbreviations of the months in the locale.",
    )
    full_names_of_months: (
        Annotated[list[str], at.Len(min_length=12, max_length=12)] | None
    ) = pydantic.Field(
        default=[
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
        description="Full names of the months in the locale.",
    )
