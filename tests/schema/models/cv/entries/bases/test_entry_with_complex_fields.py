from datetime import date as Date

import pydantic
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rendercv.exception import RenderCVInternalError
from rendercv.schema.models.cv.entries.bases.entry_with_complex_fields import (
    BaseEntryWithComplexFields,
    get_date_object,
)
from tests.strategies import valid_date_strings


class TestGetDateObject:
    @pytest.mark.parametrize(
        ("date", "expected_date_object", "expecting_error"),
        [
            ("2020-01-01", Date(2020, 1, 1), False),
            ("2020-01", Date(2020, 1, 1), False),
            ("2020", Date(2020, 1, 1), False),
            (2020, Date(2020, 1, 1), False),
            ("present", None, True),
            ("invalid", None, True),
            ("20222", None, True),
            ("202222-20200", None, True),
            ("202222-12-20", None, True),
            ("2022-20-20", None, True),
        ],
    )
    def test_parses_valid_dates_and_rejects_invalid_dates(
        self, date, expected_date_object, expecting_error
    ):
        if expecting_error:
            with pytest.raises((RenderCVInternalError, AssertionError, ValueError)):
                get_date_object(date)
        else:
            assert get_date_object(date) == expected_date_object

    def test_handles_present_with_current_date(self):
        current_date = Date(2025, 11, 3)
        assert get_date_object("present", current_date=current_date) == current_date


class TestBaseEntryWithComplexFields:
    @pytest.mark.parametrize(
        ("start_date", "end_date", "date"),
        [
            ("aaa", "2021-01-01", None),
            ("2020-01-01", "aaa", None),
            ("2023-01-01", "2021-01-01", None),
            ("2022", "2021", None),
            ("2025", "2021", None),
            ("2020-01-01", "invalid_end_date", None),
            ("invalid_start_date", "2021-01-01", None),
            ("2020-99-99", "2021-01-01", None),
            ("2020-10-12", "2020-99-99", None),
            (None, None, "2020-20-20"),
        ],
    )
    def test_rejects_invalid_dates(self, start_date, end_date, date):
        with pytest.raises(pydantic.ValidationError):
            BaseEntryWithComplexFields(
                start_date=start_date, end_date=end_date, date=date
            )

    @settings(deadline=None)
    @given(date=valid_date_strings())
    def test_date_only_clears_start_and_end(self, date: str) -> None:
        entry = BaseEntryWithComplexFields(
            date=date, start_date="2020-01", end_date="2021-01"
        )
        assert entry.start_date is None
        assert entry.end_date is None

    @settings(deadline=None)
    @given(
        start_date=st.dates(
            min_value=Date(1900, 1, 1), max_value=Date(2025, 12, 31)
        ).map(lambda d: d.isoformat())
    )
    def test_start_only_implies_present(self, start_date: str) -> None:
        entry = BaseEntryWithComplexFields(start_date=start_date)
        assert entry.end_date == "present"

    @settings(deadline=None)
    @given(end_date=valid_date_strings())
    def test_end_only_becomes_date(self, end_date: str) -> None:
        entry = BaseEntryWithComplexFields(end_date=end_date)
        assert entry.date == end_date
        assert entry.start_date is None
        assert entry.end_date is None
