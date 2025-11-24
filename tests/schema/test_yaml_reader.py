import pathlib

import pytest
from ruamel.yaml.comments import CommentedMap

from rendercv.exception import RenderCVInternalError, RenderCVUserError
from rendercv.schema.yaml_reader import read_yaml


def test_read_input_file(input_file_path):
    commented_map_dictionary = read_yaml(input_file_path)

    assert isinstance(commented_map_dictionary, CommentedMap)


def test_nonexistent_file_raises_error(tmp_path: pathlib.Path):
    nonexistent_file_path = tmp_path / "nonexistent.yaml"
    with pytest.raises(RenderCVUserError):
        read_yaml(nonexistent_file_path)


def test_invalid_file_extension_raises_error(tmp_path: pathlib.Path):
    invalid_file_path = tmp_path / "invalid.extension"
    invalid_file_path.touch()
    with pytest.raises(RenderCVUserError):
        read_yaml(invalid_file_path)


def test_plain_string_path_raises_error():
    with pytest.raises(RenderCVInternalError):
        read_yaml("plain_string.yaml")
