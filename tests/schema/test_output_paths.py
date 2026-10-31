import pathlib
from datetime import date as Date

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.settings.render_command import RenderCommand
from rendercv.schema.models.settings.settings import Settings
from rendercv.schema.models.validation_context import ValidationContext
from rendercv.schema.output_paths import (
    resolve_output_folder_placeholder,
    resolve_output_path,
)


def test_outputs_cannot_overwrite_each_other(tmp_path):
    with pytest.raises(ValidationError, match="outputs overlap"):
        RenderCVModel.model_validate(
            {
                "cv": {"name": "Jane"},
                "settings": {
                    "render_command": {
                        "pdf_path": str(tmp_path / "same.file"),
                        "typst_path": str(tmp_path / "same.file"),
                    }
                },
            }
        )


def test_outputs_cannot_overwrite_the_input(tmp_path):
    source = tmp_path / "cv.yaml"
    with pytest.raises(ValidationError, match="overwrite an input"):
        RenderCVModel.model_validate(
            {
                "cv": {"name": "Jane"},
                "settings": {"render_command": {"pdf_path": "cv.yaml"}},
            },
            context={"context": ValidationContext(input_file_path=source)},
        )


def test_numbered_page_outputs_cannot_overwrite_another_format(tmp_path):
    with pytest.raises(ValidationError, match="outputs overlap"):
        RenderCVModel.model_validate(
            {
                "cv": {"name": "Jane"},
                "settings": {
                    "render_command": {
                        "pdf_path": str(tmp_path / "pages_2.png"),
                        "png_path": str(tmp_path / "pages.png"),
                    }
                },
            }
        )


def test_outputs_cannot_be_each_others_parent_directory(tmp_path):
    with pytest.raises(ValidationError, match="outputs overlap"):
        RenderCVModel.model_validate(
            {
                "cv": {"name": "Jane"},
                "settings": {
                    "render_command": {
                        "pdf_path": str(tmp_path / "output"),
                        "typst_path": str(tmp_path / "output" / "cv.typ"),
                    }
                },
            }
        )
    assert not (tmp_path / "output").exists()


def test_outputs_cannot_replace_an_existing_directory_or_go_inside_a_file(tmp_path):
    (tmp_path / "folder").mkdir()
    (tmp_path / "file").write_text("", encoding="utf-8")
    for pdf_path in (tmp_path / "folder", tmp_path / "file" / "cv.pdf"):
        with pytest.raises(ValidationError, match="conflicts with an existing"):
            RenderCVModel.model_validate(
                {
                    "cv": {"name": "Jane"},
                    "settings": {"render_command": {"pdf_path": str(pdf_path)}},
                }
            )


def test_output_folder_can_be_used_once_in_a_path(tmp_path):
    with pytest.raises(ValueError, match="only once"):
        resolve_output_folder_placeholder(
            tmp_path / "OUTPUT_FOLDER" / "OUTPUT_FOLDER" / "cv.pdf", tmp_path
        )


def test_disabled_outputs_do_not_reserve_their_paths(tmp_path):
    model = RenderCVModel.model_validate(
        {
            "cv": {"name": "Jane"},
            "settings": {
                "render_command": {
                    "pdf_path": str(tmp_path / "result"),
                    "typst_path": str(tmp_path / "result"),
                    "dont_generate_typst": True,
                }
            },
        }
    )
    assert model._output_plan.paths["pdf"] == tmp_path / "result"


def test_python_path_edits_do_not_leave_a_stale_plan(tmp_path):
    model = RenderCVModel.model_validate({"cv": {"name": "Jane"}})
    model.settings.render_command.typst_path = tmp_path / "source" / "cv.typ"
    assert model._output_plan.paths["typst"] == tmp_path / "source" / "cv.typ"


