from datetime import date as Date

import pydantic
import pytest

from rendercv.exception import RenderCVInternalError
from rendercv.renderer.templater.entry_templates_from_yaml import (
    clean_trailing_parts,
    process_authors,
    process_date,
    process_doi,
    process_highlights,
    process_summary,
    process_url,
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


@pytest.fixture
def current_date():
    return Date(2024, 1, 1)


class TestProcessHighlights:
    def test_formats_and_indents_nested_items(self):
        highlights = ["First line", "Second line - Nested"]

        result = process_highlights(highlights)

        assert result == "- First line\n- Second line\n  - Nested"


class TestProcessAuthors:
    def test_joins_authors_with_commas(self):
        assert process_authors(["Alice", "Bob", "Charlie"]) == "Alice, Bob, Charlie"


class TestProcessDate:
    def test_appends_time_span_when_requested(self, current_date):
        result = process_date(
            date=None,
            start_date="2020-01-01",
            end_date="2021-02-01",
            locale=EnglishLocale(),
            show_time_span=True,
            current_date=current_date,
            single_date_template="MONTH_ABBREVIATION YEAR",
            date_range_template="START_DATE – END_DATE",
            time_span_template="1 year 2 months",
        )

        assert result == "Jan 2020 – Feb 2021\n\n1 year 2 months"

    def test_skips_time_span_when_disabled(self, current_date):
        result = process_date(
            date=None,
            start_date="2020-01-01",
            end_date="2021-02-01",
            locale=EnglishLocale(),
            show_time_span=False,
            current_date=current_date,
            single_date_template="MONTH_ABBREVIATION YEAR",
            date_range_template="START_DATE – END_DATE",
            time_span_template="1 year 2 months",
        )

        assert result == "Jan 2020 – Feb 2021"

    def test_raises_error_when_no_dates_exist(self, current_date):
        with pytest.raises(RenderCVInternalError):
            process_date(
                date=None,
                start_date=None,
                end_date=None,
                locale=EnglishLocale(),
                show_time_span=True,
                current_date=current_date,
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


def test_process_summary():
    summary = "This is a summary"
    result = process_summary(summary)
    assert result == "!!! note\n    This is a summary"


class TestRenderEntryTemplates:
    def test_text_entry(self, current_date):
        text_entry = "Plain text entry"
        entry = render_entry_templates(
            text_entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=False,
            current_date=current_date,
        )

        assert text_entry == entry

    def test_removes_missing_placeholders_and_doubles_newlines(self, current_date):
        entry = NormalEntry(name="Solo")

        entry = render_entry_templates(
            entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=False,
            current_date=current_date,
        )

        assert entry.main_column == "**Solo**"  # pyright: ignore [reportAttributeAccessIssue]
        assert entry.date_and_location_column == ""  # pyright: ignore [reportAttributeAccessIssue]

    def test_populates_highlights_and_date_placeholders(self, current_date):
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
            current_date=current_date,
        )

        assert entry.main_column == "**Project**\n- Alpha\n- Beta"  # pyright: ignore [reportAttributeAccessIssue]
        assert entry.date_and_location_column == "Remote\nMay 2023"  # pyright: ignore [reportAttributeAccessIssue]

    def test_formats_start_and_end_dates_in_custom_template(self, current_date):
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
            current_date=current_date,
        )

        assert entry.main_column == "Jan 2020 / Mar 2021 /  / Jan 2020 – Mar 2021"  # pyright: ignore [reportAttributeAccessIssue]

    def test_handles_authors_doi_and_date_placeholders(self, current_date):
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
            current_date=current_date,
        )

        assert (
            entry.main_column  # pyright: ignore [reportAttributeAccessIssue]
            == "Alice, Bob | [10.1000/xyz123](https://doi.org/10.1000/xyz123) | Feb"
            " 2024"
        )

    def test_creates_links_for_url_placeholders(self, current_date):
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
            current_date=current_date,
        )

        assert (
            entry.main_column  # pyright: ignore [reportAttributeAccessIssue]
            == "Linked Item [example.com/page](https://example.com/page/)"
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
