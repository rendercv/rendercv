import pydantic
import pytest

from rendercv.schema.models.cv.cv import Cv


def test_rendercv_sections(
    education_entry,
    experience_entry,
    publication_entry,
    normal_entry,
    one_line_entry,
    text_entry,
):
    input = {
        "name": "John Doe",
        "sections": {
            "arbitrary_title": [
                education_entry,
                education_entry,
            ],
            "arbitrary_title_2": [
                experience_entry,
                experience_entry,
            ],
            "arbitrary_title_3": [
                publication_entry,
                publication_entry,
            ],
            "arbitrary_title_4": [
                normal_entry,
                normal_entry,
            ],
            "arbitrary_title_5": [
                one_line_entry,
                one_line_entry,
            ],
            "arbitrary_title_6": [
                text_entry,
                text_entry,
            ],
        },
    }

    cv = Cv(**input)
    assert len(cv.rendercv_sections) == 6
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
