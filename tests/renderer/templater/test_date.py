from datetime import date as Date

import pytest

from rendercv.renderer.templater.date import (
    compute_time_span_string,
    date_object_to_string,
    format_date_range,
    format_single_date,
)
from rendercv.schema.models.locale.english_locale import EnglishLocale


@pytest.mark.parametrize(
    ("date", "template", "locale_kwargs", "expected"),
    [
        # Default locale with various templates
        (Date(2020, 1, 15), "MONTH_ABBREVIATION YEAR", {}, "Jan 2020"),
        (Date(2020, 6, 1), "MONTH_ABBREVIATION YEAR", {}, "June 2020"),
        (Date(2020, 9, 1), "MONTH_ABBREVIATION YEAR", {}, "Sept 2020"),
        (Date(2020, 12, 1), "MONTH_ABBREVIATION YEAR", {}, "Dec 2020"),
        (Date(2020, 1, 1), "MONTH_NAME", {}, "January"),
        (Date(2020, 9, 1), "MONTH_NAME", {}, "September"),
        (Date(2020, 1, 1), "MONTH", {}, "1"),
        (Date(2020, 12, 1), "MONTH", {}, "12"),
        (Date(2020, 1, 1), "MONTH_IN_TWO_DIGITS", {}, "01"),
        (Date(2020, 12, 1), "MONTH_IN_TWO_DIGITS", {}, "12"),
        (Date(2020, 5, 15), "YEAR", {}, "2020"),
        (Date(1999, 5, 15), "YEAR", {}, "1999"),
        (Date(2020, 5, 15), "YEAR_IN_TWO_DIGITS", {}, "20"),
        (Date(1999, 5, 15), "YEAR_IN_TWO_DIGITS", {}, "99"),
        (Date(2020, 3, 15), "MONTH/YEAR", {}, "3/2020"),
        (
            Date(2020, 3, 15),
            "MONTH_IN_TWO_DIGITS/MONTH_IN_TWO_DIGITS/YEAR",
            {},
            "03/03/2020",
        ),
        (
            Date(2020, 3, 15),
            "MONTH_NAME (MONTH_ABBREVIATION) MONTH, YEAR",
            {},
            "March (Mar) 3, 2020",
        ),
        (Date(2020, 3, 15), "YEAR-MONTH_IN_TWO_DIGITS", {}, "2020-03"),
        # Test DAY and DAY_IN_TWO_DIGITS
        (Date(2020, 12, 5), "MONTH/DAY/YEAR", {}, "12/5/2020"),
        (
            Date(2020, 12, 5),
            "MONTH_IN_TWO_DIGITS/DAY_IN_TWO_DIGITS/YEAR",
            {},
            "12/05/2020",
        ),
        (Date(2020, 1, 9), "MONTH/DAY/YEAR", {}, "1/9/2020"),
        (
            Date(2020, 1, 9),
            "MONTH_IN_TWO_DIGITS/DAY_IN_TWO_DIGITS/YEAR",
            {},
            "01/09/2020",
        ),
        # Custom month abbreviations
        (
            Date(2020, 1, 1),
            "MONTH_ABBREVIATION YEAR",
            {"month_abbreviations": list("ABCDEFGHIJKL")},
            "A 2020",
        ),
        (
            Date(2020, 6, 1),
            "MONTH_ABBREVIATION YEAR",
            {"month_abbreviations": list("ABCDEFGHIJKL")},
            "F 2020",
        ),
        (
            Date(2020, 12, 1),
            "MONTH_ABBREVIATION YEAR",
            {"month_abbreviations": list("ABCDEFGHIJKL")},
            "L 2020",
        ),
        # Custom month names
        (
            Date(2020, 1, 1),
            "MONTH_NAME YEAR",
            {
                "month_names": [
                    "Enero",
                    "Febrero",
                    "Marzo",
                    "Abril",
                    "Mayo",
                    "Junio",
                    "Julio",
                    "Agosto",
                    "Septiembre",
                    "Octubre",
                    "Noviembre",
                    "Diciembre",
                ]
            },
            "Enero 2020",
        ),
        (
            Date(2020, 8, 1),
            "MONTH_NAME YEAR",
            {
                "month_names": [
                    "Enero",
                    "Febrero",
                    "Marzo",
                    "Abril",
                    "Mayo",
                    "Junio",
                    "Julio",
                    "Agosto",
                    "Septiembre",
                    "Octubre",
                    "Noviembre",
                    "Diciembre",
                ]
            },
            "Agosto 2020",
        ),
    ],
)
def test_date_object_to_string(date, template, locale_kwargs, expected):
    result = date_object_to_string(
        date, locale=EnglishLocale(**locale_kwargs), single_date_template=template
    )
    assert result == expected


