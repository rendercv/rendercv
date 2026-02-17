from dataclasses import asdict

import pydantic
import pytest

from rendercv.exception import RenderCVInternalError
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.validation_context import ValidationContext
from rendercv.schema.pydantic_error_handling import (
    get_inner_yaml_object_from_its_key,
    parse_validation_errors,
)
from rendercv.schema.yaml_reader import read_yaml


class TestParseValidationErrors:
    def test_parses_all_validation_errors_from_wrong_input(self, testdata_dir):
        wrong_input_file_path = testdata_dir / "wrong_input.yaml"
        wrong_input_commented_map = read_yaml(wrong_input_file_path)

        expected_errors_file_path = testdata_dir / "expected_errors.yaml"
        expected_errors = read_yaml(expected_errors_file_path)["expected_errors"]

        try:
            RenderCVModel.model_validate(
                wrong_input_commented_map,
                context={
                    "context": ValidationContext(
                        input_file_path=wrong_input_file_path,
                        current_date=wrong_input_commented_map.get("settings", {}).get(
                            "current_date", None
                        ),
                    )
                },
            )
        except pydantic.ValidationError as e:
            validation_errors = [
                asdict(error)
                for error in parse_validation_errors(e, wrong_input_commented_map)
            ]
            for validation_error, expected_error in zip(
                validation_errors, expected_errors, strict=True
            ):
                expected_error["yaml_location"] = tuple(
                    tuple(part) for part in expected_error["yaml_location"]
                )
                expected_error["schema_location"] = tuple(
                    expected_error["schema_location"]
                )
                assert validation_error == expected_error, (
                    f"expected {expected_error} but got {validation_error}"
                )

    def test_provides_helpful_message_for_invalid_date_format(self, tmp_path):
        yaml_content = """
cv:
    name: John Doe
    sections:
        Experience:
            - name: Job
              start_date: 2020-01-01
              end_date: invalid_date
"""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        yaml_object = read_yaml(yaml_file)

        try:
            RenderCVModel.model_validate(
                yaml_object,
                context={
                    "context": ValidationContext(
                        input_file_path=yaml_file,
                    )
                },
            )
        except pydantic.ValidationError as e:
            errors = parse_validation_errors(e, yaml_object)
            end_date_error = next(
                (
                    err
                    for err in errors
                    if err.schema_location is not None
                    and "end_date" in err.schema_location
                ),
                None,
            )
            assert end_date_error is not None
            assert "YYYY-MM-DD, YYYY-MM" in end_date_error.message
            assert 'or "present"' in end_date_error.message


class TestParseValidationErrorsWithOverlaySources:
    def test_design_overlay_error_reports_correct_source_and_location(self):
        main_yaml = "cv:\n  name: John Doe\n"
        design_yaml = "design:\n  theme: not_a_valid_theme\n"

        main_cm = read_yaml(main_yaml)
        design_cm = read_yaml(design_yaml)
        main_cm["design"] = design_cm["design"]
        overlay_sources = {"design": design_cm}

        try:
            RenderCVModel.model_validate(
                main_cm,
                context={"context": ValidationContext()},
            )
            pytest.fail("Expected ValidationError")
        except pydantic.ValidationError as e:
            errors = parse_validation_errors(e, main_cm, overlay_sources)

        design_error = next(
            (
                err
                for err in errors
                if err.schema_location is not None
                and err.schema_location[0] == "design"
            ),
            None,
        )
        assert design_error is not None
        assert design_error.yaml_source == "design_yaml_file"
        assert design_error.yaml_location is not None

    def test_main_file_error_has_main_yaml_source(self):
        main_yaml = (
            "cv:\n"
            "  name: John Doe\n"
            "  phone: not_a_valid_phone\n"
            "design:\n"
            "  theme: classic\n"
        )
        main_cm = read_yaml(main_yaml)

        try:
            RenderCVModel.model_validate(
                main_cm,
                context={"context": ValidationContext()},
            )
            pytest.fail("Expected ValidationError")
        except pydantic.ValidationError as e:
            errors = parse_validation_errors(e, main_cm)

        assert len(errors) > 0
        for error in errors:
            assert error.yaml_source == "main_yaml_file"

    def test_mixed_errors_from_main_and_overlay(self):
        main_yaml = "cv:\n  name: John Doe\n  phone: not_a_valid_phone\n"
        design_yaml = "design:\n  theme: not_a_valid_theme\n"

        main_cm = read_yaml(main_yaml)
        design_cm = read_yaml(design_yaml)
        main_cm["design"] = design_cm["design"]
        overlay_sources = {"design": design_cm}

        try:
            RenderCVModel.model_validate(
                main_cm,
                context={"context": ValidationContext()},
            )
            pytest.fail("Expected ValidationError")
        except pydantic.ValidationError as e:
            errors = parse_validation_errors(e, main_cm, overlay_sources)

        cv_errors = [
            err
            for err in errors
            if err.schema_location is not None and err.schema_location[0] == "cv"
        ]
        design_errors = [
            err
            for err in errors
            if err.schema_location is not None and err.schema_location[0] == "design"
        ]

        assert len(cv_errors) > 0
        assert len(design_errors) > 0

        for err in cv_errors:
            assert err.yaml_source == "main_yaml_file"
        for err in design_errors:
            assert err.yaml_source == "design_yaml_file"


class TestGetInnerYamlObjectFromItsKey:
    def test_returns_object_and_coordinates_for_valid_key(self):
        yaml_content = "name: John\nage: 30"
        yaml_object = read_yaml(yaml_content)

        inner_object, coordinates = get_inner_yaml_object_from_its_key(
            yaml_object, "name"
        )

        assert inner_object == "John"
        assert len(coordinates) == 2
        assert len(coordinates[0]) == 2
        assert len(coordinates[1]) == 2

    def test_returns_object_and_coordinates_for_valid_list_index(self):
        yaml_content = "items:\n  - first\n  - second"
        yaml_object = read_yaml(yaml_content)
        items_list = yaml_object["items"]

        inner_object, coordinates = get_inner_yaml_object_from_its_key(items_list, "0")

        assert inner_object == "first"
        assert len(coordinates) == 2

    def test_raises_error_for_out_of_range_index(self):
        yaml_content = "items:\n  - first\n  - second"
        yaml_object = read_yaml(yaml_content)
        items_list = yaml_object["items"]

        with pytest.raises(RenderCVInternalError, match="Index 10 is out of range"):
            get_inner_yaml_object_from_its_key(items_list, "10")

    def test_raises_error_for_missing_key(self):
        yaml_content = "name: John"
        yaml_object = read_yaml(yaml_content)

        with pytest.raises(RenderCVInternalError, match="Key 'nonexistent' not found"):
            get_inner_yaml_object_from_its_key(yaml_object, "nonexistent")
