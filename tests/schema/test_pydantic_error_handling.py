import pathlib

import pydantic

from rendercv.schema.pydantic_error_handling import parse_validation_errors
from rendercv.schema.rendercv_reader import (
    validate_input_dictionary_and_return_rendercv_pydantic_model,
)
from rendercv.schema.yaml_reader import read_yaml


def test_parse_validation_errors():
    wrong_input_file_path = (
        pathlib.Path(__file__).parent / "testdata" / "test_reader" / "wrong_input.yaml"
    )
    wrong_input_dictionary = read_yaml(wrong_input_file_path)

    expected_errors_file_path = (
        pathlib.Path(__file__).parent
        / "testdata"
        / "test_reader"
        / "expected_errors.yaml"
    )
    expected_errors = read_yaml(expected_errors_file_path)["expected_errors"]

    try:
        validate_input_dictionary_and_return_rendercv_pydantic_model(
            wrong_input_dictionary
        )
    except pydantic.ValidationError as e:
        validation_errors = parse_validation_errors(e, wrong_input_dictionary)
        for validation_error, expected_error in zip(
            validation_errors, expected_errors, strict=True
        ):
            assert validation_error["location"] == tuple(expected_error["location"])
            assert validation_error["message"] == expected_error["message"]
            assert validation_error["input"] == expected_error["input"]
            assert validation_error["yaml_location"] == tuple(
                tuple(part) for part in expected_error["yaml_location"]
            )
