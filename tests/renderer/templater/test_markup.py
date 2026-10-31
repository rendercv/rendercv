import json
import re
import xml.etree.ElementTree as ET

import pytest
import typst
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from rendercv.exception import RenderCVInternalError
from rendercv.renderer.templater.markup import (
    Break,
    Code,
    Emph,
    Link,
    ListMarker,
    Math,
    Node,
    Placeholder,
    Raw,
    Strong,
    Summary,
    Text,
    bold_keywords,
    can_open_and_close,
    character_class,
    clean_url,
    emit,
    escape_markdown,
    escape_typst,
    find_closing_bracket,
    find_math_end,
    find_typst_expression_end,
    markdown_to_html,
    normalize,
    parse_content,
    parse_inline,
    plain_text,
    typst_string,
)


def bold(text: str) -> Strong:
    return Strong((Text(text),))


def italic(text: str) -> Emph:
    return Emph((Text(text),))


class TestFindClosingBracket:
    @pytest.mark.parametrize(
        ("source", "start", "expected"),
        [
            ("(a)", 0, 3),
            ("[a [b] c]x", 0, 9),
            ('(a, ")")', 0, 8),
            ("[a #emph[b] c]", 0, 14),
            ("[a #h(1fr) )]", 0, 13),
            ("[a \\] b]", 0, 8),
            ("(a", 0, None),
        ],
    )
    def test_finds_the_matching_bracket(self, source, start, expected):
        assert find_closing_bracket(source, start) == expected


class TestFindTypstExpressionEnd:
    @pytest.mark.parametrize(
        ("source", "expected"),
        [
            ("#h(1fr)", 7),
            ("#emph[x] y", 8),
            ("#sym.pi", 7),
            ("#datetime.today().year", 22),
            ("#text(fill: red)[a]b", 19),
            ('#link("a")[b] c', 13),
            ("#emph[x].5", 8),
        ],
    )
    def test_finds_the_end_of_an_expression(self, source, expected):
        assert find_typst_expression_end(source, 0) == expected

    @pytest.mark.parametrize("source", ["#OpenToWork", "#", "# x", "#emph[x", "#1"])
    def test_returns_none_for_text(self, source):
        assert find_typst_expression_end(source, 0) is None


@pytest.mark.parametrize(
    ("source", "expected"),
    [("$$x$$", 5), ("$$a + b$$ c", 9), ("$$x", None)],
)
def test_find_math_end(source, expected):
    assert find_math_end(source, 0) == expected


class TestParseInline:
    @given(
        source=st.recursive(
            st.sampled_from(["#sym.pi", "#emph[**not Markdown**]", '#text("a)\\"b")']),
            lambda children: children.map(lambda child: f"#emph[{child}]"),
            max_leaves=10,
        )
    )
    def test_nested_typst_expressions_survive_unchanged(self, source):
        assert parse_inline(source) == (Raw(source),)
        assert emit(parse_inline(source), "typst") == source

    @pytest.mark.parametrize(
        ("source", "expected"),
        [
            ("plain text", (Text("plain text"),)),
            ("**bold**", (bold("bold"),)),
            ("*italic*", (italic("italic"),)),
            ("_italic_", (italic("italic"),)),
            ("***both***", (Emph((bold("both"),)),)),
            ("`code`", (Code("code"),)),
            (
                "[link](https://example.com)",
                (Link("https://example.com", (Text("link"),)),),
            ),
            ("[label]()", (Link("", (Text("label"),)),)),
            ("![alt](https://example.com/a.png)", (Text("alt"),)),
            ("\\*not bold\\*", (Text("*not bold*"),)),
            ("&amp; &copy;", (Text("& ©"),)),
            ("<b>html</b>", (Text("<b>html</b>"),)),
            ("a_b_c", (Text("a_b_c"),)),
            (
                "a **b *c* d** e",
                (
                    Text("a "),
                    Strong((Text("b "), italic("c"), Text(" d"))),
                    Text(" e"),
                ),
            ),
        ],
    )
    def test_parses_markdown(self, source, expected):
        assert parse_inline(source) == expected

    @pytest.mark.parametrize(
        "source",
        [
            "#emph[x]",
            "#h(1fr)",
            "#sym.pi",
            "#datetime.today().year",
            "#text(fill: rgb(1, 2, 3))[a #emph[b] c]",
            '#link("https://example.com")[*not emphasis*]',
        ],
    )
    def test_keeps_typst_expressions_verbatim(self, source):
        assert parse_inline(source) == (Raw(source),)

    @pytest.mark.parametrize("source", ["#OpenToWork", "#emph[unclosed", "C# and F#"])
    def test_treats_incomplete_typst_as_text(self, source):
        assert parse_inline(source) == (Text(source),)

    def test_keeps_typst_math_verbatim(self):
        assert parse_inline("$$x^2 *y*$$") == (Math("x^2 *y*"),)

    def test_treats_unclosed_math_as_text(self):
        assert parse_inline("$$x") == (Text("$$x"),)

    def test_parses_typst_inside_formatting(self):
        assert parse_inline("**#emph[x]**") == (Strong((Raw("#emph[x]"),)),)


