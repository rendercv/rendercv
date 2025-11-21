import pytest

from rendercv.schema.override_dictionary import (
    apply_overrides_to_dictionary,
    update_value_by_location,
)


class TestUpdateValueByLocation:
    # Test simple dictionary updates
    @pytest.mark.parametrize(
        ("initial_dict", "key", "value", "expected"),
        [
            ({"name": "John"}, "name", "Jane", {"name": "Jane"}),
            ({"age": 30}, "age", "25", {"age": "25"}),
            ({}, "new_key", "new_value", {"new_key": "new_value"}),
        ],
    )
    def test_simple_dictionary_updates(self, initial_dict, key, value, expected):
        result = update_value_by_location(initial_dict, key, value, key)
        assert result == expected

    # Test nested dictionary updates
    @pytest.mark.parametrize(
        ("initial_dict", "key", "value", "expected"),
        [
            (
                {"user": {"name": "John"}},
                "user.name",
                "Jane",
                {"user": {"name": "Jane"}},
            ),
            (
                {"cv": {"sections": {"education": "MIT"}}},
                "cv.sections.education",
                "Harvard",
                {"cv": {"sections": {"education": "Harvard"}}},
            ),
            (
                {"a": {"b": {"c": {"d": "old"}}}},
                "a.b.c.d",
                "new",
                {"a": {"b": {"c": {"d": "new"}}}},
            ),
        ],
    )
    def test_nested_dictionary_updates(self, initial_dict, key, value, expected):
        result = update_value_by_location(initial_dict, key, value, key)
        assert result == expected

    # Test list updates
    @pytest.mark.parametrize(
        ("initial_list", "key", "value", "expected"),
        [
            (["a", "b", "c"], "0", "x", ["x", "b", "c"]),
            (["a", "b", "c"], "1", "y", ["a", "y", "c"]),
            (["a", "b", "c"], "2", "z", ["a", "b", "z"]),
        ],
    )
    def test_list_updates(self, initial_list, key, value, expected):
        result = update_value_by_location(initial_list, key, value, f"list.{key}")
        assert result == expected

    # Test mixed dictionary and list traversal
    @pytest.mark.parametrize(
        ("initial_dict", "key", "value", "expected"),
        [
            (
                {"items": ["a", "b", "c"]},
                "items.1",
                "updated",
                {"items": ["a", "updated", "c"]},
            ),
            (
                {"cv": {"sections": ["edu", "exp"]}},
                "cv.sections.0",
                "education",
                {"cv": {"sections": ["education", "exp"]}},
            ),
            (
                {"data": [{"name": "John"}, {"name": "Jane"}]},
                "data.0.name",
                "Bob",
                {"data": [{"name": "Bob"}, {"name": "Jane"}]},
            ),
            (
                {"cv": {"sections": {"education": [{"institution": "MIT"}]}}},
                "cv.sections.education.0.institution",
                "Harvard",
                {"cv": {"sections": {"education": [{"institution": "Harvard"}]}}},
            ),
        ],
    )
    def test_mixed_dict_list_traversal(self, initial_dict, key, value, expected):
        result = update_value_by_location(initial_dict, key, value, key)
        assert result == expected

    # Test error: non-integer index for list
    @pytest.mark.parametrize(
        ("initial_dict", "key", "full_key"),
        [
            ({"items": ["a", "b"]}, "items.invalid", "items.invalid"),
            ({"data": [1, 2, 3]}, "data.foo", "data.foo"),
        ],
    )
    def test_non_integer_index_for_list_raises_error(
        self, initial_dict, key, full_key
    ):
        with pytest.raises(ValueError, match=r"corresponds to a list, but .* is not an integer"):
            update_value_by_location(initial_dict, key, "value", full_key)

    # Test error: index out of range
    @pytest.mark.parametrize(
        ("initial_dict", "key", "full_key"),
        [
            ({"items": ["a", "b"]}, "items.5", "items.5"),
            ({"data": [1]}, "data.10", "data.10"),
        ],
    )
    def test_index_out_of_range_raises_error(self, initial_dict, key, full_key):
        with pytest.raises(IndexError, match=r"Index .* is out of range"):
            update_value_by_location(initial_dict, key, "value", full_key)

    # Test error: invalid structure (neither dict nor list)
    @pytest.mark.parametrize(
        ("initial_dict", "key", "full_key"),
        [
            ({"name": "John"}, "name.field", "name.field"),
            ({"age": 30}, "age.value", "age.value"),
        ],
    )
    def test_invalid_structure_raises_error(self, initial_dict, key, full_key):
        with pytest.raises(ValueError, match="It seems like there's something wrong"):
            update_value_by_location(initial_dict, key, "value", full_key)

    # Test that original structure is mutated (not copied)
    def test_mutates_original_structure(self):
        original = {"name": "John"}
        result = update_value_by_location(original, "name", "Jane", "name")
        assert result is original
        assert original == {"name": "Jane"}

    # Test deeply nested structures
    def test_deeply_nested_structure(self):
        initial = {
            "cv": {
                "sections": {
                    "education": [
                        {
                            "institution": "MIT",
                            "degree": "PhD",
                            "details": {"gpa": "4.0"},
                        }
                    ]
                }
            }
        }
        result = update_value_by_location(
            initial,
            "cv.sections.education.0.details.gpa",
            "3.9",
            "cv.sections.education.0.details.gpa",
        )
        assert result["cv"]["sections"]["education"][0]["details"]["gpa"] == "3.9"


