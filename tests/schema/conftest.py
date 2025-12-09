import pathlib
import shutil

import pytest
import ruamel.yaml


@pytest.fixture
def input_file_path(tmp_path, update_testdata: bool) -> pathlib.Path:
    # copy the input file to the temporary directory
    input_file_path = pathlib.Path(__file__).parent / "testdata" / "input_file.yaml"
    # Update the auxiliary files if update_testdata is True
    if update_testdata:
        # create testdata directory if it doesn't exist
        if not input_file_path.parent.exists():
            input_file_path.parent.mkdir()

        input_dictionary = {
            "cv": {
                "name": "John Doe",
                "sections": {"test_section": ["this is a text entry."]},
            },
        }

        # dump the dictionary to a yaml file
        yaml_object = ruamel.yaml.YAML()
        yaml_object.dump(input_dictionary, input_file_path)

    shutil.copyfile(input_file_path, tmp_path / input_file_path.name)
    return tmp_path / input_file_path.name
