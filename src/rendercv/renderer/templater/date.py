from datetime import date as Date

from rendercv.schema.models.cv.entries.basis.entry_with_complex_fields import (
    BaseEntryWithComplexFields,
    get_date_object,
)
from rendercv.schema.models.cv.entries.basis.entry_with_date import BaseEntryWithDate
from rendercv.schema.models.cv.section import Entry
from rendercv.schema.models.locale.locale import Locale

from .regex import build_keyword_matcher_pattern


def compute_date_string(
    entry: Entry,
    locale: Locale,
) -> str | None:
    if isinstance(entry, BaseEntryWithDate) and entry.date is not None:
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

    elif (
        isinstance(entry, BaseEntryWithComplexFields)
        and entry.start_date is not None
        and entry.end_date is not None
    ):
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

        if locale.to:
            date_string = f"{start_date} {locale.to} {end_date}"
        else:
            date_string = f"{start_date} {end_date}"

    else:
        date_string = None

    return date_string


def compute_last_updated_date(locale: Locale, today: Date, name: str | None) -> str:
    placeholders: dict[str, str] = {
        "TODAY": format_date(today, locale),
        "NAME": name or "",
    }
    pattern = build_keyword_matcher_pattern(frozenset(placeholders.keys()))
    return pattern.sub(
        lambda match: placeholders[match.group(0)], locale.last_updated_date_template
    )


def format_date(date: Date, locale: Locale) -> str:
    """Formats a `Date` object to a string based on the `locale`.

    Example:
        ```python
        format_date(Date(2024, 5, 1), EnglishLocale())
        ```

        will return

        `"May 2024"`

    Args:
        date: The date to format.
        locale: The locale to use for formatting the date.

    Returns:
        The formatted date.
    """
    full_month_names = locale.full_names_of_months
    short_month_names = locale.abbreviations_for_months

    month = int(date.strftime("%m"))
    year = int(date.strftime(format="%Y"))

    placeholders: dict[str, str] = {
        "FULL_MONTH_NAME": full_month_names[month - 1],
        "MONTH_ABBREVIATION": short_month_names[month - 1],
        "MONTH": str(month),
        "MONTH_IN_TWO_DIGITS": f"{month:02d}",
        "YEAR": str(year),
        "YEAR_IN_TWO_DIGITS": str(year)[-2:],
    }

    pattern = build_keyword_matcher_pattern(frozenset(placeholders.keys()))

    return pattern.sub(lambda match: placeholders[match.group(0)], locale.date_template)
