import pathlib

import pydantic
import pytest

from rendercv.schema.models.path import (
    ExistingPathRelativeToInput,
    PlannedPathRelativeToInput,
)
from rendercv.schema.models.validation_context import ValidationContext


class PlannedPathModel(pydantic.BaseModel):
    output: PlannedPathRelativeToInput


@pytest.fixture
def existing_file(tmp_path):
    existing = tmp_path / "existing.txt"
    existing.touch()
    return existing


@pytest.fixture
def context_with_input_file(tmp_path):
    return {"context": ValidationContext(input_file_path=tmp_path / "input.yaml")}


existing_input_relative_path_adapter = pydantic.TypeAdapter(ExistingPathRelativeToInput)
planned_input_relative_path_adapter = pydantic.TypeAdapter(PlannedPathRelativeToInput)


class TestExistingInputRelativePath:
    def test_absolute_path_to_existing_file(
        self, existing_file, context_with_input_file
    ):
        result = existing_input_relative_path_adapter.validate_python(
            existing_file, context=context_with_input_file
        )

        assert result == existing_file

    def test_absolute_path_to_nonexistent_file_raises_error(
        self, tmp_path, context_with_input_file
    ):
        nonexistent = tmp_path / "nonexistent.txt"

        with pytest.raises(pydantic.ValidationError, match="does not exist"):
            existing_input_relative_path_adapter.validate_python(
                nonexistent, context=context_with_input_file
            )

    def test_relative_path_to_existing_file(self, tmp_path, context_with_input_file):
        existing = tmp_path / "relative_existing.txt"
        existing.touch()
        relative_path = pathlib.Path("relative_existing.txt")

        result = existing_input_relative_path_adapter.validate_python(
            relative_path, context=context_with_input_file
        )

        # Should be resolved relative to input_file_path directory
        assert result == tmp_path / "relative_existing.txt"
        assert result.exists()

    def test_relative_path_to_nonexistent_file_raises_error(
        self, context_with_input_file
    ):
        relative_path = pathlib.Path("nonexistent_relative.txt")

        with pytest.raises(pydantic.ValidationError, match="does not exist"):
            existing_input_relative_path_adapter.validate_python(
                relative_path, context=context_with_input_file
            )

    @pytest.mark.parametrize(
        "relative_path",
        [
            pathlib.Path("subdir/file.txt"),
            pathlib.Path("../sibling/file.txt"),
            pathlib.Path("./same_dir/file.txt"),
        ],
    )
    def test_various_relative_path_formats(
        self, tmp_path, context_with_input_file, relative_path
    ):
        expected_path = tmp_path / relative_path
        expected_path.parent.mkdir(parents=True, exist_ok=True)
        expected_path.touch()

        result = existing_input_relative_path_adapter.validate_python(
            relative_path, context=context_with_input_file
        )

        assert result == expected_path
        assert result.exists()

    def test_path_string_validation(self, existing_file, context_with_input_file):
        result = existing_input_relative_path_adapter.validate_python(
            str(existing_file), context=context_with_input_file
        )

        assert result == existing_file

    def test_existing_path_is_not_a_file_raises_error(
        self, tmp_path, context_with_input_file
    ):
        new_dir = tmp_path / "new_dir"
        new_dir.mkdir()
        with pytest.raises(pydantic.ValidationError, match="is not a file"):
            existing_input_relative_path_adapter.validate_python(
                new_dir, context=context_with_input_file
            )


