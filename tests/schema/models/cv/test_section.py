import pydantic
import pytest

# They are called dynamically in the test with `eval(f"{entry_type}(**entry)")`.
from rendercv.schema.models.cv.entries.bullet import BulletEntry  # NOQA: F401
from rendercv.schema.models.cv.entries.education import EducationEntry  # NOQA: F401
from rendercv.schema.models.cv.entries.experience import ExperienceEntry  # NOQA: F401
from rendercv.schema.models.cv.entries.normal import NormalEntry  # NOQA: F401
from rendercv.schema.models.cv.entries.one_line import OneLineEntry  # NOQA: F401
from rendercv.schema.models.cv.entries.publication import PublicationEntry  # NOQA: F401
from rendercv.schema.models.cv.section import (
    Section,
    available_entry_models,
    dictionary_key_to_proper_section_title,
    get_entry_type_name_and_section_model,
)


@pytest.mark.parametrize(
    ("entry", "expected_entry_type", "expected_section_type"),
    [
        (
            "publication_entry",
            "PublicationEntry",
            "SectionWithPublicationEntries",
        ),
        (
            "experience_entry",
            "ExperienceEntry",
            "SectionWithExperienceEntries",
        ),
        (
            "education_entry",
            "EducationEntry",
            "SectionWithEducationEntries",
        ),
        (
            "normal_entry",
            "NormalEntry",
            "SectionWithNormalEntries",
        ),
        ("one_line_entry", "OneLineEntry", "SectionWithOneLineEntries"),
        ("text_entry", "TextEntry", "SectionWithTextEntries"),
        ("bullet_entry", "BulletEntry", "SectionWithBulletEntries"),
    ],
)
def test_get_entry_type_name_and_section_model(
    entry, expected_entry_type, expected_section_type, request: pytest.FixtureRequest
):
    entry = request.getfixturevalue(entry)
    entry_type, SectionModel = get_entry_type_name_and_section_model(entry)
    assert entry_type == expected_entry_type
    assert SectionModel.__name__ == expected_section_type

    # Initialize the entry with the entry type to test with model instances too
    if entry_type != "TextEntry":
        entry = eval(f"{entry_type}(**entry)")
        entry_type, SectionModel = get_entry_type_name_and_section_model(entry)
        assert entry_type == expected_entry_type
        assert SectionModel.__name__ == expected_section_type


@pytest.mark.parametrize(
    "EntryType",
    available_entry_models,
)
def test_entries_with_extra_attributes(EntryType, request: pytest.FixtureRequest):
    # Get the name of the class:
    entry_type_name: str = EntryType.__name__

    # Convert from camel case to snake case
    entry_type_name = "".join(
        ["_" + c.lower() if c.isupper() else c for c in entry_type_name]
    ).lstrip("_")

    # Get entry contents from fixture:
    entry_contents = request.getfixturevalue(entry_type_name)

    entry_contents["extra_attribute"] = "extra value"

    entry = EntryType(**entry_contents)

    assert entry.extra_attribute == "extra value"


@pytest.mark.parametrize(
    ("key", "expected_section_title"),
    [
        ("this_is_a_test", "This Is a Test"),
        ("welcome_to_rendercv!", "Welcome to Rendercv!"),
        ("Welcome to RenderCV!", "Welcome to RenderCV!"),
        ("\\faGraduationCap_education", "\\faGraduationCap_education"),
        ("\\faGraduationCap Education", "\\faGraduationCap Education"),
        ("Hello_World", "Hello_World"),
        ("Hello World", "Hello World"),
    ],
)
def test_dictionary_key_to_proper_section_title(key, expected_section_title):
    assert dictionary_key_to_proper_section_title(key) == expected_section_title


def test_section_rejects_none_entries():
    section_adapter = pydantic.TypeAdapter[Section](Section)
    with pytest.raises(pydantic.ValidationError):
        section_adapter.validate_python([None])