class TestApplyOverridesToDictionary:
    # Test single override
    @pytest.mark.parametrize(
        ("initial_dict", "overrides", "expected"),
        [
            ({"name": "John"}, {"name": "Jane"}, {"name": "Jane"}),
            (
                {"cv": {"name": "John"}},
                {"cv.name": "Jane"},
                {"cv": {"name": "Jane"}},
            ),
            (
                {"items": ["a", "b"]},
                {"items.0": "x"},
                {"items": ["x", "b"]},
            ),
        ],
    )
    def test_single_override(self, initial_dict, overrides, expected):
        result = apply_overrides_to_dictionary(initial_dict, overrides)
        assert result == expected

    # Test multiple overrides
    @pytest.mark.parametrize(
        ("initial_dict", "overrides", "expected"),
        [
            (
                {"name": "John", "age": "30"},
                {"name": "Jane", "age": "25"},
                {"name": "Jane", "age": "25"},
            ),
            (
                {"cv": {"name": "John", "email": "john@example.com"}},
                {"cv.name": "Jane", "cv.email": "jane@example.com"},
                {"cv": {"name": "Jane", "email": "jane@example.com"}},
            ),
            (
                {"cv": {"sections": {"education": "MIT", "experience": "Google"}}},
                {"cv.sections.education": "Harvard", "cv.sections.experience": "Meta"},
                {"cv": {"sections": {"education": "Harvard", "experience": "Meta"}}},
            ),
        ],
    )
    def test_multiple_overrides(self, initial_dict, overrides, expected):
        result = apply_overrides_to_dictionary(initial_dict, overrides)
        assert result == expected

    # Test that original dictionary is not mutated
    def test_does_not_mutate_original(self):
        original = {"name": "John", "age": "30"}
        original_copy = {"name": "John", "age": "30"}
        overrides = {"name": "Jane"}

        result = apply_overrides_to_dictionary(original, overrides)

        assert original == original_copy  # Original unchanged
        assert result == {"name": "Jane", "age": "30"}  # Result has override
        assert result is not original  # Different objects

    # Test deep copy behavior (nested structures)
    def test_deep_copy_behavior(self):
        original = {"cv": {"sections": {"education": ["MIT"]}}}
        overrides = {"cv.sections.education.0": "Harvard"}

        result = apply_overrides_to_dictionary(original, overrides)

        # Original should not be affected
        assert original["cv"]["sections"]["education"][0] == "MIT"
        # Result should have the override
        assert result["cv"]["sections"]["education"][0] == "Harvard"

    # Test empty overrides
    def test_empty_overrides(self):
        original = {"name": "John", "age": "30"}
        result = apply_overrides_to_dictionary(original, {})
        assert result == original
        assert result is not original  # Still a copy

    # Test complex real-world scenario
    def test_complex_cv_scenario(self):
        initial = {
            "cv": {
                "name": "John Doe",
                "sections": {
                    "education": [
                        {
                            "institution": "MIT",
                            "degree": "PhD",
                            "start_date": "2020-01",
                        }
                    ],
                    "experience": [
                        {"company": "Google", "title": "Engineer"}
                    ],
                },
            }
        }
        overrides = {
            "cv.name": "Jane Doe",
            "cv.sections.education.0.institution": "Harvard",
            "cv.sections.education.0.start_date": "2021-01",
            "cv.sections.experience.0.company": "Meta",
        }

        result = apply_overrides_to_dictionary(initial, overrides)

        assert result["cv"]["name"] == "Jane Doe"
        assert result["cv"]["sections"]["education"][0]["institution"] == "Harvard"
        assert result["cv"]["sections"]["education"][0]["start_date"] == "2021-01"
        assert result["cv"]["sections"]["education"][0]["degree"] == "PhD"  # Unchanged
        assert result["cv"]["sections"]["experience"][0]["company"] == "Meta"
        assert result["cv"]["sections"]["experience"][0]["title"] == "Engineer"  # Unchanged
        # Original should remain unchanged
        assert initial["cv"]["name"] == "John Doe"
