import pydantic
import pytest

from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.cv.section import available_entry_type_names


def test_rendercv_sections(
    request: pytest.FixtureRequest,
):
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

    cv = Cv(**input)
    assert len(cv.rendercv_sections) == len(available_entry_type_names)
    for section in cv.rendercv_sections:
        assert len(section.entries) == 2


def test_section_with_different_entry_types(
    education_entry,
    experience_entry,
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
        Cv(**input)


def test_sections_with_invalid_entries():
    input = {"name": "John Doe", "sections": {}}
    input["sections"]["section_title"] = [
        {
            "this": "is",
            "an": "invalid",
            "entry": 10,
        }
    ]
    with pytest.raises(pydantic.ValidationError):
        Cv(**input)


def test_sections_without_list():
    input = {"name": "John Doe", "sections": {}}
    input["sections"]["section_title"] = {
        "this section": "does not have a list of entries but a single entry."
    }
    with pytest.raises(pydantic.ValidationError):
        Cv(**input)


def test_phone_serialization():
    input_data = {"name": "John Doe", "phone": "+905419999999"}
    cv = Cv.model_validate(input_data)

    # Serialize the model to trigger the phone serializer
    serialized = cv.model_dump()

    # The phone should be serialized without the tel: prefix
    assert "tel:" not in serialized["phone"]
    # Phone number is formatted by pydantic-phone-numbers
    assert serialized["phone"] == "+90-541-999-99-99"
