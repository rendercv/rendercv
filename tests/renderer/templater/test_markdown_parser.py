import pytest

from rendercv.renderer.templater.markdown_parser import markdown_to_typst


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
            "Some other **tests, which should be *tricky* to parse!**",
            "Some other #strong[tests, which should be #emph[tricky] to parse!]",
        ),
        # (
        #     "One asterisk does not a quote* maketh",
        #     "One asterisk does not a quote#sym.ast.basic maketh",
        # ),
        # (
        #     "We can put asteri*sks in the middle of words",
        #     (
        #         "We can put asteri#sym.ast.basic#h(0pt, weak: true) sks in the middle"
        #         " of words"
        #     ),
        # ),
        # (
        #     (
        #         "If we want to escape \\*'s such that they don't become bold, we use a"
        #         " backslash: \\*"
        #     ),
        #     (
        #         "If we want to escape #sym.ast.basic#h(0pt, weak: true) 's such that"
        #         " they don't become bold, we use a backslash: #sym.ast.basic#h(0pt,"
        #         " weak: true) "
        #     ),
        # ),
        # (
        #     "Asterisk with a space after it does not need a zero-width space: * test",
        #     (
        #         "Asterisk with a space after it does not need a zero-width space:"
        #         " #sym.ast.basic test"
        #     ),
        # ),
        # (
        #     "Asterisk with a space after it does not need a zero-width space: *test",
        #     (
        #         "Asterisk with a space after it does not need a zero-width space:"
        #         " #sym.ast.basic#h(0pt, weak: true) test"
        #     ),
        # ),
        # (
        #     "\\* Asterisk should not be escaped\\*.Hey?",
        #     (
        #         "#sym.ast.basic Asterisk should not be escaped#sym.ast.basic#h(0pt,"
        #         " weak: true) .Hey?"
        #     ),
        # ),
        # (
        #     "I would like to not have any \\*\\*bold\\*\\* text",
        #     (
        #         "I would like to not have any #sym.ast.basic#h(0pt, weak: true)"
        #         " #sym.ast.basic#h(0pt, weak: true) bold#sym.ast.basic#h(0pt,"
        #         " weak: true) #sym.ast.basic text"
        #     ),
        # ),
        # (
        #     "Keep Typst commands #test-typst-command[argument] as they are.",
        #     "Keep Typst commands #test-typst-command[argument] as they are.",
        # ),
    ],
)
def test_markdown_to_typst(markdown_string, expected_typst_string):
    assert markdown_to_typst(markdown_string) == expected_typst_string
