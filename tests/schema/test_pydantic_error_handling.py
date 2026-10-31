import copy
from dataclasses import asdict
from typing import Annotated, Literal
from unittest.mock import MagicMock

import pydantic
import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic_core import ErrorDetails

from rendercv.exception import RenderCVInternalError
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.validation_context import ValidationContext
from rendercv.schema.override_dictionary import merge_overlay
from rendercv.schema.pydantic_error_handling import (
    contains_location,
    get_coordinates_of_a_key_in_a_yaml_object,
    get_inner_yaml_object_from_its_key,
    parse_plain_pydantic_error,
    parse_validation_errors,
    resolve_location,
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
        sources = [("design_yaml_file", design_cm)]

        try:
            RenderCVModel.model_validate(
                main_cm,
                context={"context": ValidationContext()},
            )
            pytest.fail("Expected ValidationError")
        except pydantic.ValidationError as e:
            errors = parse_validation_errors(e, main_cm, sources)

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
        sources = [("design_yaml_file", design_cm)]

        try:
            RenderCVModel.model_validate(
                main_cm,
                context={"context": ValidationContext()},
            )
            pytest.fail("Expected ValidationError")
        except pydantic.ValidationError as e:
            errors = parse_validation_errors(e, main_cm, sources)

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


class TestParseValidationErrorsWithMergedOverlays:
    def test_reports_errors_in_the_last_file_that_has_the_value(self):
        main_cm = read_yaml(
            "cv:\n  name: John Doe\n  email: john@example.com\n  phone: invalid\n"
        )
        overlay_cm = read_yaml("cv:\n  email: not_an_email\n")
        merge_overlay(main_cm, overlay_cm)

        try:
            RenderCVModel.model_validate(
                main_cm, context={"context": ValidationContext()}
            )
            pytest.fail("Expected ValidationError")
        except pydantic.ValidationError as e:
            errors = parse_validation_errors(e, main_cm, [("secrets.yaml", overlay_cm)])

        sources = {error.schema_location: error.yaml_source for error in errors}
        assert sources == {
            ("cv", "email"): "secrets.yaml",
            ("cv", "phone"): "main_yaml_file",
        }
        email_error = next(e for e in errors if e.schema_location == ("cv", "email"))
        assert email_error.yaml_location == ((2, 3), (2, 9))


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        ((), True),
        (("cv",), True),
        (("cv", "sections", "a", 1), True),
        (("cv", "sections", "a", 2), False),
        (("cv", "name"), False),
        (("cv", "sections", "a", "x"), False),
    ],
)
def test_contains_location(location, expected):
    document = {"cv": {"sections": {"a": ["x", "y"]}}}

    assert contains_location(document, location) is expected


class TestGetInnerYamlObjectFromItsKey:
    def test_returns_object_and_coordinates_for_valid_key(self):
        yaml_content = "name: John\nage: 30"
        yaml_object = read_yaml(yaml_content)

        inner_object, coordinates = get_inner_yaml_object_from_its_key(
            yaml_object, "name"
        )

        assert inner_object == "John"
        assert coordinates is not None
        assert len(coordinates) == 2
        assert len(coordinates[0]) == 2
        assert len(coordinates[1]) == 2

    def test_returns_object_and_coordinates_for_valid_list_index(self):
        yaml_content = "items:\n  - first\n  - second"
        yaml_object = read_yaml(yaml_content)
        items_list = yaml_object["items"]

        inner_object, coordinates = get_inner_yaml_object_from_its_key(items_list, "0")

        assert inner_object == "first"
        assert coordinates is not None
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


