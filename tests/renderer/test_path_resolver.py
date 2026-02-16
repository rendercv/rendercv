import datetime
import pathlib

import pytest

from rendercv.renderer.path_resolver import resolve_rendercv_file_path
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.settings.settings import Settings


class TestResolveRendercvFilePath:
    @pytest.mark.parametrize(
        ("file_path_template", "cv_name", "current_date", "expected_filename"),
        [
            # Name placeholders
            ("NAME.pdf", "John Doe", None, "John Doe.pdf"),
            ("NAME_IN_SNAKE_CASE.pdf", "John Doe", None, "John_Doe.pdf"),
            ("NAME_IN_LOWER_SNAKE_CASE.pdf", "John Doe", None, "john_doe.pdf"),
            ("NAME_IN_UPPER_SNAKE_CASE.pdf", "John Doe", None, "JOHN_DOE.pdf"),
            ("NAME_IN_KEBAB_CASE.pdf", "John Doe", None, "John-Doe.pdf"),
            ("NAME_IN_LOWER_KEBAB_CASE.pdf", "John Doe", None, "john-doe.pdf"),
            ("NAME_IN_UPPER_KEBAB_CASE.pdf", "John Doe", None, "JOHN-DOE.pdf"),
            # Date placeholders
            ("MONTH_NAME.pdf", "John Doe", datetime.date(2024, 3, 15), "March.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                datetime.date(2024, 3, 15),
                "Mar.pdf",
            ),
            ("MONTH.pdf", "John Doe", datetime.date(2024, 3, 15), "3.pdf"),
            (
                "MONTH_IN_TWO_DIGITS.pdf",
                "John Doe",
                datetime.date(2024, 3, 15),
                "03.pdf",
            ),
            ("YEAR.pdf", "John Doe", datetime.date(2024, 3, 15), "2024.pdf"),
            (
                "YEAR_IN_TWO_DIGITS.pdf",
                "John Doe",
                datetime.date(2024, 3, 15),
                "24.pdf",
            ),
            # Different months
            ("MONTH_NAME.pdf", "John Doe", datetime.date(2024, 1, 1), "January.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                datetime.date(2024, 1, 1),
                "Jan.pdf",
            ),
            ("MONTH_NAME.pdf", "John Doe", datetime.date(2024, 6, 1), "June.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                datetime.date(2024, 6, 1),
                "June.pdf",
            ),
            ("MONTH_NAME.pdf", "John Doe", datetime.date(2024, 12, 1), "December.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                datetime.date(2024, 12, 1),
                "Dec.pdf",
            ),
            # Day placeholders
            ("DAY.pdf", "John Doe", datetime.date(2024, 3, 15), "15.pdf"),
            ("DAY_IN_TWO_DIGITS.pdf", "John Doe", datetime.date(2024, 3, 5), "05.pdf"),
            # Multiple placeholders
            (
                "NAME_IN_SNAKE_CASE_CV_YEAR-MONTH_IN_TWO_DIGITS.pdf",
                "John Doe",
                datetime.date(2024, 3, 15),
                "John_Doe_CV_2024-03.pdf",
            ),
            # No placeholders
            ("my_cv.pdf", "John Doe", None, "my_cv.pdf"),
        ],
    )
    def test_resolve_rendercv_file_path(
        self,
        tmp_path: pathlib.Path,
        file_path_template: str,
        cv_name: str,
        current_date: datetime.date | None,
        expected_filename: str,
    ):
        if current_date is not None:
            model = RenderCVModel(
                cv=Cv(name=cv_name), settings=Settings(current_date=current_date)
            )
        else:
            model = RenderCVModel(cv=Cv(name=cv_name))

        file_path = tmp_path / file_path_template
        result = resolve_rendercv_file_path(model, file_path)

        assert result.name == expected_filename
        assert result.parent == tmp_path

    def test_creates_parent_directories(self, tmp_path: pathlib.Path):
        model = RenderCVModel(cv=Cv(name="John Doe"))
        nested_dir = tmp_path / "output" / "cv" / "final"
        file_path = nested_dir / "NAME_IN_SNAKE_CASE_CV.pdf"

        result = resolve_rendercv_file_path(model, file_path)

        assert result.parent.exists()
        assert result == nested_dir / "John_Doe_CV.pdf"
