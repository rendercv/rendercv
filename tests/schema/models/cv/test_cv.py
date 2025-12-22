from typing import Any

import pydantic
import pytest

from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.cv.section import available_entry_type_names


class TestCv:
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

    def test_phone_serialization(self):
        input_data = {"name": "John Doe", "phone": "+905419999999"}
        cv = Cv.model_validate(input_data)
        serialized = cv.model_dump()

        assert "tel:" not in serialized["phone"]
        assert serialized["phone"] == "+90-541-999-99-99"