class TestResolveOutputPath:
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
            ("MONTH_NAME.pdf", "John Doe", Date(2024, 3, 15), "March.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                Date(2024, 3, 15),
                "Mar.pdf",
            ),
            ("MONTH.pdf", "John Doe", Date(2024, 3, 15), "3.pdf"),
            (
                "MONTH_IN_TWO_DIGITS.pdf",
                "John Doe",
                Date(2024, 3, 15),
                "03.pdf",
            ),
            ("YEAR.pdf", "John Doe", Date(2024, 3, 15), "2024.pdf"),
            (
                "YEAR_IN_TWO_DIGITS.pdf",
                "John Doe",
                Date(2024, 3, 15),
                "24.pdf",
            ),
            # Different months
            ("MONTH_NAME.pdf", "John Doe", Date(2024, 1, 1), "January.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                Date(2024, 1, 1),
                "Jan.pdf",
            ),
            ("MONTH_NAME.pdf", "John Doe", Date(2024, 6, 1), "June.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                Date(2024, 6, 1),
                "June.pdf",
            ),
            ("MONTH_NAME.pdf", "John Doe", Date(2024, 12, 1), "December.pdf"),
            (
                "MONTH_ABBREVIATION.pdf",
                "John Doe",
                Date(2024, 12, 1),
                "Dec.pdf",
            ),
            # Day placeholders
            ("DAY.pdf", "John Doe", Date(2024, 3, 15), "15.pdf"),
            ("DAY_IN_TWO_DIGITS.pdf", "John Doe", Date(2024, 3, 5), "05.pdf"),
            # Multiple placeholders
            (
                "NAME_IN_SNAKE_CASE_CV_YEAR-MONTH_IN_TWO_DIGITS.pdf",
                "John Doe",
                Date(2024, 3, 15),
                "John_Doe_CV_2024-03.pdf",
            ),
            # No placeholders
            ("my_cv.pdf", "John Doe", None, "my_cv.pdf"),
        ],
    )
    def test_resolve_output_path(
        self,
        tmp_path: pathlib.Path,
        file_path_template: str,
        cv_name: str,
        current_date: Date | None,
        expected_filename: str,
    ):
        if current_date is not None:
            model = RenderCVModel(
                cv=Cv(name=cv_name), settings=Settings(current_date=current_date)
            )
        else:
            model = RenderCVModel(cv=Cv(name=cv_name))

        file_path = tmp_path / file_path_template
        result = resolve_output_path(model, file_path)

        assert result.name == expected_filename
        assert result.parent == tmp_path

    @pytest.mark.parametrize(
        ("cv_name", "expected_filename"),
        [
            ("AC/DC", "AC_DC_CV.pdf"),
            ("../../evil", ".._.._evil_CV.pdf"),
            ('Jane: "J" <Doe>', "Jane___J___Doe__CV.pdf"),
        ],
    )
    def test_keeps_values_in_the_file_name(
        self, tmp_path: pathlib.Path, cv_name: str, expected_filename: str
    ):
        model = RenderCVModel(cv=Cv(name=cv_name))

        result = resolve_output_path(model, tmp_path / "NAME_IN_SNAKE_CASE_CV.pdf")

        assert result.name == expected_filename
        assert result.parent == tmp_path

    def test_output_folder_placeholder_resolved(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "rendercv_output"
        model = RenderCVModel(
            cv=Cv(name="John Doe"),
            settings=Settings(
                render_command=RenderCommand(output_folder=output_folder)
            ),
        )
        file_path = tmp_path / "OUTPUT_FOLDER" / "NAME_IN_SNAKE_CASE_CV.pdf"

        result = resolve_output_path(model, file_path)

        assert result == output_folder / "John_Doe_CV.pdf"

    def test_custom_output_folder(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "build" / "en"
        model = RenderCVModel(
            cv=Cv(name="John Doe"),
            settings=Settings(
                render_command=RenderCommand(output_folder=output_folder)
            ),
        )
        file_path = tmp_path / "OUTPUT_FOLDER" / "NAME_IN_SNAKE_CASE_CV.pdf"

        result = resolve_output_path(model, file_path)

        assert result == output_folder / "John_Doe_CV.pdf"

    def test_no_output_folder_placeholder_in_path(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "build"
        model = RenderCVModel(
            cv=Cv(name="John Doe"),
            settings=Settings(
                render_command=RenderCommand(output_folder=output_folder)
            ),
        )
        file_path = tmp_path / "custom_dir" / "NAME_IN_SNAKE_CASE_CV.pdf"

        result = resolve_output_path(model, file_path)

        assert result == tmp_path / "custom_dir" / "John_Doe_CV.pdf"

    def test_output_folder_with_subdirectory_in_path(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "build"
        model = RenderCVModel(
            cv=Cv(name="John Doe"),
            settings=Settings(
                render_command=RenderCommand(output_folder=output_folder)
            ),
        )
        file_path = tmp_path / "OUTPUT_FOLDER" / "typst" / "NAME_IN_SNAKE_CASE_CV.typ"

        result = resolve_output_path(model, file_path)

        assert result == output_folder / "typst" / "John_Doe_CV.typ"


class TestResolveOutputFolderPlaceholder:
    def test_replaces_output_folder_component(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "my_output"
        file_path = tmp_path / "OUTPUT_FOLDER" / "file.pdf"

        result = resolve_output_folder_placeholder(file_path, output_folder)

        assert result == output_folder / "file.pdf"

    def test_no_placeholder_returns_unchanged(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "my_output"
        file_path = tmp_path / "some_dir" / "file.pdf"

        result = resolve_output_folder_placeholder(file_path, output_folder)

        assert result == file_path

    def test_nested_output_folder(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "build" / "en"
        file_path = tmp_path / "OUTPUT_FOLDER" / "sub" / "file.pdf"

        result = resolve_output_folder_placeholder(file_path, output_folder)

        assert result == output_folder / "sub" / "file.pdf"

    def test_output_folder_only(self, tmp_path: pathlib.Path):
        output_folder = tmp_path / "build"
        file_path = tmp_path / "OUTPUT_FOLDER"

        result = resolve_output_folder_placeholder(file_path, output_folder)

        assert result == output_folder

    @given(
        suffix=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
        folder=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
    )
    def test_idempotent(self, suffix: str, folder: str) -> None:
        path = pathlib.PurePosixPath(f"/base/OUTPUT_FOLDER/{suffix}")
        output_folder = pathlib.PurePosixPath(f"/base/{folder}")
        first = resolve_output_folder_placeholder(
            pathlib.Path(path), pathlib.Path(output_folder)
        )
        second = resolve_output_folder_placeholder(first, pathlib.Path(output_folder))
        assert first == second

    @given(
        suffix=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
        folder=st.from_regex(r"[a-z_]{1,10}", fullmatch=True),
    )
    def test_output_folder_absent_in_result(self, suffix: str, folder: str) -> None:
        path = pathlib.PurePosixPath(f"/base/OUTPUT_FOLDER/{suffix}")
        output_folder = pathlib.PurePosixPath(f"/base/{folder}")
        result = resolve_output_folder_placeholder(
            pathlib.Path(path), pathlib.Path(output_folder)
        )
        assert "OUTPUT_FOLDER" not in result.parts
