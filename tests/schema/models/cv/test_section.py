from functools import cache

import jsonschema
import pydantic
import pydantic_core
import pytest
from hypothesis import given
from hypothesis import strategies as st

from rendercv.schema.json_schema_generator import generate_json_schema

# They are called dynamically in the test with `eval(f"{entry_type}(**entry)")`.
from rendercv.schema.models.cv.entries.bullet import BulletEntry  # NOQA: F401
from rendercv.schema.models.cv.entries.education import EducationEntry  # NOQA: F401
from rendercv.schema.models.cv.entries.experience import ExperienceEntry  # NOQA: F401
from rendercv.schema.models.cv.entries.normal import NormalEntry  # NOQA: F401
from rendercv.schema.models.cv.entries.one_line import OneLineEntry  # NOQA: F401
from rendercv.schema.models.cv.entries.publication import PublicationEntry
from rendercv.schema.models.cv.entries.reversed_numbered import ReversedNumberedEntry
from rendercv.schema.models.cv.section import (
    BaseRenderCVSection,
    Section,
    SubsectionEntry,
    available_entry_models,
    build_rendercv_section,
    dictionary_key_to_proper_section_title,
    get_entry_type_name_and_section_model,
    get_rendercv_sections,
    is_subsection_entry,
    validate_section,
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


class TestDictionaryKeyToProperSectionTitle:
    @given(
        key=st.from_regex(r"[a-z]{1,5}(_[a-z]{1,5}){0,3}", fullmatch=True),
    )
    def test_snake_case_replaces_underscores_with_spaces(self, key: str) -> None:
        result = dictionary_key_to_proper_section_title(key)
        assert "_" not in result
        assert " " in result or len(key.split("_")) == 1

    @given(
        parts=st.lists(
            st.from_regex(r"[a-zA-Z0-9]{1,10}", fullmatch=True),
            min_size=2,
            max_size=5,
        )
    )
    def test_keys_with_spaces_returned_unchanged(self, parts: list[str]) -> None:
        key = " ".join(parts)
        assert dictionary_key_to_proper_section_title(key) == key

    @given(
        key=st.from_regex(r"[a-zA-Z]*[A-Z][a-zA-Z]*", fullmatch=True).filter(
            lambda s: " " not in s and len(s) <= 30
        )
    )
    def test_keys_with_uppercase_returned_unchanged(self, key: str) -> None:
        assert dictionary_key_to_proper_section_title(key) == key


def test_section_rejects_none_entries():
    section_adapter = pydantic.TypeAdapter[Section](Section)
    with pytest.raises(pydantic.ValidationError):
        section_adapter.validate_python([None])


def test_section_accepts_empty_list():
    section_adapter = pydantic.TypeAdapter[Section](Section)
    result = section_adapter.validate_python([])
    assert result == []


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        ({"title": "Talks", "entries": []}, True),
        ({"entries": ["A talk."]}, True),
        (SubsectionEntry(title="Talks", entries=[]), True),
        ({"title": "A Paper", "authors": ["J. Doe"]}, False),
        ("A text entry.", False),
        (None, False),
    ],
)
def test_is_subsection_entry(entry, expected):
    assert is_subsection_entry(entry) is expected


def test_get_entry_type_name_and_section_model_detects_subsections():
    entry_type, SectionModel = get_entry_type_name_and_section_model(
        {"title": "Talks", "entries": []}
    )

    assert entry_type == "SubsectionEntry"
    assert SectionModel.__name__ == "SectionWithSubsectionEntries"


