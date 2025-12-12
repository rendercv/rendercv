import pytest

from rendercv.renderer.templater.markdown_parser import (
    escape_typst_characters,
    markdown_to_html,
    markdown_to_typst,
)


class TestEscapeTypstCharacters:
    def test_returns_newline_unchanged(self):
        assert escape_typst_characters("\n") == "\n"

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("#", r"\#"),
            ("$", r"\$"),
            ("[", r"\["),
            ("]", r"\]"),
            ("\\", r"\\"),
            ('"', r"\""),
            ("@", r"\@"),
            ("%", r"\%"),
            ("~", r"\~"),
            ("_", r"\_"),
            ("/", r"\/"),
            (">", r"\>"),
            ("<", r"\<"),
        ],
    )
    def test_escapes_typst_special_characters(self, string, expected):
        assert escape_typst_characters(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("* test", "#sym.ast.basic test"),
            ("*test", "#sym.ast.basic#h(0pt, weak: true) test"),
        ],
    )
    def test_replaces_asterisks_with_typst_symbols(self, string, expected):
        assert escape_typst_characters(string) == expected

    def test_preserves_typst_commands_while_escaping_outside(self):
        string = "Keep #emph[a_b] but escape 5% and _"
        expected = "Keep #emph[a_b] but escape 5\\% and \\_"

        assert escape_typst_characters(string) == expected

    def test_preserves_math_blocks(self):
        string = "$$a*b + c$$ and #1"
        expected = "$a*b + c$ and \\#1"

        assert escape_typst_characters(string) == expected


@pytest.mark.parametrize(
    ("markdown_string", "expected_typst_string"),
    [
        ("plain", "plain"),
        ("**b**", "#strong[b]"),
        ("*i*", "#emph[i]"),
        ("***x***", "#strong[#emph[x]]"),
        ("`c`", "`c`"),
        ("[x](https://myurl.com)", '#link("https://myurl.com")[x]'),
        (
            "[**b** *i* ***bi*** `c`](https://myurl.com)",
            '#link("https://myurl.com")[#strong[b] #emph[i] #strong[#emph[bi]] `c`]',
        ),
        ("**a *b* c**", "#strong[a #emph[b] c]"),
        (
            "quote*",
            "quote#sym.ast.basic#h(0pt, weak: true)",
        ),
        (
            "asteri*sks",
            "asteri#sym.ast.basic#h(0pt, weak: true) sks",
        ),
        (
            "* test",
            "#sym.ast.basic test",
        ),
        (
            "*test",
            "#sym.ast.basic#h(0pt, weak: true) test",
        ),
        (
            r"\*'s",
            "#sym.ast.basic#h(0pt, weak: true) 's",
        ),
        (
            r"\* x",
            "#sym.ast.basic x",
        ),
        (
            r"\*.x",
            "#sym.ast.basic#h(0pt, weak: true) .x",
        ),
        (
            r"\*\*bold\*\*",
            (
                "#sym.ast.basic#h(0pt, weak: true) "
                "#sym.ast.basic#h(0pt, weak: true) "
                "bold#sym.ast.basic#h(0pt, weak: true) "
                "#sym.ast.basic#h(0pt, weak: true)"
            ),
        ),
        # Typst commands should be preserved
        (
            "#test-typst-command[argument]",
            "#test-typst-command[argument]",
        ),
        (
            "#test-typst-command",
            "#test-typst-command",
        ),
        (
            "#test-typst-command(a, b)",
            "#test-typst-command(a, b)",
        ),
        (
            "#test-typst-command(a, b)[c, d]",
            "#test-typst-command(a, b)[c, d]",
        ),
        # things that look like commands but aren't:
        ("#1", r"\#1"),
        ("I made $100", r"I made \$100"),
        # inside math: no escaping, keep everything as is:
        (
            r"$$a*b * c #cmd[x]$$",
            r"$a*b * c #cmd[x]$",
        ),
        ("My # Text", "My \\# Text"),
        ("My % Text", "My \\% Text"),
        ("My ~ Text", "My \\~ Text"),
        ("My _ Text", "My \\_ Text"),
        ("My $ Text", "My \\$ Text"),
        ("My [ Text", "My \\[ Text"),
        ("My ] Text", "My \\] Text"),
        ("My \\ Text", "My \\\\ Text"),
        ('My " Text', 'My \\" Text'),
        ("My @ Text", "My \\@ Text"),
        (
            "[link_test#](Shouldn't be escaped in here & % # ~)",
            '#link("Shouldn\'t be escaped in here & % # ~")[link\\_test\\#]',
        ),
        (
            "$$a=5_4^3 % & #$$ # $$aaaa ___ &&$$",
            "$a=5_4^3 % & #$ \\# $aaaa ___ &&$",
        ),
        ("60%", "60\\%"),
        (
            (
                "!!! summary\n"
                "    Did #emph[this] and this is a #strong[bold]"
                ' #link("https://example.com")[link]. But I must explain to you how all'
                " this mistaken idea of denouncing pleasure and praising pain was born"
                " and I will give you a complete account of the system, and expound the"
                " actual teachings of the great explorer of the truth, the"
                " master-builder of human happiness. No one rejects, dislikes, or"
                " avoids pleasure itself, because it is pleasure, but because those who"
                " do not know how to pursue pleasure rationally encounter consequences"
                " that are extremely painful."
            ),
            (
                "#summary[Did #emph[this] and this is a #strong[bold]"
                ' #link("https://example.com")[link]. But I must explain to you how all'
                " this mistaken idea of denouncing pleasure and praising pain was born"
                " and I will give you a complete account of the system, and expound the"
                " actual teachings of the great explorer of the truth, the"
                " master-builder of human happiness. No one rejects, dislikes, or"
                " avoids pleasure itself, because it is pleasure, but because those who"
                " do not know how to pursue pleasure rationally encounter consequences"
                " that are extremely painful.]"
            ),
        ),
        (
            "!!! summary\n    This is a multi-line summary\n    with two lines",
            "#summary[This is a multi-line summary \\ with two lines]",
        )
    ],
)
def test_markdown_to_typst(markdown_string, expected_typst_string):
    assert markdown_to_typst(markdown_string) == expected_typst_string


def test_markdown_to_html():
    assert (
        markdown_to_html("Hello, **world**!") == "<p>Hello, <strong>world</strong>!</p>"
    )