class TestStructuralErrorReporting:
    @pytest.mark.parametrize(
        "section",
        [
            "interests",
            "paintings",
            "internships",
            "distributed_systems",
            "0",
            "str",
            "list",
            "literal",
            "function-x",
            "tagged-union",
            "date",
        ],
    )
    def test_preserves_user_keys_and_nested_coordinates(self, section):
        data = read_yaml(f'cv:\n  sections:\n    "{section}":\n      - name: [bad]\n')
        with pytest.raises(pydantic.ValidationError) as exc:
            RenderCVModel.model_validate(data)
        errors = parse_validation_errors(exc.value, data)
        assert errors[-1].schema_location == ("cv", "sections", section, "0", "name")
        assert errors[-1].yaml_location == ((4, 9), (4, 14))

    def test_extra_keys_are_not_collapsed_into_one_error(self):
        data = read_yaml("cv: {interests: 1, paintings: 2, distributed_systems: 3}")
        with pytest.raises(pydantic.ValidationError) as exc:
            RenderCVModel.model_validate(data)
        errors = parse_validation_errors(exc.value, data)
        assert [e.schema_location for e in errors] == [
            ("cv", "interests"),
            ("cv", "paintings"),
            ("cv", "distributed_systems"),
        ]

    def test_root_error_has_coordinates_and_does_not_crash(self):
        data = read_yaml("cv: {}")
        error: ErrorDetails = {
            "type": "value_error",
            "loc": (),
            "msg": "Root error",
            "input": data,
        }
        result = parse_plain_pydantic_error(error, data)
        assert result.schema_location == ()
        assert result.yaml_location == ((1, 1), (1, 1))

    def test_plain_dictionaries_do_not_fabricate_coordinates(self):
        data = {"cv": {"sections": {"interests": [{"name": 3}]}}}
        with pytest.raises(pydantic.ValidationError) as exc:
            RenderCVModel.model_validate(data)
        assert all(
            e.yaml_location is None for e in parse_validation_errors(exc.value, data)
        )

    def test_conversion_is_pure_and_repeatable(self):
        data = read_yaml("cv: {sections: {interests: [{name: 3}]}}")
        with pytest.raises(pydantic.ValidationError) as exc:
            RenderCVModel.model_validate(data)
        original = copy.deepcopy(exc.value.errors())
        first = parse_validation_errors(exc.value, data)
        assert parse_validation_errors(exc.value, data) == first
        assert exc.value.errors() == original

    @pytest.mark.parametrize(
        "code",
        ["url_parsing", "color_error", "missing", "extra_forbidden", "list_type"],
    )
    def test_translations_do_not_depend_on_pydantic_english(self, code):
        data = read_yaml("value: bad")
        error: ErrorDetails = {
            "type": code,
            "loc": ("value",),
            "msg": "old prose",
            "input": "bad",
        }
        first = parse_plain_pydantic_error(error, data)
        changed = error.copy()
        changed["msg"] = "entirely new prose"
        assert parse_plain_pydantic_error(changed, data) == first
        assert error["msg"] == "old prose"

    def test_integer_parsing_is_not_mislabeled_as_a_date(self):
        error: ErrorDetails = {
            "type": "int_parsing",
            "loc": ("count",),
            "msg": (
                "Input should be a valid integer, unable to parse string as an integer"
            ),
            "input": "bad",
        }
        result = parse_plain_pydantic_error(error, {"count": "bad"})
        assert "date" not in result.message
        assert "integer" in result.message

    def test_field_names_do_not_change_the_message(self):
        error: ErrorDetails = {
            "type": "string_type",
            "loc": ("current_date_label",),
            "msg": "Input should be a valid string",
            "input": 3,
        }
        result = parse_plain_pydantic_error(error, {"current_date_label": 3})
        assert result.message == "Input should be a valid string."

    def test_preserves_distinct_errors_and_deduplicates_identical_rows(self):
        exception = MagicMock(spec=pydantic.ValidationError)
        error: ErrorDetails = {
            "type": "value_error",
            "loc": ("a",),
            "msg": "First problem!",
            "input": "bad",
        }
        exception.errors.return_value = [
            error,
            error.copy(),
            {**error, "msg": "Second problem"},
        ]
        assert [
            e.message for e in parse_validation_errors(exception, {"a": "bad"})
        ] == ["First problem!", "Second problem."]

    @pytest.mark.parametrize("field", ["email", "phone", "website"])
    def test_list_or_scalar_errors_keep_indices(self, field):
        for value, suffix in [("bad", ()), (["bad"], ("0",))]:
            data = {"cv": {field: value}}
            with pytest.raises(pydantic.ValidationError) as exc:
                RenderCVModel.model_validate(data)
            errors = parse_validation_errors(exc.value, data)
            assert len(errors) == 1
            assert errors[0].schema_location == ("cv", field, *suffix)

    def test_discriminated_union_at_arbitrary_depth(self):
        class First(pydantic.BaseModel):
            kind: Literal["first"]
            interests: str

        class Second(pydantic.BaseModel):
            kind: Literal["second"]
            count: int

        adapter = pydantic.TypeAdapter(
            Annotated[First | Second, pydantic.Field(discriminator="kind")]
        )
        data = read_yaml("kind: first\ninterests: 3")
        with pytest.raises(pydantic.ValidationError) as exc:
            adapter.validate_python(data)
        error = parse_validation_errors(exc.value, data)[0]
        assert error.schema_location == ("interests",)
        assert error.yaml_location == ((2, 1), (2, 11))

    @pytest.mark.parametrize(
        ("content", "expected"),
        [
            (
                "design: {theme: classic, classic: x, colors: {body: notacolor}}",
                ("design", "colors", "body"),
            ),
            (
                "locale: {language: english, english: x, present: 3}",
                ("locale", "present"),
            ),
        ],
    )
    def test_selector_names_cannot_steal_real_field_paths(self, content, expected):
        data = read_yaml(content)
        with pytest.raises(pydantic.ValidationError) as exc:
            RenderCVModel.model_validate(data)
        assert expected in [
            e.schema_location for e in parse_validation_errors(exc.value, data)
        ]

    def test_missing_field_keeps_its_name_and_points_to_parent(self):
        class Entry(pydantic.BaseModel):
            interests: str

        data = read_yaml("name: John")
        with pytest.raises(pydantic.ValidationError) as exc:
            Entry.model_validate(data)
        error = parse_validation_errors(exc.value, data)[0]
        assert error.schema_location == ("interests",)
        assert error.yaml_location == ((1, 1), (1, 1))

    @given(key=st.text(min_size=1))
    def test_location_projection_preserves_all_mapping_keys(self, key):
        data = {key: [{"leaf": 3}]}
        # Insert a branch label that is absent at each container level.
        branch = key + "_branch"
        if branch == "leaf":
            branch += "_"
        assert resolve_location(
            (branch, key, branch, 0, branch, "leaf", branch), data
        ) == (key, 0, "leaf")
        assert resolve_location((key, 0, "missing"), data, missing=True) == (
            key,
            0,
            "missing",
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("start_date", "2025-13-01", "The month must be between 1 and 12."),
        ("start_date", "2025-02-30", "The day is out of range for the month."),
        ("date", "2025-13-01", "The month must be between 1 and 12."),
        ("date", "2025-02-30", "The day is out of range for the month."),
        ("date", "0000-01", "The year must be between 1 and 9999."),
    ],
)
def test_calendar_diagnostics_keep_the_specific_component(field, value, message):
    data = {"cv": {"sections": {"interests": [{"name": "Job", field: value}]}}}
    with pytest.raises(pydantic.ValidationError) as exc:
        RenderCVModel.model_validate(data)
    assert parse_validation_errors(exc.value, data)[-1].message == message


def test_explains_doi_prefixes():
    publication = {"title": "Paper", "authors": ["Jane Doe"], "doi": "1109/TASC"}
    data = {"cv": {"sections": {"publications": [publication]}}}
    with pytest.raises(pydantic.ValidationError) as exc:
        RenderCVModel.model_validate(data)
    assert parse_validation_errors(exc.value, data)[-1].message == (
        'A DOI prefix should always start with "10.". For example,'
        ' "10.1109/TASC.2023.3340648".'
    )


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        (("cv", "name"), ((2, 3), (2, 8))),
        # A value that a command-line override added has no position in the file:
        (("cv", "email"), None),
    ],
)
def test_get_coordinates_of_a_key_in_a_yaml_object(location, expected):
    data = read_yaml("cv:\n  name: Jane Doe\n")
    assert get_coordinates_of_a_key_in_a_yaml_object(data, location) == expected
