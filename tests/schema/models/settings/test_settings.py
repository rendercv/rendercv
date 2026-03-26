import datetime

import pydantic
import pytest
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st

from rendercv.schema.models.settings.settings import Settings


class TestCurrentDate:
    def test_accepts_today_string(self):
        settings = Settings(current_date="today")

        assert settings.current_date == "today"

    def test_accepts_date_object(self):
        date = datetime.date(2024, 6, 15)
        settings = Settings(current_date=date)

        assert settings.current_date == date

    def test_accepts_iso_date_string(self):
        settings = Settings(current_date="2024-06-15")  # ty: ignore[invalid-argument-type]

        assert settings.current_date == datetime.date(2024, 6, 15)

    def test_rejects_invalid_string(self):
        with pytest.raises(pydantic.ValidationError):
            Settings(current_date="not-a-date")  # ty: ignore[invalid-argument-type]


class TestSettings:
    def test_removes_duplicates(self):
        settings = Settings(bold_keywords=["Python", "Java", "Python", "C++", "Java"])

        assert len(settings.bold_keywords) == 3
        assert set(settings.bold_keywords) == {"Python", "Java", "C++"}

    def test_with_empty_list(self):
        settings = Settings(bold_keywords=[])

        assert settings.bold_keywords == []

    def test_with_unique_list(self):
        settings = Settings(bold_keywords=["Python", "Java", "C++"])

        assert len(settings.bold_keywords) == 3
        assert set(settings.bold_keywords) == {"Python", "Java", "C++"}

    def test_pdf_title_default(self):
        settings = Settings()

        assert settings.pdf_title == "NAME - CV"

    def test_pdf_title_custom(self):
        settings = Settings(pdf_title="NAME - Resume YEAR")

        assert settings.pdf_title == "NAME - Resume YEAR"

    @hypothesis_settings(deadline=None)
    @given(
        keywords=st.lists(
            st.text(min_size=1, max_size=20).filter(lambda s: s.strip()),
            min_size=0,
            max_size=20,
        )
    )
    def test_deduplication_preserves_order(self, keywords: list[str]) -> None:
        settings = Settings(bold_keywords=keywords)
        # No duplicates
        assert len(settings.bold_keywords) == len(set(settings.bold_keywords))
        # Every unique keyword from input is present
        assert set(settings.bold_keywords) == set(keywords)
        # Order matches first occurrence
        seen: list[str] = []
        for k in keywords:
            if k not in seen:
                seen.append(k)
        assert settings.bold_keywords == seen