@pytest.mark.parametrize(
    ("date", "template", "locale_kwargs", "expected"),
    [
        # Various date formats with default template
        ("2020-01-01", "MONTH_ABBREVIATION YEAR", {}, "Jan 2020"),
        ("2020-06-15", "MONTH_ABBREVIATION YEAR", {}, "June 2020"),
        ("2020-09-01", "MONTH_ABBREVIATION YEAR", {}, "Sept 2020"),
        ("2020-12-31", "MONTH_ABBREVIATION YEAR", {}, "Dec 2020"),
        ("2020-01", "MONTH_ABBREVIATION YEAR", {}, "Jan 2020"),
        ("2020-09", "MONTH_ABBREVIATION YEAR", {}, "Sept 2020"),
        (2020, "MONTH_ABBREVIATION YEAR", {}, "2020"),
        (2024, "MONTH_ABBREVIATION YEAR", {}, "2024"),
        ("My Custom Date", "MONTH_ABBREVIATION YEAR", {}, "My Custom Date"),
        (
            "Invalid date format",
            "MONTH_ABBREVIATION YEAR",
            {},
            "Invalid date format",
        ),
        # Custom templates
        ("2020-01-01", "MONTH_NAME", {}, "January"),
        ("2020-09-01", "MONTH_NAME", {}, "September"),
        ("2020-01-01", "MONTH", {}, "1"),
        ("2020-12-01", "MONTH", {}, "12"),
        ("2020-01-01", "MONTH_IN_TWO_DIGITS", {}, "01"),
        ("2020-12-01", "MONTH_IN_TWO_DIGITS", {}, "12"),
        ("2020-05-15", "YEAR", {}, "2020"),
        ("1999-05-15", "YEAR", {}, "1999"),
        ("2020-05-15", "YEAR_IN_TWO_DIGITS", {}, "20"),
        ("1999-05-15", "YEAR_IN_TWO_DIGITS", {}, "99"),
        ("2020-03-15", "MONTH/YEAR", {}, "3/2020"),
        (
            "2020-03-15",
            "MONTH_IN_TWO_DIGITS/MONTH_IN_TWO_DIGITS/YEAR",
            {},
            "03/03/2020",
        ),
        (
            "2020-03-15",
            "MONTH_NAME (MONTH_ABBREVIATION) MONTH, YEAR",
            {},
            "March (Mar) 3, 2020",
        ),
        ("2020-03-15", "YEAR-MONTH_IN_TWO_DIGITS", {}, "2020-03"),
        # Custom locale
        (
            "2020-01-01",
            "MONTH_ABBREVIATION YEAR",
            {"month_abbreviations": list("ABCDEFGHIJKL")},
            "A 2020",
        ),
        (
            "2020-06-01",
            "MONTH_ABBREVIATION YEAR",
            {"month_abbreviations": list("ABCDEFGHIJKL")},
            "F 2020",
        ),
        (
            "2020-12-01",
            "MONTH_ABBREVIATION YEAR",
            {"month_abbreviations": list("ABCDEFGHIJKL")},
            "L 2020",
        ),
    ],
)
def test_format_single_date(date, template, locale_kwargs, expected):
    result = format_single_date(
        date, locale=EnglishLocale(**locale_kwargs), single_date_template=template
    )
    assert result == expected


