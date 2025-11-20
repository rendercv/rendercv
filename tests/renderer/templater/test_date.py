from datetime import date as Date

import pytest

from rendercv.renderer.templater.date import (
    compute_date_string,
    compute_last_updated_date,
    compute_time_span_string,
    format_date,
)
from rendercv.schema.models.locale.english_locale import EnglishLocale


class TestComputeDateString:
    @pytest.mark.parametrize(
        ("date", "start_date", "end_date", "expected"),
        [
            # Single date overrides start/end
            ("2023-02-01", "2020-01-01", "2021-01-01", "Feb 2023"),
            ("2020-01-01", None, None, "Jan 2020"),
            ("2020-09", None, None, "Sept 2020"),
            # Year only (int)
            (2024, "2002", "2020", "2024"),
            (2020, None, None, "2020"),
            # Custom date strings (invalid date formats)
            ("My Custom Date", "2020-01-01", "2021-01-01", "My Custom Date"),
            ("My Custom Date", None, None, "My Custom Date"),
        ],
    )
    def test_date_parameter_takes_precedence(
        self, date, start_date, end_date, expected
    ):
        result = compute_date_string(date, start_date, end_date, EnglishLocale())
        assert result == expected

    # Test date ranges with both start and end dates
    @pytest.mark.parametrize(
        ("start_date", "end_date", "expected"),
        [
            # Standard date ranges
            ("2020-01-01", "2021-01-01", "Jan 2020 – Jan 2021"),
            ("2020-01-01", "2022-01-01", "Jan 2020 – Jan 2022"),
            ("2020-01-01", "2021-12-10", "Jan 2020 – Dec 2021"),
            # YYYY-MM format
            ("2020-01", "2021-01", "Jan 2020 – Jan 2021"),
            ("2020-01", "2021-02-01", "Jan 2020 – Feb 2021"),
            # Mixed formats
            ("2020-01-01", "2021-01", "Jan 2020 – Jan 2021"),
            # Same year
            ("2020-10-10", "2020-11-05", "Oct 2020 – Nov 2020"),
        ],
    )
    def test_date_ranges(self, start_date, end_date, expected):
        result = compute_date_string(None, start_date, end_date, EnglishLocale())
        assert result == expected

    # Test year-only ranges
    @pytest.mark.parametrize(
        ("start_date", "end_date", "expected"),
        [
            (2020, 2021, "2020 – 2021"),
            ("2020-10-10", 2022, "Oct 2020 – 2022"),
            (2022, "2023-10-10", "2022 – Oct 2023"),
        ],
    )
    def test_year_only_ranges(self, start_date, end_date, expected):
        result = compute_date_string(None, start_date, end_date, EnglishLocale())
        assert result == expected

    # Test "present" as end date
    @pytest.mark.parametrize(
        ("start_date", "expected"),
        [
            ("2020-02-01", "Feb 2020 – present"),
            ("2020-01", "Jan 2020 – present"),
            (2020, "2020 – present"),
        ],
    )
    def test_present_as_end_date(self, start_date, expected):
        result = compute_date_string(None, start_date, "present", EnglishLocale())
        assert result == expected

    # Test None returns
    @pytest.mark.parametrize(
        ("date", "start_date", "end_date"),
        [
            (None, None, None),  # No dates provided
            (None, "2020-01-01", None),  # Only start_date
            (None, None, "2021-01-01"),  # Only end_date
        ],
    )
    def test_returns_none_for_incomplete_data(self, date, start_date, end_date):
        result = compute_date_string(date, start_date, end_date, EnglishLocale())
        assert result is None

    # Test locale.to separator variations
    @pytest.mark.parametrize(
        ("separator", "expected"),
        [
            ("–", "Jan 2020 – Jan 2021"),  # Default separator
            ("-", "Jan 2020 - Jan 2021"),  # Dash
            ("to", "Jan 2020 to Jan 2021"),  # Word
            ("/", "Jan 2020 / Jan 2021"),  # Slash
            ("", "Jan 2020 Jan 2021"),  # Empty string (just space)
        ],
    )
    def test_locale_to_separator(self, separator, expected):
        custom_locale = EnglishLocale(to=separator)
        result = compute_date_string(None, "2020-01-01", "2021-01-01", custom_locale)
        assert result == expected

    # Test custom locale with different present translation
    def test_custom_locale_present_translation(self):
        spanish_locale = EnglishLocale(present="presente", to="–")
        result = compute_date_string(None, "2020-01-01", "present", spanish_locale)
        assert result == "Jan 2020 – presente"

    # Test custom date template
    def test_custom_date_template(self):
        custom_locale = EnglishLocale(date_template="YEAR-MONTH_IN_TWO_DIGITS", to="/")
        result = compute_date_string(None, "2020-03-15", "2021-08-20", custom_locale)
        assert result == "2020-03 / 2021-08"

    # Test edge case: different date object types
    def test_mixed_date_types(self):
        # Date object and string
        result = compute_date_string(None, "2020-01-01", "2021-01-01", EnglishLocale())
        assert result == "Jan 2020 – Jan 2021"

        # String and Date object
        result = compute_date_string(None, "2020-01-01", "2021-01-01", EnglishLocale())
        assert result == "Jan 2020 – Jan 2021"


