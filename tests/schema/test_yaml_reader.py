import pathlib

import pytest
from ruamel.yaml.comments import CommentedMap

from rendercv.exception import RenderCVInternalError, RenderCVUserError
from rendercv.schema.yaml_reader import read_yaml


class TestReadYaml:
    def test_reads_valid_yaml_file(self, input_file_path):
        commented_map_dictionary = read_yaml(input_file_path)

        assert isinstance(commented_map_dictionary, CommentedMap)

    def test_nonexistent_file_raises_error(self, tmp_path: pathlib.Path):
        nonexistent_file_path = tmp_path / "nonexistent.yaml"

        with pytest.raises(RenderCVUserError):
            read_yaml(nonexistent_file_path)

    def test_invalid_file_extension_raises_error(self, tmp_path: pathlib.Path):
        invalid_file_path = tmp_path / "invalid.extension"
        invalid_file_path.touch()

        with pytest.raises(RenderCVUserError):
            read_yaml(invalid_file_path)

    def test_plain_string_path_raises_error(self):
        with pytest.raises(RenderCVInternalError):
            read_yaml("plain_string.yaml")

    def test_empty_file_raises_error(self, tmp_path: pathlib.Path):
        empty_file_path = tmp_path / "empty.yaml"
        empty_file_path.write_text("", encoding="utf-8")

        with pytest.raises(RenderCVUserError, match="empty"):
            read_yaml(empty_file_path)