class TestParseContent:
    def test_separates_lines_with_breaks(self):
        assert parse_content("a\n*b*") == (Text("a"), Break(), italic("b"))

    def test_parses_each_line_independently(self):
        assert parse_content("**a\nb**") == (Text("**a"), Break(), Text("b**"))

    @pytest.mark.parametrize(
        ("source", "expected"),
        [
            ("- item", (ListMarker("- "), Text("item"))),
            ("  - nested", (ListMarker("  - "), Text("nested"))),
            ("1. first", (ListMarker("1. "), Text("first"))),
            ("+ enumerated", (ListMarker("+ "), Text("enumerated"))),
            ("-not a list", (Text("-not a list"),)),
        ],
    )
    def test_recognizes_list_markers(self, source, expected):
        assert parse_content(source) == expected

    def test_strips_indentation_of_lines_that_are_not_list_items(self):
        assert parse_content("a\n    b") == (Text("a"), Break(), Text("b"))


class TestNormalize:
    @pytest.mark.parametrize(
        ("nodes", "expected"),
        [
            ((Text("a"), Text("b")), (Text("ab"),)),
            ((Text(""), Code("a"), Code("b")), (Code("ab"),)),
            ((bold("a"), bold("b")), (bold("ab"),)),
            ((italic("a"), italic("b")), (italic("ab"),)),
            (
                (Link("u", (Text("a"),)), Link("u", (Text("b"),))),
                (Link("u", (Text("ab"),)),),
            ),
            (
                (Link("u", (Text("a"),)), Link("v", (Text("b"),))),
                (Link("u", (Text("a"),)), Link("v", (Text("b"),))),
            ),
            ((Strong(()), Emph((Text(""),))), ()),
            ((Strong((Text("a"), bold("b"))),), (bold("ab"),)),
            ((Strong((Emph((bold("x"),)),)),), (Emph((bold("x"),)),)),
            ((Strong((italic("x"),)),), (Emph((bold("x"),)),)),
            ((Emph((italic("x"),)),), (Emph((italic("x"),)),)),
        ],
    )
    def test_brings_content_into_canonical_form(self, nodes, expected):
        assert normalize(nodes) == expected

    def test_is_idempotent(self):
        nodes = parse_content("a **b *c***d** `e` [f](g)")

        assert normalize(normalize(nodes)) == normalize(nodes)


class TestBoldKeywords:
    @pytest.mark.parametrize(
        ("source", "keywords", "expected"),
        [
            (
                "Python and Pythonic",
                ["Python"],
                (bold("Python"), Text(" and Pythonic")),
            ),
            ("zero **one** two", ["one"], (Text("zero "), bold("one"), Text(" two"))),
            ("**zero one two**", ["one"], (bold("zero one two"),)),
            (
                "*one*",
                ["one"],
                (Emph((bold("one"),)),),
            ),
            ("`Python`", ["Python"], (Code("Python"),)),
            ("#emph[Python]", ["Python"], (Raw("#emph[Python]"),)),
            ("$$Python$$", ["Python"], (Math("Python"),)),
            (
                "[Python](https://python.org)",
                ["Python"],
                (Link("https://python.org", (bold("Python"),)),),
            ),
            ("C++17 and C++", ["C++"], (Text("C++17 and "), bold("C++"))),
            ("Python", [""], (Text("Python"),)),
            ("::", [":"], (bold("::"),)),
            ("1:1:", ["1:"], (Text("1:"), bold("1:"))),
            ("Py**thon**ic", ["Py"], (Text("Py"), bold("thon"), Text("ic"))),
            (
                "Py*thon*",
                ["Python"],
                (bold("Py"), Emph((bold("thon"),))),
            ),
            ("Py`thon`", ["Python"], (Text("Py"), Code("thon"))),
        ],
    )
    def test_bolds_whole_words_in_prose(self, source, keywords, expected):
        assert bold_keywords(parse_content(source), keywords) == expected

    def test_is_idempotent(self):
        nodes = bold_keywords(parse_content("Python and Java"), ["Python", "Java"])

        assert bold_keywords(nodes, ["Python", "Java"]) == nodes


