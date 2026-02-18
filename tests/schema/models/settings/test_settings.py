import datetime

import pydantic
import pytest

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
