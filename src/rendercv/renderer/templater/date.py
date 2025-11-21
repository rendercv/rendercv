from datetime import date as Date

from rendercv.schema.models.cv.entries.bases.entry_with_complex_fields import (
    get_date_object,
)
from rendercv.schema.models.locale.locale import Locale

from .string_processor import substitute_placeholders


def compute_date_string(
    date: str | int | None,
    start_date: str | int | None,
    end_date: str | int | None,
    locale: Locale,
) -> str | None:
    if date is not None:
        if isinstance(date, int):
            # Only year is provided
            date_string = str(date)
        else:
            try:
                date_object = get_date_object(date)
                date_string = format_date(date_object, locale)
            except ValueError:
                # Then it is a custom date string (e.g., "My Custom Date")
                date_string = str(date)

    elif start_date is not None and end_date is not None:
        if isinstance(start_date, int):
            # Then it means only the year is provided
            start_date = str(start_date)
        else:
            # Then it means start_date is either in YYYY-MM-DD or YYYY-MM format
            date_object = get_date_object(start_date)
            start_date = format_date(date_object, locale)

        if end_date == "present":
            end_date = locale.present
        elif isinstance(end_date, int):
            # Then it means only the year is provided
            end_date = str(end_date)
        else:
            # Then it means end_date is either in YYYY-MM-DD or YYYY-MM format
            date_object = get_date_object(end_date)
            end_date = format_date(date_object, locale)

        if locale.to:
            date_string = f"{start_date} {locale.to} {end_date}"
        else:
            date_string = f"{start_date} {end_date}"

    else:
        date_string = None

    return date_string


def compute_time_span_string(
    date: str | int | None,
    start_date: str | int | None,
    end_date: str | int | None,
    locale: Locale,
    current_date: Date,
) -> str | None:
    if date is not None or start_date is None or end_date is None:
        # If only the date is provided, the time span is irrelevant. So, return an
        # empty string.

        # If neither start_date nor end_date is provided, return an empty string.
        return None

    if isinstance(start_date, int) or isinstance(end_date, int):
        # Then it means one of the dates is year, so time span cannot be more
        # specific than years.
        start_year = get_date_object(start_date, current_date).year
        end_year = get_date_object(end_date, current_date).year

        time_span_in_years = end_year - start_year

        if time_span_in_years < 2:
            time_span_string = f"1 {locale.year}"
        else:
            time_span_string = f"{time_span_in_years} {locale.years}"

        return time_span_string

    # Then it means both start_date and end_date are in YYYY-MM-DD or YYYY-MM
    # format.
    end_date_object = get_date_object(end_date, current_date)
    start_date_object = get_date_object(start_date, current_date)

    # Calculate the number of days between start_date and end_date:
    timespan_in_days = (end_date_object - start_date_object).days

    # Calculate the number of years and months between start_date and end_date:
    how_many_years = timespan_in_days // 365
    how_many_months = (timespan_in_days % 365) // 30 + 1
    # Deal with overflow (prevent rounding to 1 year 12 months, etc.)
    how_many_years += how_many_months // 12
    how_many_months %= 12

    # Format the number of years and months between start_date and end_date:
    if how_many_years == 0:
        how_many_years_string = None
    elif how_many_years == 1:
        how_many_years_string = f"1 {locale.year}"
    else:
        how_many_years_string = f"{how_many_years} {locale.years}"

    # Format the number of months between start_date and end_date:
    if how_many_months == 1 or (how_many_years_string is None and how_many_months == 0):
        how_many_months_string = f"1 {locale.month}"
    elif how_many_months == 0:
        how_many_months_string = None
    else:
        how_many_months_string = f"{how_many_months} {locale.months}"

    # Combine howManyYearsString and howManyMonthsString:
    if how_many_years_string is None and how_many_months_string is not None:
        time_span_string = how_many_months_string
    elif how_many_months_string is None and how_many_years_string is not None:
        time_span_string = how_many_years_string
    elif how_many_years_string is not None and how_many_months_string is not None:
        time_span_string = f"{how_many_years_string} {how_many_months_string}"
    else:
        message = "The time span is not valid!"
        raise ValueError(message)

    return time_span_string.strip()


def format_date(date: Date, locale: Locale) -> str:
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

    return substitute_placeholders(locale.date_template, placeholders)


def compute_last_updated_date(
    locale: Locale, current_date: Date, name: str | None
) -> str:
    placeholders: dict[str, str] = {
        "current_date": format_date(current_date, locale),
        "NAME": name or "",
    }
    return substitute_placeholders(locale.last_updated_date_template, placeholders)