@pytest.mark.parametrize(
    (
        "start_date",
        "end_date",
        "single_date_template",
        "date_range_template",
        "locale_kwargs",
        "expected",
    ),
    [
        # Standard date ranges
        (
            "2020-01-01",
            "2021-01-01",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "Jan 2020 – Jan 2021",
        ),
        (
            "2020-01-01",
            "2022-01-01",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "Jan 2020 – Jan 2022",
        ),
        (
            "2020-01-01",
            "2021-12-10",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "Jan 2020 – Dec 2021",
        ),
        (
            "2020-01",
            "2021-01",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "Jan 2020 – Jan 2021",
        ),
        (
            "2020-01",
            "2021-02-01",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "Jan 2020 – Feb 2021",
        ),
        (
            "2020-01-01",
            "2021-01",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "Jan 2020 – Jan 2021",
        ),
        (
            "2020-10-10",
            "2020-11-05",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "Oct 2020 – Nov 2020",
        ),
        # Year only ranges
        (
            2020,
            2021,
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "2020 – 2021",
        ),
        (
            "2020-10-10",
            2022,
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "Oct 2020 – 2022",
        ),
        (
            2022,
            "2023-10-10",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "2022 – Oct 2023",
        ),
        # Present as end date
        (
            "2020-02-01",
            "present",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "Feb 2020 – present",
        ),
        (
            "2020-01",
            "present",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "Jan 2020 – present",
        ),
        (
            2020,
            "present",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {},
            "2020 – present",
        ),
        # Custom locale present translation
        (
            "2020-01-01",
            "present",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            {"present": "presente"},
            "Jan 2020 – presente",
        ),
        # Custom single date template
        (
            "2020-03-15",
            "2021-08-20",
            "YEAR-MONTH_IN_TWO_DIGITS",
            "START_DATE / END_DATE",
            {},
            "2020-03 / 2021-08",
        ),
    ],
)
def test_format_date_range(
    start_date,
    end_date,
    single_date_template,
    date_range_template,
    locale_kwargs,
    expected,
):
    result = format_date_range(
        start_date,
        end_date,
        locale=EnglishLocale(**locale_kwargs),
        single_date_template=single_date_template,
        date_range_template=date_range_template,
    )
    assert result == expected


@pytest.mark.parametrize(
    (
        "start_date",
        "end_date",
        "current_date",
        "time_span_template",
        "locale_kwargs",
        "expected",
    ),
    [
        # Year only calculations
        (
            2020,
            2021,
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "1 year",
        ),
        (
            2020,
            2022,
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "2 years",
        ),
        (
            2020,
            2024,
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "4 years",
        ),
        (
            "2020-10-10",
            2022,
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "2 years",
        ),
        (
            2022,
            "2023-10-10",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "1 year",
        ),
        # Years and months
        (
            "2020-01-01",
            "2021-01-01",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "1 year 1 month",
        ),
        (
            "2020-01-01",
            "2022-01-01",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "2 years 1 month",
        ),
        (
            "2020-01",
            "2021-02-01",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "1 year 2 months",
        ),
        (
            "2020-01-01",
            "2023-03-01",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "3 years 3 months",
        ),
        # Months only
        (
            "2020-10-10",
            "2020-11-05",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "1 month",
        ),
        (
            "2020-01-01",
            "2020-03-15",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "3 months",
        ),
        # Years only (no months)
        (
            "2020-01-01",
            "2021-12-10",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "2 years",
        ),
        (
            "2020-02-01",
            "2024-01-01",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "4 years",
        ),
        # Present as end date
        (
            "2020-01-01",
            "present",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "4 years 1 month",
        ),
        (
            "2020-02-01",
            "present",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "4 years",
        ),
        (
            2020,
            "present",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "4 years",
        ),
        # Month overflow handling
        (
            "2020-01-01",
            "2021-01-15",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {},
            "1 year 1 month",
        ),
        # Custom locale translations
        (
            "2020-01-01",
            "2021-02-01",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {"year": "año", "years": "años", "month": "mes", "months": "meses"},
            "1 año 2 meses",
        ),
        (
            2020,
            2022,
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            {"year": "año", "years": "años", "month": "mes", "months": "meses"},
            "2 años",
        ),
        # Custom time span template
        (
            "2020-01-01",
            "2021-02-01",
            Date(2024, 1, 1),
            "HOW_MANY_YEARS YEARS, HOW_MANY_MONTHS MONTHS",
            {},
            "1 year, 2 months",
        ),
    ],
)
def test_compute_time_span_string(
    start_date,
    end_date,
    current_date,
    time_span_template,
    locale_kwargs,
    expected,
):
    result = compute_time_span_string(
        start_date,
        end_date,
        locale=EnglishLocale(**locale_kwargs),
        current_date=current_date,
        time_span_template=time_span_template,
    )
    assert result == expected