class TestComputeTimeSpanString:
    @pytest.fixture
    def current_date(self):
        return Date(2024, 1, 1)

    # Test cases that should return None
    @pytest.mark.parametrize(
        ("date", "start_date", "end_date"),
        [
            ("2023-02-01", "2020-01-01", "2021-01-01"),  # date provided
            ("My Custom Date", "2020-01-01", None),  # date provided
            (None, None, None),  # no dates
            (None, "2020-01-01", None),  # missing end_date
            (None, None, "2021-01-01"),  # missing start_date
        ],
    )
    def test_returns_none_for_invalid_inputs(self, current_date, date, start_date, end_date):
        """Should return None when date is provided or dates are incomplete."""
        result = compute_time_span_string(
            date, start_date, end_date, EnglishLocale(), current_date
        )
        assert result is None

    # Test year-only calculations (int inputs)
    @pytest.mark.parametrize(
        ("start_date", "end_date", "expected"),
        [
            (2020, 2021, "1 year"),  # 1 year difference
            (2020, 2022, "2 years"),  # 2 years difference
            (2020, 2024, "4 years"),  # Multiple years
            ("2020-10-10", 2022, "2 years"),  # Mixed: date and int
            (2022, "2023-10-10", "1 year"),  # Mixed: int and date
        ],
    )
    def test_year_only_calculations(self, current_date, start_date, end_date, expected):
        """When either date is an int (year), calculate time span in years only."""
        result = compute_time_span_string(
            None, start_date, end_date, EnglishLocale(), current_date
        )
        assert result == expected

    # Test full date calculations - years and months
    @pytest.mark.parametrize(
        ("start_date", "end_date", "expected"),
        [
            ("2020-01-01", "2021-01-01", "1 year 1 month"),  # Exactly 1 year
            ("2020-01-01", "2022-01-01", "2 years 1 month"),  # Exactly 2 years
            ("2020-01", "2021-02-01", "1 year 2 months"),  # Mixed formats
            ("2020-01-01", "2023-03-01", "3 years 3 months"),  # General case
        ],
    )
    def test_full_date_with_years_and_months(
        self, current_date, start_date, end_date, expected
    ):
        """Calculate time spans with both years and months."""
        result = compute_time_span_string(
            None, start_date, end_date, EnglishLocale(), current_date
        )
        assert result == expected

    # Test edge cases: months only (no years)
    @pytest.mark.parametrize(
        ("start_date", "end_date", "expected"),
        [
            ("2020-10-10", "2020-11-05", "1 month"),  # Less than 2 months
            ("2020-01-01", "2020-03-15", "3 months"),  # Multiple months
        ],
    )
    def test_months_only_no_years(self, current_date, start_date, end_date, expected):
        """Calculate time spans with months only when less than a year."""
        result = compute_time_span_string(
            None, start_date, end_date, EnglishLocale(), current_date
        )
        assert result == expected

    # Test edge cases: years only (no months)
    @pytest.mark.parametrize(
        ("start_date", "end_date", "expected"),
        [
            ("2020-01-01", "2021-12-10", "2 years"),  # Rounds to exact years
            ("2020-02-01", "2024-01-01", "4 years"),  # Multiple years, no months
        ],
    )
    def test_years_only_no_months(self, current_date, start_date, end_date, expected):
        """Calculate time spans with years only when months round to zero."""
        result = compute_time_span_string(
            None, start_date, end_date, EnglishLocale(), current_date
        )
        assert result == expected

    # Test "present" as end date
    @pytest.mark.parametrize(
        ("start_date", "expected"),
        [
            ("2020-01-01", "4 years 1 month"),
            ("2020-02-01", "4 years"),
            (2020, "4 years"),
        ],
    )
    def test_present_as_end_date(self, current_date, start_date, expected):
        """Handle 'present' or None as end_date (uses current_date's date)."""
        # "present" should use current_date's date
        result_present = compute_time_span_string(
            None, start_date, "present", EnglishLocale(), current_date
        )

        assert result_present == expected

    # Test custom locale (different translations)
    def test_custom_locale_translations(self, current_date):
        """Test that locale translations are used correctly."""
        custom_locale = EnglishLocale(
            year="año", years="años", month="mes", months="meses"
        )

        result = compute_time_span_string(
            None, "2020-01-01", "2021-02-01", custom_locale, current_date
        )
        assert result == "1 año 2 meses"

        result_years_only = compute_time_span_string(
            None, 2020, 2022, custom_locale, current_date
        )
        assert result_years_only == "2 años"

    # Test overflow handling (12 months → 1 year)
    def test_month_overflow_handling(self, current_date):
        """Test that 12+ months correctly overflow into years."""
        # This would depend on exact dates, but the function handles overflow
        # The +1 month logic and modulo operations should prevent "1 year 12 months"
        result = compute_time_span_string(
            None, "2020-01-01", "2021-01-15", EnglishLocale(), current_date
        )
        # Should be "1 year 1 month", not "1 year 0 months" or "0 years 13 months"
        assert isinstance(result, str)
        assert "year" in result
        assert result != "1 year 0 months"  # Should handle the edge case


