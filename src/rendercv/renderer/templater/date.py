from datetime import date as Date

from rendercv.schema.models.cv.entries.basis.entry_with_complex_fields import (
    BaseEntryWithComplexFields,
    get_date_object,
)
from rendercv.schema.models.cv.entries.basis.entry_with_date import BaseEntryWithDate
from rendercv.schema.models.cv.section import Entry
from rendercv.schema.models.locale.locale import Locale


def compute_date_string(
    entry: Entry,
    locale: Locale,
) -> str | None:
    if not isinstance(entry, BaseEntryWithDate | BaseEntryWithComplexFields):
        return None

    if entry.date is not None:
        if isinstance(entry.date, int):
            # Only year is provided
            date_string = str(entry.date)
        else:
            try:
                date_object = get_date_object(entry.date)
                date_string = format_date(date_object, locale)
            except ValueError:
                # Then it is a custom date string (e.g., "My Custom Date")
                date_string = str(entry.date)

    elif isinstance(entry, BaseEntryWithComplexFields):
        if entry.start_date is not None and entry.end_date is not None:
            if isinstance(entry.start_date, int):
                # Then it means only the year is provided
                start_date = str(entry.start_date)
            else:
                # Then it means start_date is either in YYYY-MM-DD or YYYY-MM format
                date_object = get_date_object(entry.start_date)
                start_date = format_date(date_object, locale)

            if entry.end_date == "present":
                end_date = locale.present
            elif isinstance(entry.end_date, int):
                # Then it means only the year is provided
                end_date = str(entry.end_date)
            else:
                # Then it means end_date is either in YYYY-MM-DD or YYYY-MM format
                date_object = get_date_object(entry.end_date)
                end_date = format_date(date_object, locale)

            date_string = f"{start_date} {locale.to} {end_date}"
        else:
            date_string = None

    else:
        date_string = None

    return date_string


def format_date(date: Date, locale: Locale) -> str:
    """Formats a `Date` object to a string in the following format: "Jan 2021". The
    month names are taken from the `locale` dictionary from the
    `rendercv.data_models.models` module.

    Example:
        ```python
        format_date(Date(2024, 5, 1))
        ```
        will return

        `"May 2024"`

    Args:
        date: The date to format.
        date_template: The template of the date string. If not provided, the default date
            style from the `locale` dictionary will be used.

    Returns:
        The formatted date.
    """
    full_month_names = locale.full_names_of_months
    short_month_names = locale.abbreviations_for_months

    month = int(date.strftime("%m"))
    year = date.strftime(format="%Y")

    placeholders = {
        "FULL_MONTH_NAME": full_month_names[month - 1],
        "MONTH_ABBREVIATION": short_month_names[month - 1],
        "MONTH_IN_TWO_DIGITS": f"{month:02d}",
        "YEAR_IN_TWO_DIGITS": str(year[-2:]),
        "MONTH": str(month),
        "YEAR": str(year),
    }
    formatted_date = locale.date_template
    for placeholder, value in placeholders.items():
        formatted_date = formatted_date.replace(placeholder, value)

    return formatted_date
