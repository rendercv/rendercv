from typing import Annotated, Literal

import annotated_types as at
import pydantic
import pydantic_extra_types.language_code

from ..base import BaseModelWithoutExtraKeys


class Locale(BaseModelWithoutExtraKeys):
    language: pydantic_extra_types.language_code.LanguageAlpha2 = pydantic.Field(
        default=pydantic_extra_types.language_code.LanguageAlpha2("en"),
        title="Language",
        description=(
            "The language as an ISO 639 alpha-2 code. It is used for hyphenation"
            " patterns. The default value is 'en'."
        ),
    )
    phone_number_format: Literal["national", "international", "E164"] | None = (
        pydantic.Field(
            default="national",
            title="Phone Number Format",
            description=(
                "If 'national', phone numbers are formatted without the country code."
                " If 'international', phone numbers are formatted with the country"
                " code. The default value is 'national'."
            ),
        )
    )
    page_numbering_template: str = pydantic.Field(
        default="NAME - Page PAGE_NUMBER of TOTAL_PAGES",
        title="Page Numbering Template",
        description=(
            "The template of the page numbering. The following placeholders can be"
            " used:\n- NAME: The name of the person\n- PAGE_NUMBER: The current page"
            " number\n- TOTAL_PAGES: The total number of pages\n- TODAY: Today's date"
            ' with `locale.date_template`\nThe default value is "NAME -'
            ' Page PAGE_NUMBER of TOTAL_PAGES".'
        ),
    )
    last_updated_date_template: str = pydantic.Field(
        default="Last updated in TODAY",
        title="Last Updated Date Template",
        description=(
            "The template of the last updated date. The following placeholders can be"
            " used:\n- TODAY: Today's date with `locale.date_template`\nThe"
            ' default value is "Last updated in TODAY".'
        ),
    )
    date_template: str | None = pydantic.Field(
        default="MONTH_ABBREVIATION YEAR",
        title="Date Template",
        description=(
            "The template of the date. The following placeholders can be"
            " used:\n-FULL_MONTH_NAME: Full name of the month\n- MONTH_ABBREVIATION:"
            " Abbreviation of the month\n- MONTH: Month as a number\n-"
            " MONTH_IN_TWO_DIGITS: Month as a number in two digits\n- YEAR: Year as a"
            " number\n- YEAR_IN_TWO_DIGITS: Year as a number in two digits\nThe"
            ' default value is "MONTH_ABBREVIATION YEAR".'
        ),
    )
    month: str | None = pydantic.Field(
        default="month",
        title='Translation of "month"',
        description='Translation of the word "month" in the locale.',
    )
    months: str | None = pydantic.Field(
        default="months",
        title='Translation of "months"',
        description='Translation of the word "months" in the locale.',
    )
    year: str | None = pydantic.Field(
        default="year",
        title='Translation of "year"',
        description='Translation of the word "year" in the locale.',
    )
    years: str | None = pydantic.Field(
        default="years",
        title='Translation of "years"',
        description='Translation of the word "years" in the locale.',
    )
    present: str | None = pydantic.Field(
        default="present",
        title='Translation of "present"',
        description='Translation of the word "present" in the locale.',
    )
    to: str | None = pydantic.Field(
        default="–",  # NOQA: RUF001
        title='Translation of "to"',
        description=(
            "The word or character used to indicate a range in the locale (e.g.,"
            ' "2020 - 2021").'
        ),
    )
    abbreviations_for_months: (
        Annotated[list[str], at.Len(min_length=12, max_length=12)] | None
    ) = pydantic.Field(
        # Month abbreviations are taken from
        # https://web.library.yale.edu/cataloging/months:
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
        title="Abbreviations of Months",
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
        title="Full Names of Months",
        description="Full names of the months in the locale.",
    )

    @pydantic.field_validator(
        "month",
        "months",
        "year",
        "years",
        "present",
        "abbreviations_for_months",
        "to",
        "full_names_of_months",
        "phone_number_format",
        "date_template",
    )
    @classmethod
    def update_locale(cls, value: str, info: pydantic.ValidationInfo) -> str:
        """Update the `locale` dictionary."""
        if value:
            locale[info.field_name] = value  # type: ignore

        return value


# The dictionary below will be overwritten by Locale class, which will contain
# month names, month abbreviations, and other locale-specific strings.
locale: dict[str, str | list[str]] = {}

# Initialize even if the RenderCVDataModel is not called (to make `format_date` function
# work on its own):
Locale()
