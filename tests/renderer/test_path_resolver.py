import datetime
import pathlib

import pytest

from rendercv.renderer.path_resolver import resolve_rendercv_file_path
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.settings.settings import Settings


class TestResolveRendercvFilePath:
    @pytest.mark.parametrize(
        ("placeholder", "expected_filename"),
        [
            ("NAME", "John Doe"),
            ("NAME_IN_SNAKE_CASE", "John_Doe"),
            ("NAME_IN_LOWER_SNAKE_CASE", "john_doe"),
            ("NAME_IN_UPPER_SNAKE_CASE", "JOHN_DOE"),
            ("NAME_IN_KEBAB_CASE", "John-Doe"),
            ("NAME_IN_LOWER_KEBAB_CASE", "john-doe"),
            ("NAME_IN_UPPER_KEBAB_CASE", "JOHN-DOE"),
        ],
    )
    def test_name_placeholders(
        self, tmp_path: pathlib.Path, placeholder: str, expected_filename: str
    ):
        model = RenderCVModel(cv=Cv(name="John Doe"))
        file_path = tmp_path / f"{placeholder}.pdf"

        result = resolve_rendercv_file_path(model, file_path)

        assert result.name == f"{expected_filename}.pdf"
        assert result.parent == tmp_path

    @pytest.mark.parametrize(
        ("placeholder", "expected_filename"),
        [
            ("FULL_MONTH_NAME", "March"),
            ("MONTH_ABBREVIATION", "Mar"),
            ("MONTH", "3"),
            ("MONTH_IN_TWO_DIGITS", "03"),
            ("YEAR", "2024"),
            ("YEAR_IN_TWO_DIGITS", "24"),
        ],
    )
    def test_date_placeholders(
        self, tmp_path: pathlib.Path, placeholder: str, expected_filename: str
    ):
        model = RenderCVModel(
            cv=Cv(name="John Doe"),
            settings=Settings(current_date=datetime.date(2024, 3, 15)),
        )
        file_path = tmp_path / f"{placeholder}.pdf"

        result = resolve_rendercv_file_path(model, file_path)

        assert result.name == f"{expected_filename}.pdf"

    def test_multiple_placeholders_in_filename(self, tmp_path: pathlib.Path):
        model = RenderCVModel(
            cv=Cv(name="John Doe"),
            settings=Settings(current_date=datetime.date(2024, 3, 15)),
        )
        file_path = tmp_path / "NAME_IN_SNAKE_CASE_CV_YEAR-MONTH_IN_TWO_DIGITS.pdf"

        result = resolve_rendercv_file_path(model, file_path)

        assert result.name == "John_Doe_CV_2024-03.pdf"

    def test_filename_without_placeholders(self, tmp_path: pathlib.Path):
        model = RenderCVModel(cv=Cv(name="John Doe"))
        file_path = tmp_path / "my_cv.pdf"

        result = resolve_rendercv_file_path(model, file_path)

        assert result.name == "my_cv.pdf"

    def test_creates_parent_directories(self, tmp_path: pathlib.Path):
        model = RenderCVModel(cv=Cv(name="John Doe"))
        nested_dir = tmp_path / "output" / "cv" / "final"
        file_path = nested_dir / "NAME_IN_SNAKE_CASE_CV.pdf"

        result = resolve_rendercv_file_path(model, file_path)

        assert result.parent.exists()
        assert result == nested_dir / "John_Doe_CV.pdf"

    @pytest.mark.parametrize(
        ("month", "expected_full_name", "expected_abbreviation"),
        [
            (1, "January", "Jan"),
            (6, "June", "June"),
            (12, "December", "Dec"),
        ],
    )
    def test_month_names_for_different_months(
        self,
        tmp_path: pathlib.Path,
        month: int,
        expected_full_name: str,
        expected_abbreviation: str,
    ):
        model = RenderCVModel(
            cv=Cv(name="John Doe"),
            settings=Settings(current_date=datetime.date(2024, month, 1)),
        )

        full_name_result = resolve_rendercv_file_path(
            model, tmp_path / "FULL_MONTH_NAME.pdf"
        )
        abbreviation_result = resolve_rendercv_file_path(
            model, tmp_path / "MONTH_ABBREVIATION.pdf"
        )

        assert full_name_result.name == f"{expected_full_name}.pdf"
        assert abbreviation_result.name == f"{expected_abbreviation}.pdf"