class TestEscapeTypst:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            (
                "a*b_c`d$e#f@g<h[i]j~k\\l",
                "a\\*b\\_c\\`d\\$e\\#f\\@g\\<h\\[i\\]j\\~k\\\\l",
            ),
            ("https://example.com", "https:\\//example.com"),
            ("a/b > c", "a/b > c"),
            ('"quoted" isn\'t', '"quoted" isn\'t'),
        ],
    )
    def test_escapes_inline_syntax(self, text, expected):
        assert escape_typst(text, at_block_start=False) == expected

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("= Heading", "\\= Heading"),
            ("== Heading", "\\== Heading"),
            ("=b", "=b"),
            ("- item", "\\- item"),
            ("-", "\\-"),
            ("+ item", "\\+ item"),
            ("/ term", "\\/ term"),
            ("1. item", "1\\. item"),
            ("10.1007", "10.1007"),
            ("=\u00a0x", "\\=\u00a0x"),
        ],
    )
    def test_escapes_block_syntax_at_block_start(self, text, expected):
        assert escape_typst(text, at_block_start=True) == expected
        assert escape_typst(text, at_block_start=False) == text


class TestEscapeMarkdown:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("a*b`c<d\\e[f]g", "a\\*b\\`c\\<d\\\\e\\[f\\]g"),
            ("snake_case _start end_", "snake_case \\_start end\\_"),
            ("&amp; &", "\\&amp; &"),
            ("$$x$$ and $5", "\\$\\$x\\$\\$ and $5"),
            ("#h(1fr) #OpenToWork", "\\#h(1fr) #OpenToWork"),
        ],
    )
    def test_escapes_inline_syntax(self, text, expected):
        assert escape_markdown(text, at_block_start=False) == expected

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("# Heading", "\\# Heading"),
            ("#hashtag", "#hashtag"),
            ("> quote", "\\> quote"),
            ("- item", "\\- item"),
            ("+ item", "\\+ item"),
            ("1. item", "1\\. item"),
            ("1) item", "1\\) item"),
            ("---", "\\---"),
            ("===", "\\==="),
            ("~~~", "\\~~~"),
            ("10.1007", "10.1007"),
        ],
    )
    def test_escapes_block_syntax_at_block_start(self, text, expected):
        assert escape_markdown(text, at_block_start=True) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [("a", '"a"'), ('a "b" \\c', '"a \\"b\\" \\\\c"'), (None, "none")],
)
def test_typst_string(string, expected):
    assert typst_string(string) == expected


@pytest.mark.parametrize(
    ("character", "expected"),
    [
        (" ", "space"),
        ("\u00a0", "space"),
        ("*", "punctuation"),
        ("€", "punctuation"),
        ("a", "other"),
        ("1", "other"),
        ("é", "other"),
    ],
)
def test_character_class(character, expected):
    assert character_class(character) == expected


@pytest.mark.parametrize(
    ("delimiter", "before", "after", "expected"),
    [
        ("*", " ", "a", (True, False)),
        ("*", "a", " ", (False, True)),
        ("*", "a", "b", (True, True)),
        ("*", "a", '"', (False, True)),
        ("*", '"', "a", (True, False)),
        ("_", "a", "b", (False, False)),
        ("_", ";", "b", (True, False)),
    ],
)
def test_can_open_and_close(delimiter, before, after, expected):
    assert can_open_and_close(delimiter, before, after) == expected