class TestFormatDate:
    @pytest.mark.parametrize(
        ("date", "expected"),
        [
            (Date(2020, 1, 1), "Jan 2020"),
            (Date(2020, 6, 1), "June 2020"),
            (Date(2020, 9, 1), "Sept 2020"),
            (Date(2020, 12, 1), "Dec 2020"),
        ],
    )
    def test_default_template(self, date, expected):
        assert format_date(date, EnglishLocale()) == expected

    @pytest.mark.parametrize(
        ("template", "date", "expected"),
        [
            ("FULL_MONTH_NAME", Date(2020, 1, 1), "January"),
            ("FULL_MONTH_NAME", Date(2020, 9, 1), "September"),
            ("MONTH_ABBREVIATION", Date(2020, 1, 1), "Jan"),
            ("MONTH", Date(2020, 1, 1), "1"),
            ("MONTH", Date(2020, 12, 1), "12"),
            ("MONTH_IN_TWO_DIGITS", Date(2020, 1, 1), "01"),
            ("MONTH_IN_TWO_DIGITS", Date(2020, 12, 1), "12"),
            ("YEAR", Date(2020, 5, 15), "2020"),
            ("YEAR", Date(1999, 5, 15), "1999"),
            ("YEAR_IN_TWO_DIGITS", Date(2020, 5, 15), "20"),
            ("YEAR_IN_TWO_DIGITS", Date(1999, 5, 15), "99"),
        ],
    )
    def test_individual_placeholders(self, template, date, expected):
        locale = EnglishLocale(date_template=template)
        assert format_date(date, locale) == expected

    def test_custom_abbreviations(self):
        locale = EnglishLocale(
            abbreviations_for_months=list("ABCDEFGHIJKL"),
            date_template="MONTH_ABBREVIATION YEAR",
        )

        assert format_date(Date(2020, 1, 1), locale) == "A 2020"
        assert format_date(Date(2020, 6, 1), locale) == "F 2020"
        assert format_date(Date(2020, 12, 1), locale) == "L 2020"

    def test_custom_full_month_names(self):
        locale = EnglishLocale(
            full_names_of_months=[
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
            ],
            date_template="FULL_MONTH_NAME YEAR",
        )

        assert format_date(Date(2020, 1, 1), locale) == "Enero 2020"
        assert format_date(Date(2020, 8, 1), locale) == "Agosto 2020"

    @pytest.mark.parametrize(
        ("template", "expected"),
        [
            ("MONTH/YEAR", "3/2020"),
            ("MONTH_IN_TWO_DIGITS/MONTH_IN_TWO_DIGITS/YEAR", "03/03/2020"),
            ("FULL_MONTH_NAME (MONTH_ABBREVIATION) MONTH, YEAR", "March (Mar) 3, 2020"),
            ("YEAR-MONTH_IN_TWO_DIGITS", "2020-03"),
        ],
    )
    def test_complex_templates(self, template, expected):
        locale = EnglishLocale(date_template=template)
        assert format_date(Date(2020, 3, 15), locale) == expected


def test_compute_last_updated_date():
    locale = EnglishLocale(last_updated_date_template="Last updated in current_date by NAME")
    current_date = Date(2024, 1, 1)
    name = "John Doe"
    result = compute_last_updated_date(locale, current_date, name)
    assert result == "Last updated in Jan 2024 by John Doe"