class TestPlannedInputRelativePath:
    def test_absolute_path_to_existing_file(
        self, existing_file, context_with_input_file
    ):
        result = planned_input_relative_path_adapter.validate_python(
            existing_file, context=context_with_input_file
        )

        assert result == existing_file

    def test_absolute_path_to_nonexistent_file_is_accepted(
        self, tmp_path, context_with_input_file
    ):
        nonexistent = tmp_path / "planned_file.txt"
        result = planned_input_relative_path_adapter.validate_python(
            nonexistent, context=context_with_input_file
        )

        assert result == nonexistent
        assert not result.exists()

    def test_relative_path_to_existing_file(self, tmp_path, context_with_input_file):
        existing = tmp_path / "relative_existing.txt"
        existing.touch()

        relative_path = pathlib.Path("relative_existing.txt")

        result = planned_input_relative_path_adapter.validate_python(
            relative_path, context=context_with_input_file
        )

        assert result == tmp_path / "relative_existing.txt"
        assert result.exists()

    def test_relative_path_to_nonexistent_file_is_accepted(
        self, tmp_path, context_with_input_file
    ):
        relative_path = pathlib.Path("planned_output.pdf")
        result = planned_input_relative_path_adapter.validate_python(
            relative_path, context=context_with_input_file
        )

        assert result == tmp_path / "planned_output.pdf"
        assert not result.exists()

    @pytest.mark.parametrize(
        "relative_path",
        [
            pathlib.Path("output/result.pdf"),
            pathlib.Path("../build/output.html"),
            pathlib.Path("./generated/doc.md"),
        ],
    )
    def test_various_relative_path_formats_for_planned_paths(
        self, tmp_path, context_with_input_file, relative_path
    ):
        result = planned_input_relative_path_adapter.validate_python(
            relative_path, context=context_with_input_file
        )

        expected_path = tmp_path / relative_path
        assert result == expected_path

    def test_path_string_validation(self, tmp_path, context_with_input_file):
        planned_path = "output/generated.pdf"
        result = planned_input_relative_path_adapter.validate_python(
            planned_path, context=context_with_input_file
        )

        assert result == tmp_path / planned_path


class TestPathResolutionBehavior:
    @pytest.mark.parametrize(
        "path_adapter",
        [existing_input_relative_path_adapter, planned_input_relative_path_adapter],
    )
    def test_absolute_path_remains_unchanged(
        self, existing_file, context_with_input_file, path_adapter
    ):
        result = path_adapter.validate_python(
            existing_file, context=context_with_input_file
        )

        assert result == existing_file
        assert result.is_absolute()

    @pytest.mark.parametrize(
        "path_adapter",
        [existing_input_relative_path_adapter, planned_input_relative_path_adapter],
    )
    def test_relative_path_gets_resolved(
        self, tmp_path, context_with_input_file, path_adapter
    ):
        existing = tmp_path / "test.txt"
        existing.touch()
        relative_path = pathlib.Path("test.txt")

        result = path_adapter.validate_python(
            relative_path, context=context_with_input_file
        )

        assert result.is_absolute()
        assert result == tmp_path / "test.txt"

    def test_only_existing_type_validates_file_existence(
        self, tmp_path, context_with_input_file
    ):
        nonexistent_path = tmp_path / "does_not_exist.txt"

        with pytest.raises(pydantic.ValidationError, match="does not exist"):
            existing_input_relative_path_adapter.validate_python(
                nonexistent_path, context=context_with_input_file
            )

        result = planned_input_relative_path_adapter.validate_python(
            nonexistent_path, context=context_with_input_file
        )
        assert result == nonexistent_path


class TestPathSerialization:
    def test_serializes_path_relative_to_cwd_when_possible(self):
        input_file_path = pathlib.Path.cwd() / "input.yaml"
        model = PlannedPathModel.model_validate(
            {"output": "build/output.pdf"},
            context={"context": ValidationContext(input_file_path=input_file_path)},
        )

        assert model.model_dump()["output"] == "build/output.pdf"

    def test_serializes_absolute_path_outside_cwd_without_crashing(self, tmp_path):
        input_file_path = tmp_path / "input.yaml"
        outside_path = tmp_path / "build" / "output.pdf"
        model = PlannedPathModel.model_validate(
            {"output": outside_path},
            context={"context": ValidationContext(input_file_path=input_file_path)},
        )

        assert model.model_dump()["output"] == str(outside_path)
