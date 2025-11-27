from datetime import date as Date

import pydantic
import pytest

from rendercv.exception import RenderCVInternalError
from rendercv.renderer.templater.templates_from_yaml import (
    clean_trailing_parts,
    render_templates_of_entry,
    handle_authors,
    handle_date,
    handle_doi,
    handle_highlights,
    handle_start_or_end_date,
    handle_url,
)
from rendercv.schema.models.cv.entries.normal import NormalEntry
from rendercv.schema.models.cv.entries.publication import PublicationEntry
from rendercv.schema.models.design.classic_theme import NormalEntry
from rendercv.schema.models.locale.english_locale import EnglishLocale


@pytest.fixture
def current_date():
    return Date(2024, 1, 1)


class TestHandleHighlights:
    def test_formats_and_indents_nested_items(self):
        highlights = ["First line", "Second line - Nested"]

        result = handle_highlights(highlights)

        assert result == "- First line\n- Second line\n  - Nested"


class TestHandleAuthors:
    def test_joins_authors_with_commas(self):
        assert handle_authors(["Alice", "Bob", "Charlie"]) == "Alice, Bob, Charlie"


class TestHandleDate:
    def test_appends_time_span_when_requested(self, current_date):
        result = handle_date(
            None,
            "2020-01-01",
            "2021-02-01",
            EnglishLocale(),
            show_time_spans=True,
            current_date=current_date,
        )

        assert result == "Jan 2020 – Feb 2021\n\n1 year 2 months"

    def test_skips_time_span_when_disabled(self, current_date):
        result = handle_date(
            None,
            "2020-01-01",
            "2021-02-01",
            EnglishLocale(),
            show_time_spans=False,
            current_date=current_date,
        )

        assert result == "Jan 2020 – Feb 2021"

    def test_without_start_and_end_date(self, current_date):
        result = handle_date(
            "2023-05",
            None,
            None,
            EnglishLocale(),
            show_time_spans=True,
            current_date=current_date,
        )

        assert result == "May 2023"

    def test_raises_error_when_no_dates_exist(self, current_date):
        with pytest.raises(RenderCVInternalError):
            handle_date(
                None, None, None, EnglishLocale(), True, current_date=current_date
            )


class TestHandleStartOrEndDate:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [("2020-05-10", "May 2020"), (2023, "2023"), (None, RenderCVInternalError)],
    )
    def test_formats_start_or_end_date(self, value, expected):
        if expected == RenderCVInternalError:
            with pytest.raises(RenderCVInternalError):
                handle_start_or_end_date(value, EnglishLocale())
        else:
            assert handle_start_or_end_date(value, EnglishLocale()) == expected


class TestHandleUrl:
    def test_publication_prefers_doi_over_url(self):
        entry = PublicationEntry(
            title="Paper",
            authors=["Author"],
            doi="10.1/abc",
            url=pydantic.HttpUrl("https://example.com"),
        )

        result = handle_url(entry)

        assert result == "[10.1/abc](https://doi.org/10.1/abc)"

    def test_returns_markdown_link_for_generic_url(self):
        entry = NormalEntry.model_validate(
            {"name": "Linked", "url": pydantic.HttpUrl("https://example.com/path/")}
        )

        result = handle_url(entry)

        assert result == "[example.com/path](https://example.com/path/)"

    def test_raises_error_when_no_url_is_given(self):
        entry = NormalEntry(name="No link here")

        with pytest.raises(RenderCVInternalError):
            handle_url(entry)


class TestHandleDoi:
    def test_returns_doi_link_when_present(self):
        entry = PublicationEntry(title="Paper", authors=["Author"], doi="10.1/abc")

        result = handle_doi(entry)

        assert result == "[10.1/abc](https://doi.org/10.1/abc)"

    def test_raises_error_when_doi_missing(self):
        entry = PublicationEntry(
            title="Paper without DOI",
            authors=["Author"],
            url=pydantic.HttpUrl("https://example.com"),
        )

        with pytest.raises(RenderCVInternalError):
            handle_doi(entry)


class TestComputeEntryTemplates:
    def test_returns_empty_dict_for_text_entries(self, current_date):
        templates = render_templates_of_entry(
            "Plain text entry",
            NormalEntryOptions(),
            EnglishLocale(),
            True,
            current_date=current_date,
        )

        assert templates == {}

    def test_removes_missing_placeholders_and_doubles_newlines(self, current_date):
        entry = NormalEntry(name="Solo")

        templates = render_templates_of_entry(
            entry,
            NormalEntryOptions(),
            EnglishLocale(),
            False,
            current_date=current_date,
        )

        assert templates == {
            "main_column_template": "**Solo**",
            "date_and_location_column_template": "",
        }

    def test_populates_highlights_and_date_placeholders(self, current_date):
        entry = NormalEntry(
            name="Project",
            date="2023-05",
            highlights=["Alpha", "Beta"],
            location="Remote",
        )

        templates = render_templates_of_entry(
            entry,
            NormalEntryOptions(),
            EnglishLocale(),
            True,
            current_date=current_date,
        )

        assert templates == {
            "main_column_template": "**Project**\n- Alpha\n- Beta",
            "date_and_location_column_template": "Remote\nMay 2023",
        }

    def test_formats_start_and_end_dates_in_custom_template(self, current_date):
        class TimelineOptions(pydantic.BaseModel):
            timeline_template: str = "START_DATE / END_DATE / LOCATION / DATE"

        entry = NormalEntry(
            name="Timeline",
            start_date="2020-01-01",
            end_date="2021-03-01",
        )

        templates = render_templates_of_entry(
            entry, TimelineOptions(), EnglishLocale(), False, current_date=current_date
        )

        assert templates == {
            "timeline_template": "Jan 2020 / Mar 2021 /  / Jan 2020 – Mar 2021"
        }

    def test_handles_authors_doi_and_date_placeholders(self, current_date):
        class PublicationTemplates(pydantic.BaseModel):
            citation_template: str = "AUTHORS | DOI | DATE | OPTIONAL"

        entry = PublicationEntry(
            title="My Paper",
            authors=["Alice", "Bob"],
            doi="10.1000/xyz123",
            date="2024-02-01",
        )

        templates = render_templates_of_entry(
            entry,
            PublicationTemplates(),
            EnglishLocale(),
            False,
            current_date=current_date,
        )

        assert templates == {
            "citation_template": (
                "Alice, Bob | [10.1000/xyz123](https://doi.org/10.1000/xyz123)"
                " | Feb 2024"
            )
        }

    def test_creates_links_for_url_placeholders(self, current_date):
        class LinkTemplates(pydantic.BaseModel):
            link_template: str = "NAME URL OPTIONAL"

        entry = NormalEntry.model_validate(
            {
                "name": "Linked Item",
                "url": pydantic.HttpUrl("https://example.com/page/"),
            }
        )

        templates = render_templates_of_entry(
            entry, LinkTemplates(), EnglishLocale(), False, current_date=current_date
        )

        assert templates == {
            "link_template": "Linked Item [example.com/page](https://example.com/page/)"
        }


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
        ("Just fine!", "Just fine!"),
        ("EndsWithDash - ", "EndsWithDash"),
        ("***", "***"),  # remains
        ("Mix\nBad+++", "Mix\nBad"),  # multiline behavior
    ],
)
def test_clean_trailing_parts(input_text, expected):
    assert clean_trailing_parts(input_text) == expected
