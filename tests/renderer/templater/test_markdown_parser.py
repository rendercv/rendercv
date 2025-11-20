import pytest

from rendercv.renderer.templater.markdown_parser import (
    markdown_to_html,
    markdown_to_typst,
)


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
        ("My ( Text", "My \\( Text"),
        ("My ) Text", "My \\) Text"),
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
    ],
)
def test_markdown_to_typst(markdown_string, expected_typst_string):
    assert markdown_to_typst(markdown_string) == expected_typst_string


def test_markdown_to_html():
    assert (
        markdown_to_html("Hello, **world**!") == "<p>Hello, <strong>world</strong>!</p>"
    )
