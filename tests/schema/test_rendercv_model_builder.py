import io

import pytest
import ruamel.yaml

from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.rendercv_model_builder import build_rendercv_model


def test_read_input_file(input_file_path):
    data_model = build_rendercv_model(input_file_path)

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

    data_model = build_rendercv_model(yaml_string)

    assert isinstance(data_model, RenderCVModel)


def test_read_input_file_invalid_file(tmp_path):
    invalid_file_path = tmp_path / "invalid.extension"
    invalid_file_path.write_text("dummy content", encoding="utf-8")
    with pytest.raises(ValueError):  # NOQA: PT011
        build_rendercv_model(invalid_file_path)


def test_read_input_file_that_doesnt_exist(tmp_path):
    non_existent_file_path = tmp_path / "non_existent_file.yaml"
    with pytest.raises(FileNotFoundError):
        build_rendercv_model(non_existent_file_path)