class TestEmit:
    @pytest.mark.parametrize(
        ("source", "expected_typst", "expected_markdown"),
        [
            ("plain text", "plain text", "plain text"),
            ("**bold** *italic*", "#strong[bold] #emph[italic]", "**bold** *italic*"),
            ("***both***", "#emph[#strong[both]]", "*__both__*"),
            ("`code`", "`code`", "`code`"),
            ("``a`b``", '#raw("a`b")', "``a`b``"),
            (
                "[link](https://example.com)",
                '#link("https://example.com")[link]',
                "[link](https://example.com)",
            ),
            ("[label]()", "label", "label"),
            ("#emph[x]", "#emph[x]", "#emph\\[x\\]"),
            ("$$x^2$$", '#[#set math.equation(alt: "x^2");$x^2$]', "$$x^2$$"),
            ("#OpenToWork", "\\#OpenToWork", "#OpenToWork"),
            (
                "john_doe@example.com",
                "john\\_doe\\@example.com",
                "john_doe@example.com",
            ),
            ("- item", "- item", "- item"),
            ("- - item", "- \\- item", "- \\- item"),
            ("[1] ref", "\\[1\\] ref", "\\[1\\] ref"),
            ('say "hi"', 'say "hi"', 'say "hi"'),
        ],
    )
    def test_emits_content(self, source, expected_typst, expected_markdown):
        nodes = parse_content(source)

        assert emit(nodes, "typst") == expected_typst
        assert emit(nodes, "markdown") == expected_markdown

    @pytest.mark.parametrize(
        ("source", "expected"),
        [
            ("**Node**.js", "#strong[Node];.js"),
            ("**Python**(3.11)", "#strong[Python];(3.11)"),
            ("**a**;b", "#strong[a];;b"),
            ("**a**[b]", "#strong[a]\\[b\\]"),
            ("**Python**. Next", "#strong[Python]. Next"),
            ("#h(1fr).5", "#h(1fr).5"),
        ],
    )
    def test_ends_typst_expressions_that_would_continue(self, source, expected):
        assert emit(parse_content(source), "typst") == expected

    @pytest.mark.parametrize(
        ("nodes", "expected"),
        [
            ((bold("C++"), Text("17")), "**C++**&#49;7"),
            ((Text("a"), bold('"b"'), Text("c")), '&#97;**"b"**&#99;'),
            ((Strong((Text(" a"),)),), "**&#32;a**"),
            (
                (Text("!"), Link("https://example.com", (Text("x"),))),
                "\\![x](https://example.com)",
            ),
            ((Emph((italic("x"),)),), "*_x_*"),
            ((bold("a"), italic("b")), "**a***b*"),
            # What follows text in its line would make it Typst code:
            (
                (Text("#a"), Link("https://example.com", (Text("x"),))),
                "\\#a[x](https://example.com)",
            ),
            ((bold("#a("), Text(")")), "**\\#a(**)"),
            # An underscore next to a character reference would be a delimiter:
            ((Emph((bold("1"), italic("1_1"))),), "*__&#49;___&#49;\\_1_*"),
            ((Strong((Text("_ "),)),), "**\\_&#32;**"),
        ],
    )
    def test_repairs_markdown_boundaries(self, nodes, expected):
        assert emit(nodes, "markdown") == expected
        assert parse_content(emit(nodes, "markdown")) == normalize(nodes)

    def test_closes_and_reopens_formatting_around_line_breaks(self):
        nodes = (Strong((Text("a"), Break(), Text("b"))),)

        assert emit(nodes, "typst") == "#strong[a]\n#strong[b]"
        assert emit(nodes, "markdown") == "**a**\n**b**"

    def test_keeps_list_markers_at_line_starts_inside_formatting(self):
        nodes = (
            Strong((ListMarker("- "), Text("a"), Break(), ListMarker("- "), Text("b"))),
        )

        assert emit(nodes, "typst") == "- #strong[a]\n- #strong[b]"

    def test_emits_summaries(self):
        nodes = (Summary(parse_content("a\nb")),)

        assert emit(nodes, "typst") == "#summary[a \\ b]"
        assert emit(nodes, "markdown") == "a\nb"

    def test_keeps_the_list_markers_of_a_summary_as_text(self):
        # A Typst summary is one block, whose lines can't be list items:
        nodes = (Summary(parse_content("- a\n- b")),)

        assert emit(nodes, "typst") == "#summary[\\- a \\ \\- b]"
        assert emit(nodes, "markdown") == "- a\n- b"

    def test_writes_a_list_marker_after_text_as_text(self):
        nodes = (Text("x "), Strong((ListMarker("- "), Text("a"))))

        assert emit(nodes, "typst") == "x #strong[\\- a]"
        assert emit(nodes, "markdown") == "x **\\- a**"

    def test_raises_for_unfilled_placeholders(self):
        with pytest.raises(RenderCVInternalError):
            emit((Placeholder("NAME"),), "typst")


