import pytest

from rendercv.renderer.templater.text_processor import (
    clean_url,
    make_keywords_bold,
    markdown_to_typst,
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
    ("markdown_string", "expected_typst_string"),
    [
        ("My Text", "My Text"),
        ("**My** Text", "#strong[My] Text"),
        ("*My* Text", "#emph[My] Text"),
        ("***My*** Text", "#strong[#emph[My]] Text"),
        ("[My](https://myurl.com) Text", '#link("https://myurl.com")[My] Text'),
        ("`My` Text", "`My` Text"),
        (
            "[**My** *Text* ***Is*** `Here`](https://myurl.com)",
            (
                '#link("https://myurl.com")[#strong[My] #emph[Text] #strong[#emph[Is]]'
                " `Here`]"
            ),
        ),
        (
            "Some other *** tests, which should be tricky* to parse!**",
            "Some other #strong[#emph[ tests, which should be tricky] to parse!]",
        ),
        (
            "One asterisk does not a quote* maketh",
            "One asterisk does not a quote#sym.ast.basic maketh",
        ),
        (
            "We can put asteri*sks in the middle of words",
            (
                "We can put asteri#sym.ast.basic#h(0pt, weak: true) sks in the middle"
                " of words"
            ),
        ),
        (
            (
                "If we want to escape \\*'s such that they don't become bold, we use a"
                " backslash: \\*"
            ),
            (
                "If we want to escape #sym.ast.basic#h(0pt, weak: true) 's such that"
                " they don't become bold, we use a backslash: #sym.ast.basic#h(0pt,"
                " weak: true) "
            ),
        ),
        (
            "Asterisk with a space after it does not need a zero-width space: * test",
            (
                "Asterisk with a space after it does not need a zero-width space:"
                " #sym.ast.basic test"
            ),
        ),
        (
            "Asterisk with a space after it does not need a zero-width space: *test",
            (
                "Asterisk with a space after it does not need a zero-width space:"
                " #sym.ast.basic#h(0pt, weak: true) test"
            ),
        ),
        (
            "\\* Asterisk should not be escaped\\*.Hey?",
            (
                "#sym.ast.basic Asterisk should not be escaped#sym.ast.basic#h(0pt,"
                " weak: true) .Hey?"
            ),
        ),
        (
            "I would like to not have any \\*\\*bold\\*\\* text",
            (
                "I would like to not have any #sym.ast.basic#h(0pt, weak: true)"
                " #sym.ast.basic#h(0pt, weak: true) bold#sym.ast.basic#h(0pt,"
                " weak: true) #sym.ast.basic text"
            ),
        ),
        (
            "Keep Typst commands #test-typst-command[argument] as they are.",
            "Keep Typst commands #test-typst-command[argument] as they are.",
        ),
    ],
)
def test_markdown_to_typst(markdown_string, expected_typst_string):
    assert markdown_to_typst(markdown_string) == expected_typst_string
