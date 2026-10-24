from datetime import date as Date
from unittest.mock import patch

import pydantic
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from rendercv.exception import RenderCVInternalError
from rendercv.renderer.templater.entry_templates_from_input import (
    clean_trailing_parts,
    process_authors,
    process_date,
    process_doi,
    process_highlights,
    process_summary,
    process_url,
    remove_connectors_of_missing_placeholders,
    remove_not_provided_placeholders,
    render_entry_templates,
)
from rendercv.schema.models.cv.entries.education import EducationEntry
from rendercv.schema.models.cv.entries.experience import ExperienceEntry
from rendercv.schema.models.cv.entries.normal import NormalEntry
from rendercv.schema.models.cv.entries.publication import PublicationEntry
from rendercv.schema.models.design.classic_theme import (
    EducationEntryTemplate,
    NormalEntryTemplate,
    PublicationEntryTemplate,
    Templates,
)
from rendercv.schema.models.locale.english_locale import EnglishLocale
from rendercv.schema.models.locale.locale import locale_adapter


@pytest.mark.parametrize(
    ("highlights", "expected"),
    [
        (
            ["First line", "Second line - Nested"],
            "- First line\n- Second line\n  - Nested",
        ),
        (["Single item"], "- Single item"),
        (["Item 1", "Item 2", "Item 3"], "- Item 1\n- Item 2\n- Item 3"),
        (
            ["Parent - Child 1", "Item 2 - Nested item"],
            "- Parent\n  - Child 1\n- Item 2\n  - Nested item",
        ),
    ],
)
def test_process_highlights(highlights, expected):
    result = process_highlights(highlights)
    assert result == expected


@pytest.mark.parametrize(
    ("authors", "expected"),
    [
        (["Alice", "Bob", "Charlie"], "Alice, Bob, Charlie"),
        (["Single Author"], "Single Author"),
        (["A", "B"], "A, B"),
    ],
)
def test_process_authors(authors, expected):
    assert process_authors(authors) == expected


class TestProcessDate:
    def test_appends_time_span_when_requested(self):
        result = process_date(
            date=None,
            start_date="2020-01-01",
            end_date="2021-02-01",
            locale=EnglishLocale(),
            show_time_span=True,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
            single_date_template="MONTH_ABBREVIATION YEAR",
            date_range_template="START_DATE – END_DATE",
            time_span_template="1 year 2 months",
        )

        assert result == "Jan 2020 – Feb 2021\n\n1 year 2 months"

    def test_skips_time_span_when_disabled(self):
        result = process_date(
            date=None,
            start_date="2020-01-01",
            end_date="2021-02-01",
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
            single_date_template="MONTH_ABBREVIATION YEAR",
            date_range_template="START_DATE – END_DATE",
            time_span_template="1 year 2 months",
        )

        assert result == "Jan 2020 – Feb 2021"

    def test_raises_error_when_no_dates_exist(self):
        with pytest.raises(RenderCVInternalError):
            process_date(
                date=None,
                start_date=None,
                end_date=None,
                locale=EnglishLocale(),
                show_time_span=True,
                compact_date_ranges_removing_start_year=False,
                current_date=Date(2024, 1, 1),
                single_date_template="MONTH_ABBREVIATION YEAR",
                date_range_template="START_DATE – END_DATE",
                time_span_template="1 year 2 months",
            )


class TestProcessUrl:
    def test_publication_prefers_doi_over_url(self):
        entry = PublicationEntry(
            title="Paper",
            authors=["Author"],
            doi="10.1/abc",
            url=pydantic.HttpUrl("https://example.com"),
        )

        result = process_url(entry)

        assert result == "[10.1/abc](https://doi.org/10.1/abc)"

    def test_returns_markdown_link_for_generic_url(self):
        entry = NormalEntry.model_validate(
            {"name": "Linked", "url": pydantic.HttpUrl("https://example.com/path/")}
        )

        result = process_url(entry)

        assert result == "[example.com/path](https://example.com/path/)"

    def test_raises_error_when_no_url_is_given(self):
        entry = NormalEntry(name="No link here")

        with pytest.raises(RenderCVInternalError):
            process_url(entry)