def to_nodes(value: object) -> tuple[Node, ...]:
    """Convert the tree that Typst reports (see `typst_tree_prelude`) to nodes."""
    if isinstance(value, str):
        return (Text(value),)
    if isinstance(value, list):
        return tuple(node for item in value for node in to_nodes(item))
    assert isinstance(value, dict)
    if "strong" in value:
        return (Strong(to_nodes(value["strong"])),)
    if "emph" in value:
        return (Emph(to_nodes(value["emph"])),)
    if "link" in value:
        return (Link(value["link"], to_nodes(value["body"])),)
    if "code" in value:
        return (Code(value["code"]),)
    return (Text(f"<{value['other']}>"),)


typst_tree_prelude = """
#let tree(it) = {
  if type(it) == str { it }
  else if it.func() == strong { (strong: tree(it.body)) }
  else if it.func() == emph { (emph: tree(it.body)) }
  else if it.func() == link { (link: it.dest, body: tree(it.body)) }
  else if it.func() == raw { (code: it.text) }
  else if it.has("text") { it.text }
  else if it.func() == [ ].func() { " " }
  else if it.has("children") { it.children.map(tree) }
  else { (other: repr(it.func())) }
}
"""

# Characters with no typographic shorthand (`--`, `...`, smart quotes):
adversarial_text = st.text(
    alphabet=st.sampled_from([*"ab1é *_`[]()<>#\\&!+=:;$@/|{}%^?,~", "\u00a0"]),
    min_size=1,
    max_size=6,
).map(Text)
adversarial_code = st.text(
    alphabet=st.sampled_from(list("ab *_\\`$#")), min_size=1, max_size=5
).map(Code)
urls = st.sampled_from(["https://example.com", "https://a.b/c?d=(e)", "mailto:x@y.z"])


def formatting(children: st.SearchStrategy[Node]) -> st.SearchStrategy[Node]:
    groups = st.lists(children, min_size=1, max_size=3).map(tuple)
    return st.one_of(groups.map(Strong), groups.map(Emph))


leaves = st.one_of(adversarial_text, adversarial_code)
# Up to two nested levels of bold and italic, optionally inside a link:
formatted = st.one_of(leaves, formatting(st.one_of(leaves, formatting(leaves))))
inline = st.one_of(
    formatted,
    st.tuples(urls, st.lists(formatted, min_size=1, max_size=3)).map(
        lambda link: Link(link[0], tuple(link[1]))
    ),
)
lines = st.lists(inline, min_size=1, max_size=4).map(normalize)


def is_trimmed(line: tuple[Node, ...]) -> bool:
    """Whether a line has no leading or trailing whitespace, like parsed lines."""
    first, last = line[0], line[-1]
    return not (
        (isinstance(first, Text) and first.text[0].isspace())
        or (isinstance(last, Text) and last.text[-1].isspace())
    )


def collapse_spaces(nodes: tuple[Node, ...]) -> tuple[Node, ...]:
    """Collapse runs of spaces, as Typst markup does."""
    collapsed: list[Node] = []
    for node in nodes:
        match node:
            case Text(text):
                collapsed.append(Text(re.sub(r"[ \t]+", " ", text)))
            case Strong(children) | Emph(children):
                collapsed.append(type(node)(collapse_spaces(children)))
            case Link(url, children):
                collapsed.append(Link(url, collapse_spaces(children)))
            case _:
                collapsed.append(node)
    return normalize(collapsed)


