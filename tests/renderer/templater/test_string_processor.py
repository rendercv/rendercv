import pytest

from rendercv.exception import RenderCVInternalError
from rendercv.renderer.templater.string_processor import (
    build_keyword_matcher_pattern,
    clean_url,
    make_keywords_bold,
    replace_date_placeholders,
    substitute_placeholders,
)


@pytest.mark.parametrize(
    ("text", "keywords", "expected"),
    [
        (
            "This is a test string with some keywords.",
            ["test", "keywords"],
            "This is a **test** string with some **keywords**.",
        ),
        ("No matches here.", ["test", "keywords"], "No matches here."),
        ("Python and python", ["Python"], "**Python** and python"),
        ("", ["test"], ""),
        ("Test word", [], "Test word"),
    ],
)
def test_make_keywords_bold(text, keywords, expected):
    assert make_keywords_bold(text, keywords) == expected


@pytest.mark.parametrize(
    ("string", "placeholders", "expected_string"),
    [
        ("Hello, NAME!", {"NAME": "World"}, "Hello, World!"),
        ("Hello, NAME!", {"NAME": None}, "Hello, !"),
        ("No placeholders here.", {}, "No placeholders here."),
    ],
)
def test_substitute_placeholders(string, placeholders, expected_string):
    assert substitute_placeholders(string, placeholders) == expected_string


@pytest.mark.parametrize(
    ("url", "expected_clean_url"),
    [
        ("https://example.com", "example.com"),
        ("https://example.com/", "example.com"),
        ("https://example.com/test", "example.com/test"),
        ("https://example.com/test/", "example.com/test"),
        ("https://www.example.com/test/", "www.example.com/test"),
    ],
)
def test_clean_url(url, expected_clean_url):
    assert clean_url(url) == expected_clean_url


def test_build_keyword_matcher_pattern_raises_error_for_empty_keywords():
    with pytest.raises(RenderCVInternalError) as exc_info:
        build_keyword_matcher_pattern(frozenset())

    assert "Keywords cannot be empty" in str(exc_info.value)


def test_replace_date_placeholders(monkeypatch):
    from datetime import date as real_date

    fake_today = real_date(2024, 3, 14)

    class FakeDate:
        @classmethod
        def today(cls):
            return fake_today

    monkeypatch.setattr(
        "rendercv.renderer.templater.string_processor.date", FakeDate
    )

    template = (
        "Report generated in MONTH_NAME (MONTH_ABBREVIATION), "
        "MONTH/MONTH_IN_TWO_DIGITS of YEAR (YEAR_IN_TWO_DIGITS)."
    )

    assert replace_date_placeholders(template) == (
        "Report generated in March (Mar), 3/03 of 2024 (24)."
    )
