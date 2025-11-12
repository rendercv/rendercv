import io

import pytest
import ruamel.yaml

from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.utils.rendercv_reader import read_input_file


def test_read_input_file(input_file_path):
    data_model = read_input_file(input_file_path)

    assert isinstance(data_model, RenderCVModel)


def test_read_input_file_directly_with_contents():
    input_dictionary = {
        "cv": {
            "name": "John Doe",
        },
        "design": {
            "theme": "classic",
        },
    }

    # dump the dictionary to a yaml file
    yaml_object = ruamel.yaml.YAML()
    yaml_object.width = 60
    yaml_object.indent(mapping=2, sequence=4, offset=2)
    with io.StringIO() as string_stream:
        yaml_object.dump(input_dictionary, string_stream)
        yaml_string = string_stream.getvalue()

    data_model = read_input_file(yaml_string)

    assert isinstance(data_model, RenderCVModel)


def test_read_input_file_invalid_file(tmp_path):
    invalid_file_path = tmp_path / "invalid.extension"
    invalid_file_path.write_text("dummy content", encoding="utf-8")
    with pytest.raises(ValueError):  # NOQA: PT011
        read_input_file(invalid_file_path)


def test_read_input_file_that_doesnt_exist(tmp_path):
    non_existent_file_path = tmp_path / "non_existent_file.yaml"
    with pytest.raises(FileNotFoundError):
        read_input_file(non_existent_file_path)
