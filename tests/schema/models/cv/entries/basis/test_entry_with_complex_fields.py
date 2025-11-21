from datetime import date as Date

import pydantic
import pytest

from rendercv.schema.models.cv.entries.bases.entry_with_complex_fields import (
    BaseEntryWithComplexFields,
    get_date_object,
)


@pytest.mark.parametrize(
    ("date", "expected_date_object", "expected_error"),
    [
        ("2020-01-01", Date(2020, 1, 1), None),
        ("2020-01", Date(2020, 1, 1), None),
        ("2020", Date(2020, 1, 1), None),
        (2020, Date(2020, 1, 1), None),
        ("present", Date.today(), None),
        ("invalid", None, ValueError),
        ("20222", None, ValueError),
        ("202222-20200", None, ValueError),
        ("202222-12-20", None, ValueError),
        ("2022-20-20", None, ValueError),
    ],
)
def test_get_date_object(date, expected_date_object, expected_error):
    if expected_error:
        with pytest.raises(expected_error):
            get_date_object(date)
    else:
        assert get_date_object(date) == expected_date_object


def test_get_date_object_with_today():
    today = Date(2025, 11, 3)
    assert get_date_object("present", today=today) == today


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
def test_invalid_dates(start_date, end_date, date):
    with pytest.raises(pydantic.ValidationError):
        BaseEntryWithComplexFields(start_date=start_date, end_date=end_date, date=date)
