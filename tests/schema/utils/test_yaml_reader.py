from ruamel.yaml.comments import CommentedMap

from rendercv.schema.utils.yaml_reader import read_yaml


def test_read_input_file(input_file_path):
    commented_map_dictionary = read_yaml(input_file_path)

    assert isinstance(commented_map_dictionary, CommentedMap)
