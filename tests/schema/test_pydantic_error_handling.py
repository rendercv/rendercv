import pydantic

from rendercv.schema.pydantic_error_handling import parse_validation_errors
from rendercv.schema.rendercv_model_builder import (
    build_rendercv_model_from_dictionary,
)
from rendercv.schema.yaml_reader import read_yaml


def test_parse_validation_errors(testdata_dir):
    wrong_input_file_path = testdata_dir / "wrong_input.yaml"
    wrong_input_dictionary = read_yaml(wrong_input_file_path)

    expected_errors_file_path = testdata_dir / "expected_errors.yaml"
    expected_errors = read_yaml(expected_errors_file_path)["expected_errors"]

    try:
        build_rendercv_model_from_dictionary(wrong_input_dictionary)
    except pydantic.ValidationError as e:
        validation_errors = parse_validation_errors(e, wrong_input_dictionary)
        for validation_error, expected_error in zip(
            validation_errors, expected_errors, strict=True
        ):
            expected_error["yaml_location"] = tuple(
                tuple(part) for part in expected_error["yaml_location"]
            )
            expected_error["location"] = tuple(expected_error["location"])
            assert validation_error == expected_error
