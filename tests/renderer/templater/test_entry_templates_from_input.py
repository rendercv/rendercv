from datetime import date as Date

import pydantic
import pytest

from rendercv.exception import RenderCVInternalError
from rendercv.renderer.templater.entry_templates_from_input import (
    clean_trailing_parts,
    process_authors,
    process_date,
    process_doi,
    process_highlights,
    process_summary,
    process_url,
    remove_not_provided_placeholders,
    render_entry_templates,
)
from rendercv.schema.models.cv.entries.normal import NormalEntry
from rendercv.schema.models.cv.entries.publication import PublicationEntry
from rendercv.schema.models.design.classic_theme import (
    NormalEntry as NormalEntryOptions,
)
from rendercv.schema.models.design.classic_theme import (
    PublicationEntry as PublicationEntryOptions,
)
from rendercv.schema.models.design.classic_theme import Templates
from rendercv.schema.models.locale.english_locale import EnglishLocale


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
                normal_entry=NormalEntryOptions(
                    main_column="START_DATE / END_DATE / LOCATION / DATE",
                )
            ),
            locale=EnglishLocale(),
            show_time_span=False,
            current_date=Date(2024, 1, 1),
        )

        assert entry.main_column == "Jan 2020 / Mar 2021 /  / Jan 2020 – Mar 2021"  # ty: ignore[unresolved-attribute]

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
                publication_entry=PublicationEntryOptions(
                    main_column="AUTHORS | DOI | DATE | OPTIONAL",
                )
            ),
            locale=EnglishLocale(),
            show_time_span=False,
            current_date=Date(2024, 1, 1),
        )

        assert (
            entry.main_column  # ty: ignore[unresolved-attribute]
            == "Alice, Bob | [10.1000/xyz123](https://doi.org/10.1000/xyz123) | Feb"
            " 2024"
        )

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
                normal_entry=NormalEntryOptions(
                    main_column="NAME URL OPTIONAL",
                )
            ),
            locale=EnglishLocale(),
            show_time_span=False,
            current_date=Date(2024, 1, 1),
        )

        assert (
            entry.main_column  # ty: ignore[unresolved-attribute]
            == "Linked Item [example.com/page](https://example.com/page/)"
        )


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
            {"main": "NAME |  | DATE"},
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
            {"main": "NAME  DATE"},
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
            {"main": "NAME  | START_DATE"},
        ),
        # Underscore placeholder with complex delimiters - "at" remains (letters are allowed)
        (
            {"main": "**JOB_TITLE** at COMPANY_NAME (LOCATION)"},
            {"JOB_TITLE": "Engineer"},
            {"main": "**JOB_TITLE** at"},
        ),
    ],
)
def test_remove_not_provided_placeholders(entry_templates, entry_fields, expected):
    result = remove_not_provided_placeholders(entry_templates, entry_fields)
    assert result == expected


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