class TestEmitRoundTrip:
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    @given(line=lines)
    def test_markdown_parses_back_to_the_same_content(self, line):
        assume(line and is_trimmed(line))

        assert parse_content(emit(line, "markdown")) == line

    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    @given(line=lines)
    def test_typst_renders_the_same_content(self, line):
        source = emit(line, "typst")
        # Typst's typography turns these into other characters:
        assume(line and not re.search(r"--|\.\.\.|-\?|-\d", plain_text(line)))
        document = typst_tree_prelude + f"#metadata(tree([{source}])) <out>\n"

        value = typst.query(document.encode(), "<out>", field="value", one=True)

        rendered = to_nodes(json.loads(value) if isinstance(value, str) else value)
        assert collapse_spaces(normalize(rendered)) == collapse_spaces(line)

    @given(line=lines)
    def test_markdown_html_preserves_text_and_formatting(self, line):
        assume(line and is_trimmed(line))
        rendered = ET.fromstring(markdown_to_html(emit(line, "markdown")).strip())
        assert rendered.tag == "p"
        assert html_characters(rendered) == content_characters(line)

    @given(line=lines, keywords=st.lists(st.text(max_size=8), max_size=5))
    def test_keyword_bolding_preserves_content_and_is_idempotent(self, line, keywords):
        result = bold_keywords(line, keywords)
        assert plain_text(result) == plain_text(line)
        assert bold_keywords(result, keywords) == result
        assert content_characters(result, ignore_bold=True) == content_characters(
            line, ignore_bold=True
        )


type Character = tuple[str, bool, int, str | None, bool]


def content_characters(
    nodes: tuple[Node, ...],
    strong: bool = False,
    emphasis: int = 0,
    url: str | None = None,
    code: bool = False,
    *,
    ignore_bold: bool = False,
) -> list[Character]:
    """Read character semantics directly from the generated tree, without a parser."""
    result: list[Character] = []
    for node in nodes:
        match node:
            case Text(text) | Code(text):
                result.extend(
                    (char, strong, emphasis, url, isinstance(node, Code))
                    for char in text
                )
            case Strong(children):
                result.extend(
                    content_characters(
                        children,
                        not ignore_bold,
                        emphasis,
                        url,
                        code,
                        ignore_bold=ignore_bold,
                    )
                )
            case Emph(children):
                result.extend(
                    content_characters(
                        children,
                        strong,
                        emphasis + 1,
                        url,
                        code,
                        ignore_bold=ignore_bold,
                    )
                )
            case Link(destination, children):
                result.extend(
                    content_characters(
                        children,
                        strong,
                        emphasis,
                        destination,
                        code,
                        ignore_bold=ignore_bold,
                    )
                )
            case _:
                message = f"Unexpected node in inline strategy: {node}"
                raise AssertionError(message)
    return result


def html_characters(
    element: ET.Element,
    strong: bool = False,
    emphasis: int = 0,
    url: str | None = None,
    code: bool = False,
) -> list[Character]:
    """Read browser-facing semantics independently of RenderCV's Markdown parser."""
    assert element.tag in {"p", "strong", "em", "a", "code"}
    strong = strong or element.tag == "strong"
    emphasis += element.tag == "em"
    url = element.attrib.get("href", url)
    code = code or element.tag == "code"
    result = [(char, strong, emphasis, url, code) for char in element.text or ""]
    for child in element:
        result.extend(html_characters(child, strong, emphasis, url, code))
        result.extend((char, strong, emphasis, url, code) for char in child.tail or "")
    return result


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("**John** Doe's [CV](https://example.com)", "John Doe's CV"),
        ("a `b` #emph[c] $$d$$", "a b #emph[c] $$d$$"),
        ("- a\nb", "- a\nb"),
    ],
)
def test_plain_text(source, expected):
    assert plain_text(parse_content(source)) == expected


def test_plain_text_raises_for_unfilled_placeholders():
    with pytest.raises(RenderCVInternalError):
        plain_text((Placeholder("NAME"),))


@pytest.mark.parametrize(
    ("markdown", "expected"),
    [
        ("# Title", "<h1>Title</h1>\n"),
        ("**bold**", "<p><strong>bold</strong></p>\n"),
        ("- a\n- b", "<ul>\n<li>a</li>\n<li>b</li>\n</ul>\n"),
    ],
)
def test_markdown_to_html(markdown, expected):
    assert markdown_to_html(markdown) == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://example.com", "example.com"),
        ("https://example.com/", "example.com"),
        ("http://example.com/test/", "example.com/test"),
        ("example.com", "example.com"),
    ],
)
def test_clean_url(url, expected):
    assert clean_url(url) == expected