class TestProcessDoi:
    def test_returns_doi_link_when_present(self):
        entry = PublicationEntry(title="Paper", authors=["Author"], doi="10.1/abc")

        result = process_doi(entry)

        assert result == "[10.1/abc](https://doi.org/10.1/abc)"

    def test_raises_error_when_doi_missing(self):
        entry = PublicationEntry(
            title="Paper without DOI",
            authors=["Author"],
            url=pydantic.HttpUrl("https://example.com"),
        )

        with pytest.raises(RenderCVInternalError):
            process_doi(entry)


@pytest.mark.parametrize(
    ("summary", "expected"),
    [
        ("This is a summary", "!!! summary\n    This is a summary"),
        ("Short", "!!! summary\n    Short"),
        ("Multi word summary text", "!!! summary\n    Multi word summary text"),
        (
            "This is a multi-line summary\nwith two lines",
            "!!! summary\n    This is a multi-line summary\n    with two lines",
        ),
    ],
)
def test_process_summary(summary, expected):
    result = process_summary(summary)
    assert result == expected


class TestRenderEntryTemplates:
    def test_text_entry(self):
        text_entry = "Plain text entry"
        entry = render_entry_templates(
            text_entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert text_entry == entry

    def test_removes_missing_placeholders_and_doubles_newlines(self):
        entry = NormalEntry(name="Solo")

        entry = render_entry_templates(
            entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert entry.main_column == "**Solo**"  # ty: ignore[unresolved-attribute]
        assert entry.date_and_location_column == ""  # ty: ignore[unresolved-attribute]

    def test_populates_highlights_and_date_placeholders(self):
        entry = NormalEntry(
            name="Project",
            date="2023-05",
            highlights=["Alpha", "Beta"],
            location="Remote",
        )

        entry = render_entry_templates(
            entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=True,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert entry.main_column == "**Project**\n- Alpha\n- Beta"  # ty: ignore[unresolved-attribute]
        assert entry.date_and_location_column == "Remote\nMay 2023"  # ty: ignore[unresolved-attribute]

    def test_formats_start_and_end_dates_in_custom_template(self):
        entry = NormalEntry(
            name="Timeline",
            start_date="2020-01-01",
            end_date="2021-03-01",
        )

        entry = render_entry_templates(
            entry,
            templates=Templates(
                normal_entry=NormalEntryTemplate(
                    main_column="START_DATE / END_DATE / LOCATION / DATE",
                )
            ),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert entry.main_column == "Jan 2020 / Mar 2021 / / Jan 2020 – Mar 2021"  # ty: ignore[unresolved-attribute]

    def test_handles_authors_doi_and_date_placeholders(self):
        entry = PublicationEntry(
            title="My Paper",
            authors=["Alice", "Bob"],
            doi="10.1000/xyz123",
            date="2024-02-01",
        )

        entry = render_entry_templates(
            entry,
            templates=Templates(
                publication_entry=PublicationEntryTemplate(
                    main_column="AUTHORS | DOI | DATE | OPTIONAL",
                )
            ),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert (
            entry.main_column  # ty: ignore[unresolved-attribute]
            == "Alice, Bob | [10.1000/xyz123](https://doi.org/10.1000/xyz123) | Feb"
            " 2024"
        )

    def test_substitutes_locale_phrase_in_education_entry(self):
        entry = EducationEntry(
            institution="MIT",
            area="Computer Science",
            degree="BS",
            date="2024-05",
        )

        templates_with_phrase = Templates(
            education_entry=EducationEntryTemplate(
                main_column="**INSTITUTION**, DEGREE_WITH_AREA\nSUMMARY\nHIGHLIGHTS",
                degree_column=None,
            )
        )

        entry = render_entry_templates(
            entry,
            templates=templates_with_phrase,
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert "BS in Computer Science" in entry.main_column  # ty: ignore[unresolved-attribute]

    def test_substitutes_non_english_locale_phrase(self):
        entry = EducationEntry(
            institution="Sorbonne",
            area="Informatique",
            degree="Licence",
            date="2024-05",
        )

        french_locale = locale_adapter.validate_python({"language": "french"})
        templates_with_phrase = Templates(
            education_entry=EducationEntryTemplate(
                main_column="**INSTITUTION**, DEGREE_WITH_AREA\nSUMMARY\nHIGHLIGHTS",
                degree_column=None,
            )
        )

        entry = render_entry_templates(
            entry,
            templates=templates_with_phrase,
            locale=french_locale,
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert "Licence en Informatique" in entry.main_column  # ty: ignore[unresolved-attribute]

    def test_substitutes_locale_phrase_with_reversed_word_order(self):
        entry = EducationEntry(
            institution="University of Tokyo",
            area="Computer Science",
            degree="BS",
            date="2024-05",
        )

        japanese_locale = locale_adapter.validate_python({"language": "japanese"})
        templates_with_phrase = Templates(
            education_entry=EducationEntryTemplate(
                main_column="**INSTITUTION**, DEGREE_WITH_AREA\nSUMMARY\nHIGHLIGHTS",
                degree_column=None,
            )
        )

        entry = render_entry_templates(
            entry,
            templates=templates_with_phrase,
            locale=japanese_locale,
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert "Computer Science BS" in entry.main_column  # ty: ignore[unresolved-attribute]

    def test_creates_links_for_url_placeholders(self):
        entry = NormalEntry.model_validate(
            {
                "name": "Linked Item",
                "url": pydantic.HttpUrl("https://example.com/page/"),
            }
        )

        entry = render_entry_templates(
            entry,
            templates=Templates(
                normal_entry=NormalEntryTemplate(
                    main_column="NAME URL OPTIONAL",
                )
            ),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert (
            entry.main_column  # ty: ignore[unresolved-attribute]
            == "Linked Item [example.com/page](https://example.com/page/)"
        )

    @pytest.mark.parametrize(
        ("institution", "area", "expected_main_column"),
        [
            ("", "Computer Science", "Computer Science"),
            ("MIT", "", "**MIT**"),
            ("", "", ""),
        ],
    )
    def test_removes_formatting_around_empty_string_fields(
        self, institution, area, expected_main_column
    ):
        entry = EducationEntry(
            institution=institution,
            area=area,
            start_date="2020-01",
            end_date="2021-01",
        )

        entry = render_entry_templates(
            entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert entry.main_column == expected_main_column  # ty: ignore[unresolved-attribute]

    def test_removes_formatting_around_empty_name(self):
        entry = NormalEntry(name="")

        entry = render_entry_templates(
            entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert entry.main_column == ""  # ty: ignore[unresolved-attribute]
        assert entry.date_and_location_column == ""  # ty: ignore[unresolved-attribute]

    def test_removes_formatting_around_empty_position(self):
        entry = ExperienceEntry(
            company="Google",
            position="",
            start_date="2020-01",
            end_date="2021-01",
        )

        entry = render_entry_templates(
            entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert entry.main_column == "**Google**"  # ty: ignore[unresolved-attribute]

    def test_empty_summary_does_not_produce_admonition(self):
        entry = NormalEntry(name="Project", summary="")

        entry = render_entry_templates(
            entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert "!!!" not in entry.main_column  # ty: ignore[unresolved-attribute]
        assert entry.main_column == "**Project**"  # ty: ignore[unresolved-attribute]

    def test_inline_summary_not_wrapped_in_admonition(self):
        templates = Templates(
            experience_entry=Templates().experience_entry.model_copy(
                update={"main_column": "**COMPANY**, SUMMARY\nHIGHLIGHTS"}
            )
        )
        entry = ExperienceEntry(
            company="Google",
            position="Engineer",
            summary="Built search",
            start_date="2020-01",
            end_date="2021-01",
        )

        entry = render_entry_templates(
            entry,
            templates=templates,
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert "!!!" not in entry.main_column  # ty: ignore[unresolved-attribute]
        assert "Built search" in entry.main_column  # ty: ignore[unresolved-attribute]

    def test_standalone_summary_uses_admonition(self):
        entry = NormalEntry(name="Project", summary="Project description")

        entry = render_entry_templates(
            entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        assert "!!!" in entry.main_column  # ty: ignore[unresolved-attribute]


@pytest.mark.parametrize(
    ("entry_templates", "entry_fields", "expected"),
    [
        # All placeholders provided - no changes
        (
            {"main": "NAME - LOCATION"},
            {"NAME": "John", "LOCATION": "NYC"},
            {"main": "NAME - LOCATION"},
        ),
        # Single missing placeholder - trailing dash removed by clean_trailing_parts
        (
            {"main": "NAME - LOCATION"},
            {"NAME": "John"},
            {"main": "NAME"},
        ),
        # Missing placeholder - trailing space removed
        (
            {"main": "NAME (LOCATION)"},
            {"NAME": "John"},
            {"main": "NAME"},
        ),
        # Multiple missing placeholders - trailing comma removed
        (
            {"main": "NAME, LOCATION, DATE"},
            {"NAME": "John"},
            {"main": "NAME"},
        ),
        # Missing placeholder with various delimiters - no trailing cleanup needed
        (
            {"main": "NAME | LOCATION | DATE"},
            {"NAME": "John", "DATE": "2024"},
            {"main": "NAME | | DATE"},
        ),
        # Multiple templates - both get trailing parts cleaned
        (
            {"main": "NAME - LOCATION", "side": "DATE"},
            {"NAME": "John"},
            {"main": "NAME", "side": ""},
        ),
        # Placeholder at start - leading dash and space remain (not trailing)
        (
            {"main": "LOCATION - NAME"},
            {"NAME": "John"},
            {"main": " - NAME"},
        ),
        # No placeholders in template
        (
            {"main": "Just plain text"},
            {"NAME": "John"},
            {"main": "Just plain text"},
        ),
        # Empty template
        (
            {"main": ""},
            {"NAME": "John"},
            {"main": ""},
        ),
        # Placeholder with underscores - trailing space removed
        (
            {"main": "NAME START_DATE"},
            {"NAME": "John"},
            {"main": "NAME"},
        ),
        # Mixed case - only uppercase words are placeholders
        (
            {"main": "NAME Location DATE"},
            {"NAME": "John", "DATE": "2024"},
            {"main": "NAME Location DATE"},
        ),
        # All placeholders missing - empty line removed
        (
            {"main": "NAME LOCATION DATE"},
            {},
            {"main": ""},
        ),
        # Placeholder with no surrounding non-whitespace
        (
            {"main": "NAME LOCATION DATE"},
            {"NAME": "John", "DATE": "2024"},
            {"main": "NAME DATE"},
        ),
        # Complex surrounding characters - trailing dash removed
        (
            {"main": "**NAME** - [LOCATION] (DATE)"},
            {"NAME": "John"},
            {"main": "**NAME**"},
        ),
        # Realistic placeholder with underscores - trailing dashes removed
        (
            {"main": "COMPANY_NAME - JOB_TITLE", "side": "START_DATE - END_DATE"},
            {"COMPANY_NAME": "Acme Corp", "START_DATE": "2020"},
            {"main": "COMPANY_NAME", "side": "START_DATE"},
        ),
        # Multiple underscores in placeholder - trailing dash removed
        (
            {"main": "THIS_IS_A_LONG_KEY - ANOTHER_KEY"},
            {"THIS_IS_A_LONG_KEY": "Value"},
            {"main": "THIS_IS_A_LONG_KEY"},
        ),
        # Mix of underscore and non-underscore placeholders
        (
            {"main": "NAME (COMPANY_NAME) | START_DATE"},
            {"NAME": "John", "START_DATE": "2020"},
            {"main": "NAME | START_DATE"},
        ),
        # Connector word "at" removed because adjacent placeholder is missing
        (
            {"main": "**JOB_TITLE** at COMPANY_NAME (LOCATION)"},
            {"JOB_TITLE": "Engineer"},
            {"main": "**JOB_TITLE**"},
        ),
    ],
)
def test_remove_not_provided_placeholders(entry_templates, entry_fields, expected):
    result = remove_not_provided_placeholders(entry_templates, entry_fields)
    assert result == expected


class TestRemoveNotProvidedPlaceholders:
    @settings(deadline=None)
    @given(
        provided_key=st.from_regex(r"[A-Z]{2,10}", fullmatch=True),
        missing_key=st.from_regex(r"[A-Z]{2,10}", fullmatch=True),
        value=st.from_regex(r"[a-z ]{1,20}", fullmatch=True),
    )
    def test_provided_placeholders_survive(
        self, provided_key: str, missing_key: str, value: str
    ) -> None:
        assume(provided_key != missing_key)
        templates = {"main": f"{provided_key} {missing_key}"}
        fields = {provided_key: value}
        result = remove_not_provided_placeholders(templates, fields)
        assert provided_key in result["main"]

    @settings(deadline=None)
    @given(
        missing_key=st.from_regex(r"[A-Z]{2,10}", fullmatch=True),
    )
    def test_missing_placeholders_removed(self, missing_key: str) -> None:
        templates = {"main": f"PREFIX {missing_key} SUFFIX"}
        fields = {"PREFIX": "a", "SUFFIX": "b"}
        assume(missing_key not in ("PREFIX", "SUFFIX"))
        result = remove_not_provided_placeholders(templates, fields)
        assert missing_key not in result["main"]


class TestRenderEntryTemplatesInternalErrors:
    """Test defensive guards when model_dump includes a key but the attribute is None."""

    @pytest.mark.parametrize(
        ("entry_type", "field_name"),
        [
            ("education", "highlights"),
            ("publication", "authors"),
        ],
    )
    def test_raises_when_field_in_dump_but_attribute_is_none(
        self, entry_type, field_name
    ):
        if entry_type == "education":
            entry = EducationEntry.model_validate(
                {
                    "institution": "MIT",
                    "area": "CS",
                    "highlights": ["A"],
                    "start_date": "2020-01",
                    "end_date": "2021-01",
                }
            )
        else:
            entry = PublicationEntry.model_validate(
                {
                    "title": "Paper",
                    "authors": ["John"],
                    "date": "2024-01",
                }
            )

        # Set the attribute to None while model_dump still includes it
        original_model_dump = entry.model_dump

        def patched_model_dump(**kwargs):
            result = original_model_dump(**kwargs)
            result[field_name] = "placeholder"
            return result

        entry.model_dump = patched_model_dump  # ty: ignore[invalid-assignment]
        setattr(entry, field_name, None)

        with pytest.raises(RenderCVInternalError):
            render_entry_templates(
                entry,
                templates=Templates(),
                locale=EnglishLocale(),
                show_time_span=False,
                compact_date_ranges_removing_start_year=False,
                current_date=Date(2024, 1, 1),
            )

    @pytest.mark.parametrize("field_name", ["start_date", "end_date"])
    def test_raises_when_date_field_in_dump_but_attribute_is_none(self, field_name):
        entry = EducationEntry.model_validate(
            {
                "institution": "MIT",
                "area": "CS",
                "start_date": "2020-01",
                "end_date": "2021-01",
            }
        )

        original_model_dump = entry.model_dump

        def patched_model_dump(**kwargs):
            result = original_model_dump(**kwargs)
            result[field_name] = "placeholder"
            return result

        entry.model_dump = patched_model_dump  # ty: ignore[invalid-assignment]
        setattr(entry, field_name, None)

        with (
            patch(
                "rendercv.renderer.templater.entry_templates_from_input.process_date",
                return_value="Jan 2020 – Jan 2021",
            ),
            pytest.raises(RenderCVInternalError),
        ):
            render_entry_templates(
                entry,
                templates=Templates(),
                locale=EnglishLocale(),
                show_time_span=False,
                compact_date_ranges_removing_start_year=False,
                current_date=Date(2024, 1, 1),
            )


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        ("Hello---", "Hello"),
        ("World**", "World**"),  # ** is allowed
        ("Name_", "Name_"),  # underscore allowed
        ("Foo bar!!!???///", "Foo bar!!!???"),  # only trailing junk removed
        ("Ok..--", "Ok.."),  # trims only the trailing --
        ("(Test)]}", "(Test)]"),  # allowed chars kept
        ("Line!!***", "Line!!***"),  # trailing *** removed
        ("Line!%", "Line!%"),
        ("Just fine!", "Just fine!"),
        ("EndsWithDash - ", "EndsWithDash"),
        ("***", "***"),  # remains
        ("Mix\nBad+++", "Mix\nBad"),  # multiline behavior
    ],
)
def test_clean_trailing_parts(input_text, expected):
    assert clean_trailing_parts(input_text) == expected


class TestCleanTrailingParts:
    @settings(deadline=None)
    @given(
        text=st.text(
            alphabet=st.characters(
                categories=(), include_characters="abcdefghijABCDEF0123456789.!?[]()_*%"
            ),
            min_size=1,
            max_size=50,
        )
    )
    def test_allowed_trailing_chars_preserved(self, text: str) -> None:
        result = clean_trailing_parts(text)
        if result:
            assert result[-1] in "abcdefghijABCDEF0123456789.!?[]()_*%"

    @settings(deadline=None)
    @given(text=st.text(min_size=1, max_size=50))
    def test_never_crashes(self, text: str) -> None:
        clean_trailing_parts(text)


class TestRemoveConnectorsOfMissingPlaceholders:
    @pytest.mark.parametrize(
        ("template", "not_provided", "expected"),
        [
            # No missing placeholders — unchanged
            ("DEGREE in AREA", set(), "DEGREE in AREA"),
            # Connector "in" removed when left placeholder missing
            ("DEGREE in AREA", {"DEGREE"}, "DEGREE  AREA"),
            # Connector "en" removed (French)
            ("DEGREE en AREA", {"DEGREE"}, "DEGREE  AREA"),
            # Connector "in" removed when right placeholder missing
            ("DEGREE in AREA", {"AREA"}, "DEGREE  AREA"),
            # No connector word to remove (just space) — stays as-is
            ("AREA DEGREE", {"DEGREE"}, "AREA DEGREE"),
            # Formatting preserved, only connector word removed
            (
                "**INSTITUTION**, DEGREE in AREA -- LOCATION",
                {"DEGREE"},
                "**INSTITUTION**, DEGREE  AREA -- LOCATION",
            ),
            # Connector "at" removed between JOB_TITLE and COMPANY
            (
                "**JOB_TITLE** at COMPANY_NAME",
                {"COMPANY_NAME"},
                "**JOB_TITLE**  COMPANY_NAME",
            ),
            # No connector between placeholders separated by punctuation only
            ("NAME, LOCATION", {"LOCATION"}, "NAME, LOCATION"),
            # Hindi connector removed
            ("AREA \u092e\u0947\u0902 DEGREE", {"DEGREE"}, "AREA  DEGREE"),
            # Both sides missing — connector removed
            ("DEGREE in AREA", {"DEGREE", "AREA"}, "DEGREE  AREA"),
        ],
    )
    def test_removes_connector_words(self, template, not_provided, expected):
        assert (
            remove_connectors_of_missing_placeholders(template, not_provided)
            == expected
        )

    @settings(deadline=None)
    @given(
        connector=st.from_regex(r"[a-z]{2,8}", fullmatch=True),
    )
    def test_connector_removed_when_adjacent_placeholder_missing(
        self, connector: str
    ) -> None:
        template = f"PRESENT {connector} MISSING"
        result = remove_connectors_of_missing_placeholders(template, {"MISSING"})
        assert connector not in result

    @settings(deadline=None)
    @given(
        connector=st.from_regex(r"[a-z]{2,8}", fullmatch=True),
    )
    def test_connector_preserved_when_both_placeholders_present(
        self, connector: str
    ) -> None:
        template = f"LEFT {connector} RIGHT"
        result = remove_connectors_of_missing_placeholders(template, set())
        assert connector in result


class TestRenderEntryTemplatesWithMissingDegree:
    def test_no_connector_word_when_degree_is_none(self):
        entry = EducationEntry(
            institution="MIT",
            area="Computer Science",
            date="2024-05",
        )

        entry = render_entry_templates(
            entry,
            templates=Templates(
                education_entry=EducationEntryTemplate(
                    main_column=(
                        "**INSTITUTION**, DEGREE_WITH_AREA\nSUMMARY\nHIGHLIGHTS"
                    ),
                    degree_column=None,
                )
            ),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        main = entry.main_column  # ty: ignore[unresolved-attribute]
        assert "Computer Science" in main
        assert " in " not in main

    def test_no_connector_word_in_french_when_degree_is_none(self):
        entry = EducationEntry(
            institution="Sorbonne",
            area="Informatique",
            date="2024-05",
        )

        entry = render_entry_templates(
            entry,
            templates=Templates(
                education_entry=EducationEntryTemplate(
                    main_column=(
                        "**INSTITUTION**, DEGREE_WITH_AREA\nSUMMARY\nHIGHLIGHTS"
                    ),
                    degree_column=None,
                )
            ),
            locale=locale_adapter.validate_python({"language": "french"}),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        main = entry.main_column  # ty: ignore[unresolved-attribute]
        assert "Informatique" in main
        assert " en " not in main

    def test_no_connector_word_when_area_is_empty(self):
        entry = EducationEntry(
            institution="MIT",
            area="",
            degree="PhD",
            date="2024-05",
        )

        entry = render_entry_templates(
            entry,
            templates=Templates(
                education_entry=EducationEntryTemplate(
                    main_column=(
                        "**INSTITUTION**, DEGREE_WITH_AREA\nSUMMARY\nHIGHLIGHTS"
                    ),
                    degree_column=None,
                )
            ),
            locale=EnglishLocale(),
            show_time_span=False,
            compact_date_ranges_removing_start_year=False,
            current_date=Date(2024, 1, 1),
        )

        main = entry.main_column  # ty: ignore[unresolved-attribute]
        assert "PhD" in main
        assert " in " not in main
