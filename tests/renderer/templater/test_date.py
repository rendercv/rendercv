import calendar
import re
from datetime import date as Date
from datetime import timedelta

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from rendercv.document import build_date_placeholders, date_object_to_string
from rendercv.renderer.templater.date import (
    compute_time_span,
    count_months,
    format_date,
    format_date_range,
    format_single_date,
    get_period,
    get_precision,
    sort_entries,
)
from rendercv.renderer.templater.markup import emit, plain_text
from rendercv.schema.models.cv.entries.bases.entry_with_complex_fields import (
    get_date_object,
)
from rendercv.schema.models.cv.entries.experience import ExperienceEntry
from rendercv.schema.models.cv.entries.normal import NormalEntry
from rendercv.schema.models.locale.english_locale import EnglishLocale
from rendercv.schema.models.locale.locale import locale_adapter


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
                    "DAY_ORDINAL": "15th",
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

    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_always_returns_the_date_placeholders(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert set(result.keys()) == {
            "MONTH_NAME",
            "MONTH_ABBREVIATION",
            "MONTH",
            "MONTH_IN_TWO_DIGITS",
            "DAY",
            "DAY_IN_TWO_DIGITS",
            "DAY_ORDINAL",
            "YEAR",
            "YEAR_IN_TWO_DIGITS",
        }

    @pytest.mark.parametrize(
        ("language", "day", "expected"),
        [
            ("english", 1, "1st"),
            ("english", 2, "2nd"),
            ("english", 3, "3rd"),
            ("english", 4, "4th"),
            ("english", 11, "11th"),
            ("english", 12, "12th"),
            ("english", 13, "13th"),
            ("english", 21, "21st"),
            ("english", 22, "22nd"),
            ("english", 23, "23rd"),
            ("english", 31, "31st"),
            ("french", 1, "1er"),
            ("french", 2, "2"),
            ("german", 2, "2."),
            ("swedish", 22, "22:a"),
            ("swedish", 23, "23:e"),
        ],
    )
    def test_day_ordinal_comes_from_the_locale(self, language, day, expected):
        locale = locale_adapter.validate_python({"language": language})

        result = build_date_placeholders(Date(2025, 1, day), locale=locale)

        assert result["DAY_ORDINAL"] == expected

    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_month_in_range(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert 1 <= int(result["MONTH"]) <= 12

    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_two_digit_variants_always_two_chars(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert len(result["MONTH_IN_TWO_DIGITS"]) == 2
        assert len(result["DAY_IN_TWO_DIGITS"]) == 2

    @given(date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_year_in_two_digits_always_two_chars(self, date: Date) -> None:
        result = build_date_placeholders(date, locale=EnglishLocale())
        assert len(result["YEAR_IN_TWO_DIGITS"]) == 2

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
        date,
        locale=EnglishLocale(**locale_kwargs),
        single_date_template=template,
        output_format="markdown",
    )
    assert plain_text(result) == expected


@pytest.mark.parametrize(
    ("template", "expected"),
    [
        ("MONTH_ABBREVIATION YEAR", "Mar 2023"),
        ("MONTH_ABBREVIATION DAY, YEAR", "Mar 5, 2023"),
        ("YEAR-MONTH_IN_TWO_DIGITS", "2023-03"),
        ("**MONTH_NAME** YEAR", "**March** 2023"),
    ],
)
def test_format_date(template, expected):
    result = format_date(
        Date(2023, 3, 5),
        locale=EnglishLocale(),
        single_date_template=template,
        output_format="markdown",
    )
    assert emit(result, "markdown") == expected


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
        output_format="markdown",
    )
    assert plain_text(result) == expected


class TestComputeTimeSpan:
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
    def test_compute_time_span(
        self,
        start_date,
        end_date,
        current_date,
        time_span_template,
        locale_kwargs,
        expected,
    ):
        result = plain_text(
            compute_time_span(
                start_date,
                end_date,
                locale=EnglishLocale(**locale_kwargs),
                current_date=current_date,
                time_span_template=time_span_template,
                output_format="typst",
            )
        )
        assert result == expected

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
        result = plain_text(
            compute_time_span(
                start_year,
                end_year,
                locale=locale,
                current_date=Date(2025, 1, 1),
                time_span_template="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
                output_format="typst",
            )
        )
        assert locale.month not in result
        assert locale.months not in result

    @given(
        start=valid_date_strings(),
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
        result = plain_text(
            compute_time_span(
                start,
                end_str,
                locale=locale,
                current_date=Date(2025, 1, 1),
                time_span_template="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
                output_format="typst",
            )
        )
        numbers = re.findall(r"\d+", result)
        for n in numbers:
            assert int(n) >= 0

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
        result = plain_text(
            compute_time_span(
                start_year,
                end_year,
                locale=locale,
                current_date=Date(2025, 1, 1),
                time_span_template="HOW_MANY_YEARS YEARS",
                output_format="typst",
            )
        )
        if delta_years == 1:
            assert locale.year in result
            assert locale.years not in result
        elif delta_years > 1:
            assert locale.years in result


class TestGetDateObject:
    @given(date_str=valid_date_strings())
    def test_valid_strings_produce_date_objects(self, date_str: str) -> None:
        result = get_date_object(date_str)
        assert isinstance(result, Date)

    @given(year=st.integers(min_value=1, max_value=9999))
    def test_integer_years_produce_jan_first(self, year: int) -> None:
        result = get_date_object(year)
        assert result == Date(year, 1, 1)

    @given(current_date=st.dates(min_value=Date(1, 1, 1), max_value=Date(9999, 12, 31)))
    def test_present_returns_current_date(self, current_date: Date) -> None:
        assert get_date_object("present", current_date) == current_date

    @given(
        year=st.integers(min_value=1, max_value=9999),
        month=st.integers(min_value=1, max_value=12),
    )
    def test_yyyy_mm_format_sets_day_to_first(self, year: int, month: int) -> None:
        result = get_date_object(f"{year:04d}-{month:02d}")
        assert result.day == 1


@pytest.mark.parametrize(
    ("date", "expected"),
    [
        (2020, "year"),
        ("2020", "year"),
        ("2020-03", "month"),
        ("2020-03-15", "day"),
        ("present", "day"),
    ],
)
def test_get_precision(date, expected):
    assert get_precision(date) == expected


def add_calendar_months(start: Date, months: int) -> Date:
    """Add calendar months, clamping the day to the length of the month."""
    index = start.month - 1 + months
    year, month = start.year + index // 12, index % 12 + 1
    return Date(year, month, min(start.day, calendar.monthrange(year, month)[1]))


class TestCountMonths:
    @pytest.mark.parametrize(
        ("start", "end", "expected"),
        [
            (Date(2021, 2, 1), Date(2021, 3, 31), 2),
            (Date(2021, 3, 1), Date(2021, 4, 30), 2),
            (Date(2021, 1, 1), Date(2021, 1, 31), 1),
            (Date(2021, 1, 15), Date(2021, 2, 14), 1),
            (Date(2021, 1, 15), Date(2021, 2, 15), 2),
            (Date(2020, 1, 1), Date(2021, 1, 1), 13),
            (Date(2021, 1, 31), Date(2021, 2, 28), 2),
        ],
    )
    def test_counts_months_covering_the_days(self, start, end, expected):
        assert count_months(start, end) == expected

    @given(
        start=st.dates(min_value=Date(1900, 1, 1), max_value=Date(2100, 12, 31)),
        days=st.integers(min_value=0, max_value=4000),
    )
    def test_is_the_fewest_calendar_months_reaching_past_the_end(
        self, start: Date, days: int
    ) -> None:
        end = start + timedelta(days=days)
        months = count_months(start, end)

        assert months >= 1
        assert add_calendar_months(start, months) > end
        assert add_calendar_months(start, months - 1) <= end


class TestComputeTimeSpanPrecision:
    @pytest.mark.parametrize(
        ("start_date", "end_date", "expected"),
        [
            ("2021-02", "2021-03", "2 months"),
            ("2021-03", "2021-04", "2 months"),
            ("2020-06", "2023-09", "3 years 4 months"),
            ("2020-06", "present", "4 years 8 months"),
            ("2020-01", "2020-12", "1 year"),
            (2020, 2020, "1 year"),
        ],
    )
    def test_months_cover_whole_months(self, start_date, end_date, expected):
        result = compute_time_span(
            start_date,
            end_date,
            locale=EnglishLocale(),
            current_date=Date(2025, 1, 1),
            time_span_template="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
            output_format="typst",
        )

        assert plain_text(result) == expected


@pytest.mark.parametrize(
    ("date", "expected"),
    [
        (2020, (Date(2020, 1, 1), Date(2020, 12, 31))),
        ("2020", (Date(2020, 1, 1), Date(2020, 12, 31))),
        ("2020-02", (Date(2020, 2, 1), Date(2020, 2, 29))),
        ("2020-02-10", (Date(2020, 2, 10), Date(2020, 2, 10))),
        ("present", (Date(2025, 1, 1), Date(2025, 1, 1))),
    ],
)
def test_get_period(date, expected):
    assert get_period(date, Date(2025, 1, 1)) == expected


class TestSortEntries:
    entries = (
        ExperienceEntry(
            company="A", position="P", start_date="2015-01", end_date="2016-01"
        ),
        ExperienceEntry(company="B", position="P"),
        ExperienceEntry(
            company="C", position="P", start_date="2021-01", end_date="present"
        ),
        ExperienceEntry(company="D", position="P", start_date=2019, end_date=2020),
        ExperienceEntry(
            company="E", position="P", start_date="2020-03", end_date="2020-06"
        ),
        ExperienceEntry(company="F", position="P", date="2018-05"),
        ExperienceEntry(company="G", position="P", date="Fall 2017"),
        ExperienceEntry(company="H", position="P", date="2018-05"),
    )

    @pytest.mark.parametrize(
        ("order", "expected"),
        [
            # The year 2020 ends after June 2020, and undated entries come last:
            ("reverse-chronological", "CDEFHABG"),
            ("chronological", "AFHEDCBG"),
        ],
    )
    def test_orders_entries_by_their_ends_then_starts(self, order, expected):
        result = sort_entries(self.entries, order=order, current_date=Date(2025, 1, 1))

        assert "".join(entry.company for entry in result) == expected

    def test_keeps_text_entries_in_their_order(self):
        result = sort_entries(
            ["b", "a"], order="chronological", current_date=Date(2025, 1, 1)
        )

        assert result == ["b", "a"]


def test_present_is_a_date_when_sorting_single_dates():
    old = NormalEntry(name="Old", date="2020-01")
    now = NormalEntry(name="Now", date="present")
    assert sort_entries(
        [old, now], order="reverse-chronological", current_date=Date(2025, 1, 1)
    ) == [now, old]
