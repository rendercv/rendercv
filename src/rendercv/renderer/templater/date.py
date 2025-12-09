from datetime import date as Date

from rendercv.exception import RenderCVInternalError
from rendercv.schema.models.cv.entries.bases.entry_with_complex_fields import (
    get_date_object,
)
from rendercv.schema.models.locale.locale import Locale

from .string_processor import substitute_placeholders


def date_object_to_string(
    date: Date, *, locale: Locale, single_date_template: str
) -> str:
    """Convert date object to localized string using template placeholders.

    Why:
        Date display varies by locale and user preference. Template-based
        formatting allows MONTH_ABBREVIATION YEAR or MONTH_NAME, YEAR without
        hardcoding formats for each language.

    Example:
        ```py
        result = date_object_to_string(
            Date(2025, 3, 15),
            locale=english_locale,
            single_date_template="MONTH_ABBREVIATION YEAR",
        )
        # Returns: "Mar 2025"
        ```

    Args:
        date: Date to format.
        locale: Locale providing month names and abbreviations.
        single_date_template: Template with date placeholders.

    Returns:
        Formatted date string with placeholders substituted.
    """
    month_names = locale.month_names
    month_abbreviations = locale.month_abbreviations

    month = int(date.strftime("%m"))
    year = int(date.strftime(format="%Y"))

    placeholders: dict[str, str] = {
        "MONTH_NAME": month_names[month - 1],
        "MONTH_ABBREVIATION": month_abbreviations[month - 1],
        "MONTH": str(month),
        "MONTH_IN_TWO_DIGITS": f"{month:02d}",
        "YEAR": str(year),
        "YEAR_IN_TWO_DIGITS": str(year)[-2:],
    }

    return substitute_placeholders(single_date_template, placeholders)


def format_date_range(
    start_date: str | int,
    end_date: str | int,
    *,
    locale: Locale,
    single_date_template: str,
    date_range_template: str,
) -> str:
    """Format date range with localized start and end dates.

    Why:
        CV entries use date ranges for employment and education. Users provide
        dates as year-only integers, YYYY-MM strings, YYYY-MM-DD strings, or
        "present". Unified formatting handles all input types consistently.

    Example:
        ```py
        result = format_date_range(
            "2020-06",
            "present",
            locale=english_locale,
            single_date_template="MONTH_ABBREVIATION YEAR",
            date_range_template="START_DATE to END_DATE",
        )
        # Returns: "Jun 2020 to present"
        ```

    Args:
        start_date: Start date as integer year or ISO date string.
        end_date: End date as integer year, ISO date string, or "present".
        locale: Locale providing month names and present translation.
        single_date_template: Template for formatting individual dates.
        date_range_template: Template combining start and end dates.

    Returns:
        Formatted date range string.
    """
    if isinstance(start_date, int):
        # Then it means only the year is provided
        start_date = str(start_date)
    else:
        # Then it means start_date is either in YYYY-MM-DD or YYYY-MM format
        date_object = get_date_object(start_date)
        start_date = date_object_to_string(
            date_object, locale=locale, single_date_template=single_date_template
        )

    if end_date == "present":
        end_date = locale.present
    elif isinstance(end_date, int):
        # Then it means only the year is provided
        end_date = str(end_date)
    else:
        # Then it means end_date is either in YYYY-MM-DD or YYYY-MM format
        date_object = get_date_object(end_date)
        end_date = date_object_to_string(
            date_object, locale=locale, single_date_template=single_date_template
        )

    placeholders: dict[str, str] = {
        "START_DATE": start_date,
        "END_DATE": end_date,
    }

    return substitute_placeholders(date_range_template, placeholders)


def format_single_date(
    date: str | int, *, locale: Locale, single_date_template: str
) -> str:
    """Format single date with locale-aware template or pass through custom strings.

    Why:
        Publications and certifications use single dates rather than ranges.
        Custom date strings like "Spring 2024" need preservation while standard
        dates require localized formatting.

    Example:
        ```py
        # Standard date formatting
        result = format_single_date(
            "2024-03", locale=english_locale, single_date_template="MONTH_NAME YEAR"
        )
        # Returns: "March 2024"

        # Custom string pass-through
        result = format_single_date(
            "Spring 2024", locale=english_locale, single_date_template="MONTH_NAME YEAR"
        )
        # Returns: "Spring 2024"
        ```

    Args:
        date: Date as integer year, ISO date string, "present", or custom text.
        locale: Locale providing present translation.
        single_date_template: Template for formatting standard dates.

    Returns:
        Formatted date string or original custom text.
    """
    if isinstance(date, int):
        # Only year is provided
        date_string = str(date)
    elif date == "present":
        date_string = locale.present
    else:
        try:
            date_object = get_date_object(date)
            date_string = date_object_to_string(
                date_object, locale=locale, single_date_template=single_date_template
            )
        except RenderCVInternalError:
            # Then it is a custom date string (e.g., "My Custom Date")
            date_string = str(date)

    return date_string


def compute_time_span_string(
    start_date: str | int,
    end_date: str | int,
    *,
    locale: Locale,
    current_date: Date,
    time_span_template: str,
) -> str:
    """Calculate and format duration between dates with localized units.

    Why:
        CV readers need quick understanding of experience length. Automatic
        calculation shows "2 years 3 months" or "1 year" based on date
        precision, with proper singular/plural forms per locale.

    Example:
        ```py
        result = compute_time_span_string(
            "2020-06",
            "2023-09",
            locale=english_locale,
            current_date=Date(2025, 1, 1),
            time_span_template="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
        )
        # Returns: "3 years 4 months"
        ```

    Args:
        start_date: Start date as integer year or ISO date string.
        end_date: End date as integer year, ISO date string, or "present".
        locale: Locale providing year/month singular/plural forms.
        current_date: Reference date for "present" calculation.
        time_span_template: Template for formatting duration output.

    Returns:
        Formatted time span string with years and months.
    """
    if isinstance(start_date, int) or isinstance(end_date, int):
        # Then it means one of the dates is year, so time span cannot be more
        # specific than years.
        start_year = get_date_object(start_date, current_date).year
        end_year = get_date_object(end_date, current_date).year

        time_span_in_years = end_year - start_year

        if time_span_in_years < 2:
            how_many_years = "1"
            locale_years = locale.year
        else:
            how_many_years = str(time_span_in_years)
            locale_years = locale.years

        placeholders: dict[str, str] = {
            "HOW_MANY_YEARS": how_many_years,
            "YEARS": locale_years,
            "HOW_MANY_MONTHS": "",
            "MONTHS": "",
        }

        return substitute_placeholders(time_span_template, placeholders)

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
        how_many_years = ""
        locale_years = ""
    elif how_many_years == 1:
        how_many_years = "1"
        locale_years = locale.year
    else:
        how_many_years = str(how_many_years)
        locale_years = locale.years

    # Format the number of months between start_date and end_date:
    if how_many_months == 0:
        how_many_months = ""
        locale_months = ""
    elif how_many_months == 1:
        how_many_months = "1"
        locale_months = locale.month
    else:
        how_many_months = str(how_many_months)
        locale_months = locale.months

    placeholders = {
        "HOW_MANY_YEARS": how_many_years,
        "YEARS": locale_years,
        "HOW_MANY_MONTHS": how_many_months,
        "MONTHS": locale_months,
    }
    return substitute_placeholders(time_span_template, placeholders)
