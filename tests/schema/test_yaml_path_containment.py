import pathlib
import pytest
from rendercv.schema.models.path import resolve_relative_path
import pydantic

class DummyInfo:
    def __init__(self, input_file_path):
        self.context = {"context": type("C", (), {"input_file_path": input_file_path})()}

def test_absolute_path_outside_input_dir(tmp_path):
    # Create a dummy input YAML in a temp dir
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    input_file = input_dir / "cv.yaml"
    input_file.write_text("cv: {}\n")

    # Create a file outside the input dir
    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("secret")

    info = DummyInfo(input_file)
    # Should raise error if path is outside input dir
    import pydantic_core
    with pytest.raises(pydantic_core.PydanticCustomError):
        resolve_relative_path(outside_file, info, must_exist=True)

def test_relative_path_within_input_dir(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    input_file = input_dir / "cv.yaml"
    input_file.write_text("cv: {}\n")
    inside_file = input_dir / "photo.jpg"
    inside_file.write_text("photo")
    info = DummyInfo(input_file)
    # Should succeed for file inside input dir
    result = resolve_relative_path(inside_file.relative_to(input_dir), info, must_exist=True)
    assert result.resolve() == inside_file.resolve()
