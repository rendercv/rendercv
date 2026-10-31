from typing import Any
from unittest.mock import MagicMock

import pydantic
import pytest

from rendercv.exception import RenderCVInternalError
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.cv.section import available_entry_type_names


class TestCv:
    @pytest.mark.parametrize(
        "website", ["https://example.com/", ["https://example.com/"]]
    )
    def test_websites_serialize_without_warnings(self, website):
        cv = Cv.model_validate({"website": website})
        assert cv.model_dump(mode="json", warnings="error")["website"] == website
        assert (
            Cv.model_validate_json(cv.model_dump_json(warnings="error")).website
            == cv.website
        )

    def test_rendercv_sections(self, request: pytest.FixtureRequest):
        entry_type_names = [
            "".join(
                ["_" + c.lower() if c.isupper() else c for c in entry_type_name]
            ).lstrip("_")
            for entry_type_name in available_entry_type_names
        ]
        sections = {
            f"arbitrary_title_{i}": [
                request.getfixturevalue(entry_type_name),
                request.getfixturevalue(entry_type_name),
            ]
            for i, entry_type_name in enumerate(entry_type_names)
        }
        input = {
            "name": "John Doe",
            "sections": sections,
        }

        cv = Cv.model_validate(input)

        assert len(cv.rendercv_sections) == len(available_entry_type_names)
        for section in cv.rendercv_sections:
            assert len(section.entries) == 2

    def test_rejects_section_with_mixed_entry_types(
        self, education_entry, experience_entry
    ):
        input = {
            "name": "John Doe",
            "sections": {
                "arbitrary_title": [
                    education_entry,
                    experience_entry,
                ],
            },
        }

        with pytest.raises(pydantic.ValidationError):
            Cv.model_validate(input)

    def test_rejects_invalid_entries(self):
        input: dict[str, Any] = {"name": "John Doe", "sections": {}}
        input["sections"]["section_title"] = [
            {
                "this": "is",
                "an": "invalid",
                "entry": 10,
            }
        ]

        with pytest.raises(pydantic.ValidationError):
            Cv.model_validate(input)

    def test_rejects_section_without_list(self):
        input: dict[str, Any] = {"name": "John Doe", "sections": {}}
        input["sections"]["section_title"] = {
            "this section": "does not have a list of entries but a single entry."
        }

        with pytest.raises(pydantic.ValidationError):
            Cv.model_validate(input)

    def test_empty_section(self):
        input_data = {"name": "John Doe", "sections": {"References": []}}
        cv = Cv.model_validate(input_data)
        assert len(cv.rendercv_sections) == 1
        section = cv.rendercv_sections[0]
        assert section.title == "References"
        assert section.entry_type == "TextEntry"
        assert section.entries == []

    def test_phone_serialization(self):
        input_data = {"name": "John Doe", "phone": "+905419999999"}
        cv = Cv.model_validate(input_data)
        serialized = cv.model_dump()

        assert "tel:" not in serialized["phone"]
        assert serialized["phone"] == "+90-541-999-99-99"

    @pytest.mark.parametrize("mode", ["python", "json"])
    @pytest.mark.parametrize(
        ("phone", "expected"),
        [
            (None, None),
            ([], []),
            ("+14155552671", "+1-415-555-2671"),
            (
                ["+14155552671", "+442071838750"],
                ["+1-415-555-2671", "+44-20-7183-8750"],
            ),
        ],
    )
    def test_phone_shapes_serialize_and_round_trip(self, mode, phone, expected):
        cv = Cv.model_validate({"phone": phone})
        serialized = cv.model_dump(mode=mode, warnings="error")
        assert serialized["phone"] == expected
        assert Cv.model_validate(serialized).phone == cv.phone
        assert (
            Cv.model_validate_json(cv.model_dump_json(warnings="error")).phone
            == cv.phone
        )

    def test_raises_internal_error_when_field_name_is_none(self):
        mock_info = MagicMock(spec=pydantic.ValidationInfo)
        mock_info.field_name = None

        with pytest.raises(RenderCVInternalError, match="field_name is None"):
            Cv.validate_list_or_scalar_fields("test@example.com", mock_info)