class TestValidateSection:
    def test_detects_the_entry_type_of_each_subsection(self):
        section = validate_section(
            [
                {
                    "title": "Papers",
                    "entries": [{"title": "A Paper", "authors": ["J. Doe"]}],
                },
                {"title": "Talks", "entries": ["A talk."]},
            ]
        )

        assert section == [
            SubsectionEntry(
                title="Papers",
                entries=[PublicationEntry(title="A Paper", authors=["J. Doe"])],
            ),
            SubsectionEntry(title="Talks", entries=["A talk."]),
        ]

    @pytest.mark.parametrize(
        "section",
        [
            [{"title": "Talks", "entries": ["A talk."]}, "An entry."],
            ["An entry.", {"title": "Talks", "entries": ["A talk."]}],
        ],
    )
    def test_rejects_entries_mixed_with_subsections(self, section):
        with pytest.raises(pydantic_core.PydanticCustomError, match="problems"):
            validate_section(section)

    def test_reports_the_problems_of_the_entries_of_subsections(self):
        with pytest.raises(pydantic_core.PydanticCustomError) as exception_info:
            validate_section([{"title": "Papers", "entries": [{"title": "A Paper"}]}])

        context = exception_info.value.context
        assert context is not None
        [subsection_error] = context["caused_by"]
        [entry_error] = subsection_error["ctx"]["caused_by"]
        assert subsection_error["loc"] == ("entries", 0, "entries")
        assert entry_error["loc"] == ("entries", 0, "authors")

    def test_rejects_subsections_with_other_keys(self):
        with pytest.raises(pydantic_core.PydanticCustomError) as exception_info:
            validate_section([{"title": "Talks", "entries": [], "name": "Talks"}])

        context = exception_info.value.context
        assert context is not None
        [error] = context["caused_by"]
        assert error["type"] == "extra_forbidden"


def test_subsection_entries_can_contain_subsection_entries():
    entries = ["A talk."]
    for depth in range(8):
        entries = [{"title": f"Group {depth}", "entries": entries}]

    section = validate_section(entries)
    rendered = build_rendercv_section("Talks", section)
    for depth in reversed(range(8)):
        [entry] = section
        [rendered_entry] = rendered.entries
        assert isinstance(entry, SubsectionEntry)
        assert entry.title == rendered_entry.title == f"Group {depth}"
        section = entry.entries
        rendered = rendered_entry
    assert section == rendered.entries == ["A talk."]


section_text = st.text(alphabet="abc XYZé中文", min_size=1, max_size=12)
recursive_entries = st.recursive(
    st.lists(section_text, max_size=4)
    | st.lists(st.fixed_dictionaries({"bullet": section_text}), max_size=4),
    lambda children: st.lists(
        st.fixed_dictionaries({"title": section_text, "entries": children}),
        min_size=1,
        max_size=3,
    ),
    max_leaves=20,
)


@cache
def section_validators():
    return (
        pydantic.TypeAdapter[Section](Section),
        jsonschema.Draft7Validator(generate_json_schema()),
    )


@given(entries=recursive_entries)
def test_recursive_sections_preserve_content_and_match_editor_schema(entries):
    adapter, schema = section_validators()
    schema.validate({"cv": {"sections": {"work": entries}}})
    validated = adapter.validate_python(entries)
    assert adapter.dump_python(validated, exclude_unset=True) == entries

    def verify_rendered(source, rendered):
        assert len(source) == len(rendered.entries)
        for expected, actual in zip(source, rendered.entries, strict=True):
            if isinstance(expected, dict) and "entries" in expected:
                assert actual.title == expected["title"]
                verify_rendered(expected["entries"], actual)
            elif isinstance(expected, dict):
                assert actual.model_dump(exclude_unset=True) == expected
            else:
                assert actual == expected

    verify_rendered(entries, build_rendercv_section("Work", validated))


class TestBuildRendercvSection:
    def test_builds_a_section_of_subsections(self):
        section = build_rendercv_section(
            "Publications",
            [
                SubsectionEntry(
                    title="Papers",
                    entries=[PublicationEntry(title="A Paper", authors=["J. Doe"])],
                ),
                SubsectionEntry(title="Empty", entries=[]),
            ],
        )

        assert section == BaseRenderCVSection(
            title="Publications",
            entry_type="SubsectionEntry",
            entries=[
                BaseRenderCVSection(
                    title="Papers",
                    entry_type="PublicationEntry",
                    entries=[PublicationEntry(title="A Paper", authors=["J. Doe"])],
                ),
                BaseRenderCVSection(title="Empty", entry_type="TextEntry", entries=[]),
            ],
        )

    def test_builds_a_section_of_entries(self):
        entries = [ReversedNumberedEntry(reversed_number="An entry.")]

        section = build_rendercv_section("Talks", entries)

        assert section.entry_type == "ReversedNumberedEntry"
        assert section.entries == entries


def test_get_rendercv_sections_formats_section_titles_but_not_subsection_titles():
    sections = get_rendercv_sections(
        {"selected_work": [SubsectionEntry(title="open_source", entries=[])]}
    )

    assert sections[0].title == "Selected Work"
    assert sections[0].entries[0].title == "open_source"
