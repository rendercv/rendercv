import pytest

from rendercv.renderer.templater.string_processor import (
    clean_url,
    make_keywords_bold,
    substitute_placeholders,
)


def test_make_keywords_bold():
    assert (
        make_keywords_bold(
            "This is a test string with some keywords.",
            ["test", "keywords"],
        )
        == "This is a **test** string with some **keywords**."
    )


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
