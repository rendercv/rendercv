import calendar
import re
from datetime import date as Date

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from rendercv.renderer.templater.date import (
    build_date_placeholders,
    compute_time_span_string,
    date_object_to_string,
    format_date_range,
    format_single_date,
)
from rendercv.schema.models.cv.entries.bases.entry_with_complex_fields import (
    get_date_object,
)
from rendercv.schema.models.locale.english_locale import EnglishLocale


@st.composite
def valid_date_strings(draw: st.DrawFn) -> str:
    """Generate date strings in YYYY-MM-DD, YYYY-MM, or YYYY format."""
    year = draw(st.integers(min_value=1, max_value=9999))
    fmt = draw(st.sampled_from(["year", "year_month", "year_month_day"]))
    if fmt == "year":
        return f"{year:04d}"
    month = draw(st.integers(min_value=1, max_value=12))
    if fmt == "year_month":
        return f"{year:04d}-{month:02d}"
    max_day = calendar.monthrange(year, month)[1]
    day = draw(st.integers(min_value=1, max_value=max_day))
    return f"{year:04d}-{month:02d}-{day:02d}"


class TestBuildDatePlaceholders:
    @pytest.mark.parametrize(
        ("date", "locale_kwargs", "expected_subset"),
        [
            (
                Date(2025, 3, 15),
                {},
                {
                    "MONTH_NAME": "March",
                    "MONTH_ABBREVIATION": "Mar",
                    "MONTH": "3",
                    "MONTH_IN_TWO_DIGITS": "03",
                    "DAY": "15",
                    "DAY_IN_TWO_DIGITS": "15",
                    "YEAR": "2025",
                    "YEAR_IN_TWO_DIGITS": "25",
                },
            ),
            # Single-digit day padding
            (
                Date(2020, 1, 5),
                {},
                {"DAY": "5", "DAY_IN_TWO_DIGITS": "05"},
            ),
            # Custom locale propagates
            (
                Date(2020, 1, 10),
                {"month_abbreviations": list("ABCDEFGHIJKL")},
                {"MONTH_ABBREVIATION": "A", "DAY": "10"},
            ),
        ],
    )
    def test_build_date_placeholders(self, date, locale_kwargs, expected_subset):
        result = build_date_placeholders(date, locale=EnglishLocale(**locale_kwargs))
        for key, value in expected_subset.items():
            assert result[key] == value

    @settings(deadline=None)
    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_always_returns_8_keys(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert len(result) == 8
        expected_keys = {
            "MONTH_NAME",
            "MONTH_ABBREVIATION",
            "MONTH",
            "MONTH_IN_TWO_DIGITS",
            "DAY",
            "DAY_IN_TWO_DIGITS",
            "YEAR",
            "YEAR_IN_TWO_DIGITS",
        }
        assert set(result.keys()) == expected_keys

    @settings(deadline=None)
    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_month_in_range(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert 1 <= int(result["MONTH"]) <= 12

    @settings(deadline=None)
    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_two_digit_variants_always_two_chars(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert len(result["MONTH_IN_TWO_DIGITS"]) == 2
        assert len(result["DAY_IN_TWO_DIGITS"]) == 2

    @settings(deadline=None)
    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_year_in_two_digits_always_two_chars(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert len(result["YEAR_IN_TWO_DIGITS"]) == 2

    @settings(deadline=None)
    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_month_name_from_locale(self, date: Date) -> None:
        locale = EnglishLocale()
        result = build_date_placeholders(date, locale=locale)
        assert result["MONTH_NAME"] == locale.month_names[date.month - 1]


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
        (Date(2020, 3, 5), "DAY", {}, "5"),
        (Date(2020, 3, 15), "DAY", {}, "15"),
        (Date(2020, 3, 5), "DAY_IN_TWO_DIGITS", {}, "05"),
        (Date(2020, 3, 15), "DAY_IN_TWO_DIGITS", {}, "15"),
        (Date(2020, 12, 13), "MONTH/DAY/YEAR", {}, "12/13/2020"),
        (
            Date(2020, 3, 5),
            "YEAR-MONTH_IN_TWO_DIGITS-DAY_IN_TWO_DIGITS",
            {},
            "2020-03-05",
        ),
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
        ("2020-03-05", "DAY", {}, "5"),
        ("2020-03-15", "DAY", {}, "15"),
        ("2020-03-05", "DAY_IN_TWO_DIGITS", {}, "05"),
        ("2020-03-15", "DAY_IN_TWO_DIGITS", {}, "15"),
        ("2020-12-13", "MONTH/DAY/YEAR", {}, "12/13/2020"),
        ("2020-03-05", "YEAR-MONTH_IN_TWO_DIGITS-DAY_IN_TWO_DIGITS", {}, "2020-03-05"),
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
        "compact_date_ranges_removing_start_year",
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
            False,
            {},
            "Jan 2020 – Jan 2021",
        ),
        (
            "2020-01-01",
            "2022-01-01",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "Jan 2020 – Jan 2022",
        ),
        (
            "2020-01-01",
            "2021-12-10",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "Jan 2020 – Dec 2021",
        ),
        (
            "2020-01",
            "2021-01",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "Jan 2020 – Jan 2021",
        ),
        (
            "2020-01",
            "2021-02-01",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "Jan 2020 – Feb 2021",
        ),
        (
            "2020-01-01",
            "2021-01",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "Jan 2020 – Jan 2021",
        ),
        (
            "2020-10-10",
            "2020-11-05",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "Oct 2020 – Nov 2020",
        ),
        # Year only ranges
        (
            2020,
            2021,
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "2020 – 2021",
        ),
        (
            "2020-10-10",
            2022,
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "Oct 2020 – 2022",
        ),
        (
            2022,
            "2023-10-10",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "2022 – Oct 2023",
        ),
        # Present as end date
        (
            "2020-02-01",
            "present",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "Feb 2020 – present",
        ),
        (
            "2020-01",
            "present",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "Jan 2020 – present",
        ),
        (
            2020,
            "present",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {},
            "2020 – present",
        ),
        # Compact date ranges
        (
            "2020-01",
            "2020-05",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            True,
            {},
            "Jan – May 2020",
        ),
        (
            "2020-01",
            "present",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            True,
            {},
            "Jan 2020 – present",
        ),
        # Custom locale present translation
        (
            "2020-01-01",
            "present",
            "MONTH_ABBREVIATION YEAR",
            "START_DATE – END_DATE",
            False,
            {"present": "presente"},
            "Jan 2020 – presente",
        ),
        # Custom single date template
        (
            "2020-03-15",
            "2021-08-20",
            "YEAR-MONTH_IN_TWO_DIGITS",
            "START_DATE / END_DATE",
            False,
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
    compact_date_ranges_removing_start_year,
    locale_kwargs,
    expected,
):
    result = format_date_range(
        start_date,
        end_date,
        locale=EnglishLocale(**locale_kwargs),
        single_date_template=single_date_template,
        date_range_template=date_range_template,
        compact_date_ranges_removing_start_year=compact_date_ranges_removing_start_year,
    )
    assert result == expected


class TestComputeTimeSpanString:
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
        self,
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

    @settings(deadline=None)
    @given(
        start_year=st.integers(min_value=1900, max_value=2100),
        delta_years=st.integers(min_value=0, max_value=50),
    )
    def test_year_only_inputs_produce_year_only_output(
        self, start_year: int, delta_years: int
    ) -> None:
        end_year = start_year + delta_years
        assume(end_year <= 9999)
        locale = EnglishLocale()
        result = compute_time_span_string(
            start_year,
            end_year,
            locale=locale,
            current_date=Date(2025, 1, 1),
            time_span_template="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
        )
        assert locale.month not in result
        assert locale.months not in result

    @settings(deadline=None)
    @given(
        start=valid_date_strings(),  # ty: ignore[missing-argument]
        delta_days=st.integers(min_value=0, max_value=36500),
    )
    def test_non_negative_duration(self, start: str, delta_days: int) -> None:
        start_date = get_date_object(start)
        end_date = Date.fromordinal(
            min(start_date.toordinal() + delta_days, Date(9999, 12, 31).toordinal())
        )
        assume(end_date >= start_date)
        end_str = end_date.isoformat()
        locale = EnglishLocale()
        result = compute_time_span_string(
            start,
            end_str,
            locale=locale,
            current_date=Date(2025, 1, 1),
            time_span_template="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
        )
        numbers = re.findall(r"\d+", result)
        for n in numbers:
            assert int(n) >= 0

    @settings(deadline=None)
    @given(
        start_year=st.integers(min_value=1900, max_value=2050),
        delta_years=st.integers(min_value=1, max_value=50),
    )
    def test_singular_plural_correctness(
        self, start_year: int, delta_years: int
    ) -> None:
        end_year = start_year + delta_years
        assume(end_year <= 9999)
        locale = EnglishLocale()
        result = compute_time_span_string(
            start_year,
            end_year,
            locale=locale,
            current_date=Date(2025, 1, 1),
            time_span_template="HOW_MANY_YEARS YEARS",
        )
        if delta_years == 1:
            assert locale.year in result
            assert locale.years not in result
        elif delta_years > 1:
            assert locale.years in result


class TestGetDateObject:
    @settings(deadline=None)
    @given(date_str=valid_date_strings())  # ty: ignore[missing-argument]
    def test_valid_strings_produce_date_objects(self, date_str: str) -> None:
        result = get_date_object(date_str)
        assert isinstance(result, Date)

    @settings(deadline=None)
    @given(year=st.integers(min_value=1, max_value=9999))
    def test_integer_years_produce_jan_first(self, year: int) -> None:
        result = get_date_object(year)
        assert result == Date(year, 1, 1)

    @settings(deadline=None)
    @given(current_date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_present_returns_current_date(self, current_date: Date) -> None:
        assert get_date_object("present", current_date) == current_date

    @settings(deadline=None)
    @given(
        year=st.integers(min_value=1, max_value=9999),
        month=st.integers(min_value=1, max_value=12),
    )
    def test_yyyy_mm_format_sets_day_to_first(self, year: int, month: int) -> None:
        result = get_date_object(f"{year:04d}-{month:02d}")
        assert result.day == 1
