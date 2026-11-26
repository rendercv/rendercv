import concurrent.futures
import pathlib

import pytest
from ruamel.yaml.comments import CommentedMap

from rendercv.exception import RenderCVUserError
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
        # A bare path-looking string parses to a YAML scalar, not a mapping.
        # It is a user-facing input error (the web editor sends raw editor
        # text on every keystroke), not an internal one: RenderCVUserError is
        # what the API's error boundary turns into a 422 rather than a 500.
        with pytest.raises(RenderCVUserError, match="mapping"):
            read_yaml("plain_string.yaml")

    def test_non_mapping_document_raises_user_error(self):
        with pytest.raises(RenderCVUserError, match="mapping"):
            read_yaml("[a, b]")

    def test_empty_file_raises_error(self, tmp_path: pathlib.Path):
        empty_file_path = tmp_path / "empty.yaml"
        empty_file_path.write_text("", encoding="utf-8")

        with pytest.raises(RenderCVUserError, match="empty"):
            read_yaml(empty_file_path)

    def test_treats_asterisk_as_plain_text(self):
        result = read_yaml("key: *not_an_alias")

        assert isinstance(result, CommentedMap)
        assert result["key"] == "*not_an_alias"

    def test_concurrent_parsing_is_thread_safe(self):
        # Why: a shared module-level ruamel YAML instance corrupts its
        # internal parser state under concurrent use (observed as
        # AttributeError/ParserError 500s in the web API's threadpool);
        # read_yaml must build a parser per call so parallel callers are
        # safe. Regression for the shared-instance bug.
        sections = "\n".join(
            f"    section_{i}:\n      - entry one {i}\n      - entry two {i}"
            for i in range(40)
        )
        yaml_content = "cv:\n  name: John Doe\n  sections:\n" + sections + "\n"

        def parse_repeatedly(worker_index: int) -> int:
            for _ in range(25):
                result = read_yaml(yaml_content)
                assert result["cv"]["name"] == "John Doe"
            return worker_index

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(parse_repeatedly, range(8)))

        assert results == list(range(8))
