"""User content as a tree: parsed once, transformed as a tree, emitted once.

User content is inline Markdown (`**bold**`, `*italic*`, `` `code` ``,
`[text](url)`) with two Typst extensions: Typst expressions (`#emph[x]`,
`#h(1fr)`, `#sym.pi`) and Typst math (`$$x^2$$`). Each line is independent, and a
line may start with a list marker (`- `, `+ `, `1. `), possibly indented.

Content is parsed into a tree of immutable nodes. Every transformation (keyword
bolding, template substitution) is a tree operation, and escaping happens exactly
once, when a tree is emitted as Typst or Markdown. No intermediate string is ever
parsed again.
"""

import dataclasses
import functools
import re
from collections.abc import Sequence
from typing import Literal

import markdown_it
import markdown_it.common.utils
import markdown_it.rules_inline

from rendercv.exception import RenderCVInternalError
from rendercv.text import keyword_pattern


@dataclasses.dataclass(frozen=True)
class Text:
    """Literal text."""

    text: str


@dataclasses.dataclass(frozen=True)
class Strong:
    """Bold content."""

    children: tuple["Node", ...]


@dataclasses.dataclass(frozen=True)
class Emph:
    """Italic content."""

    children: tuple["Node", ...]


@dataclasses.dataclass(frozen=True)
class Code:
    """Inline code: literal, monospaced text."""

    text: str


@dataclasses.dataclass(frozen=True)
class Link:
    """A hyperlink. An empty URL means the label is shown without a link."""

    url: str
    children: tuple["Node", ...]


@dataclasses.dataclass(frozen=True)
class Raw:
    """Typst code written by the user, passed through to Typst verbatim."""

    source: str


@dataclasses.dataclass(frozen=True)
class Math:
    """Typst math written by the user between `$$` delimiters."""

    source: str


@dataclasses.dataclass(frozen=True)
class ListMarker:
    """A list marker at the start of a line, with its indentation (e.g. `"  - "`)."""

    source: str


@dataclasses.dataclass(frozen=True)
class Break:
    """The end of a line."""


@dataclasses.dataclass(frozen=True)
class Summary:
    """A summary block: content rendered with the theme's summary style."""

    children: tuple["Node", ...]


@dataclasses.dataclass(frozen=True)
class Placeholder:
    """A placeholder in a template, replaced by content when the template is filled."""

    name: str


type Node = (
    Text
    | Strong
    | Emph
    | Code
    | Link
    | Raw
    | Math
    | ListMarker
    | Break
    | Summary
    | Placeholder
)
type Format = Literal["typst", "markdown"]


# ======================================================================================
# Parsing
# ======================================================================================

list_marker_pattern = re.compile(r"[ \t]*(?:[-+]|\d+\.)[ \t]+")
typst_name_pattern = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
closing_bracket_of = {"(": ")", "[": "]", "{": "}"}


def find_closing_bracket(source: str, start: int) -> int | None:
    """Find the index just after the bracket that closes the one at `start`.

    Why:
        A Typst expression's arguments and content can contain brackets, strings,
        and other expressions (`#text(fill: rgb(1, 2, 3))[a #emph[b] c]`), so the
        end of an expression is found by matching brackets, not by a regex.

    Args:
        source: The string containing the expression.
        start: Index of an opening `(`, `[`, or `{`.

    Returns:
        Index after the matching closing bracket, or None if it is unbalanced.
    """
    stack = [closing_bracket_of[source[start]]]
    index = start + 1
    while index < len(source):
        character = source[index]
        in_content = stack[-1] == "]"
        if character == "\\":
            index += 2
            continue
        if in_content and character == "#":
            # A nested expression inside content is skipped as a whole, so that its
            # strings and brackets don't affect the nesting of the outer one:
            nested_end = find_typst_expression_end(source, index)
            if nested_end is not None:
                index = nested_end
                continue
        elif character == '"' and not in_content:
            # Skip a string literal, honoring escapes:
            index += 1
            while index < len(source) and source[index] != '"':
                index += 2 if source[index] == "\\" else 1
        elif character in closing_bracket_of and (character == "[" or not in_content):
            stack.append(closing_bracket_of[character])
        elif character == stack[-1]:
            stack.pop()
            if not stack:
                return index + 1
        index += 1
    return None


def find_typst_expression_end(source: str, start: int) -> int | None:
    """Find the end of a Typst expression that starts with `#` at `start`.

    Why:
        RenderCV passes Typst expressions through verbatim. An expression is a
        name followed by at least one argument list, content block, or field
        access: `#h(1fr)`, `#emph[x]`, `#sym.pi`, `#datetime.today().year`. A bare
        `#word` is not an expression; it is text, so `#OpenToWork` is a hashtag.

    Args:
        source: The string containing the expression.
        start: Index of `#`.

    Returns:
        Index after the expression, or None if there is no expression at `start`.
    """
    name = typst_name_pattern.match(source, start + 1)
    if name is None:
        return None
    end = name.end()
    has_continuation = False
    while end < len(source):
        if source[end] in "([":
            closing = find_closing_bracket(source, end)
            if closing is None:
                return None
            end = closing
        elif source[end] == "." and (
            field := typst_name_pattern.match(source, end + 1)
        ):
            end = field.end()
        else:
            break
        has_continuation = True
    return end if has_continuation else None


def find_math_end(source: str, start: int) -> int | None:
    """Find the end of `$$...$$` math that starts at `start`.

    Args:
        source: The string containing the math.
        start: Index of the opening `$$`.

    Returns:
        Index after the closing `$$`, or None if it is not closed.
    """
    closing = source.find("$$", start + 2)
    return None if closing == -1 else closing + 2


def typst_rule(state: markdown_it.rules_inline.StateInline, silent: bool) -> bool:
    """markdown-it inline rule that captures Typst expressions and math atomically.

    Why:
        Typst code must reach Typst untouched: Markdown must not interpret its
        `*`, `_`, or brackets, and escaping must not touch it. Recognizing it while
        parsing (instead of patching the output) makes it an opaque leaf.

    Args:
        state: markdown-it inline parser state.
        silent: Whether to only validate the match without emitting a token.

    Returns:
        Whether a Typst expression or math starts at the current position.
    """
    source = state.src
    start = state.pos
    if source.startswith("$$", start):
        end, kind = find_math_end(source, start), "typst_math"
    elif source[start] == "#":
        end, kind = find_typst_expression_end(source, start), "typst_raw"
    else:
        return False
    if end is None:
        return False
    if not silent:
        token = state.push(kind, "", 0)
        token.content = source[start:end]
    state.pos = end
    return True


@functools.cache
def get_markdown_parser() -> markdown_it.MarkdownIt:
    """Build the Markdown parser with RenderCV's Typst extensions.

    Returns:
        The parser.
    """
    parser = markdown_it.MarkdownIt("commonmark", {"html": False})
    parser.inline.ruler.after("escape", "typst", typst_rule)
    return parser


def parse_inline(source: str) -> tuple[Node, ...]:
    """Parse one line of inline content into nodes.

    Args:
        source: A single line of content (without its list marker).

    Returns:
        The nodes of the line.
    """
    tokens = get_markdown_parser().parseInline(source)[0].children or []
    stack: list[list[Node]] = [[]]
    hrefs: list[str] = []
    for token in tokens:
        match token.type:
            case "text" | "text_special" | "html_inline" | "softbreak" | "hardbreak":
                text = token.content if "break" not in token.type else " "
                stack[-1].append(Text(text))
            case "code_inline":
                stack[-1].append(Code(token.content))
            case "typst_raw":
                stack[-1].append(Raw(token.content))
            case "typst_math":
                stack[-1].append(Math(token.content.removeprefix("$$")[:-2]))
            case "strong_open" | "em_open" | "link_open":
                if token.type == "link_open":
                    hrefs.append(str(token.attrs.get("href", "")))
                stack.append([])
            case "strong_close" | "em_close" | "link_close":
                children = tuple(stack.pop())
                if token.type == "strong_close":
                    container = Strong(children)
                elif token.type == "em_close":
                    container = Emph(children)
                else:
                    container = Link(hrefs.pop(), children)
                stack[-1].append(container)
            case _:
                # Images and other constructs RenderCV doesn't support are kept as
                # their source text:
                stack[-1].append(Text(token.content or token.markup))
    return normalize(stack[0])


def parse_content(source: str) -> tuple[Node, ...]:
    """Parse multi-line content into nodes; lines are separated by `Break` nodes.

    Why:
        Each line of content is an independent unit (emphasis never spans lines),
        and a line may start with a list marker, which is structure, not text.

    Args:
        source: User content.

    Returns:
        The nodes of the content.
    """
    nodes: list[Node] = []
    for index, line in enumerate(source.split("\n")):
        if index:
            nodes.append(Break())
        marker = list_marker_pattern.match(line)
        if marker:
            nodes.append(ListMarker(marker.group()))
        # Indentation is meaningful only for list items:
        nodes.extend(parse_inline(line[marker.end() :] if marker else line.lstrip()))
    return tuple(nodes)


def normalize(nodes: Sequence[Node], *, in_strong: bool = False) -> tuple[Node, ...]:
    """Bring content into its canonical form, in which equivalent content is equal.

    Why:
        The same content has many trees: `**a****b**` is `**ab**`, and bold italic
        is italic bold. The canonical form drops empty text and formatting, merges
        adjacent text, code, and identical formatting, removes bold inside bold
        (bold is bold), and writes bold italic as italic bold, like Markdown
        parses `***x***`. Emission requires it: it is what makes emitted Markdown
        parse back to the same tree.

    Args:
        nodes: Content.
        in_strong: Whether the content is inside bold content.

    Returns:
        The content in canonical form.
    """
    result: list[Node] = []
    for node in nodes:
        for normalized in normalize_node(node, in_strong=in_strong):
            match result[-1] if result else None, normalized:
                case Text(before), Text(after):
                    result[-1] = Text(before + after)
                case Code(before), Code(after):
                    result[-1] = Code(before + after)
                case (Strong(before), Strong(after)) | (Emph(before), Emph(after)):
                    merged = dataclasses.replace(normalized, children=(*before, *after))
                    result[-1:] = normalize_node(merged, in_strong=in_strong)
                case Link(url, before), Link(other_url, after) if url == other_url:
                    result[-1] = Link(
                        url, normalize((*before, *after), in_strong=in_strong)
                    )
                case _:
                    result.append(normalized)
    return tuple(result)


def normalize_node(node: Node, *, in_strong: bool) -> tuple[Node, ...]:
    """Bring a node into its canonical form (see `normalize`).

    Args:
        node: A node.
        in_strong: Whether the node is inside bold content.

    Returns:
        The nodes that the node is in canonical form: none if it is empty, its
        children if it is bold inside bold, or else one node.
    """
    match node:
        case Text(""):
            return ()
        case Strong(children) if in_strong:
            return normalize(children, in_strong=True)
        case (
            Strong(children)
            | Emph(children)
            | Link(children=children)
            | Summary(children)
        ):
            normalized = normalize(
                children, in_strong=in_strong or isinstance(node, Strong)
            )
            if not normalized:
                return ()
            match node, normalized:
                case Strong(), (Emph(emphasized),):
                    # Bold italic is italic bold:
                    return (Emph(normalize((Strong(emphasized),))),)
            return (dataclasses.replace(node, children=normalized),)
    return (node,)


# ======================================================================================
# Transformations
# ======================================================================================


def bold_keywords(nodes: tuple[Node, ...], keywords: Sequence[str]) -> tuple[Node, ...]:
    """Make whole-word keyword occurrences bold.

    Why:
        Keywords are matched against visible text, so formatting boundaries don't
        create word boundaries. A match may cross formatting or a link label, but
        never code, Typst code, math, or a line break. Applying the resulting ranges
        to text leaves preserves formatting and makes repeated bolding idempotent.

    Args:
        nodes: Content.
        keywords: Keywords to bold, matched case-sensitively as whole words.

    Returns:
        Content with keywords bolded.
    """
    keywords = [keyword for keyword in keywords if keyword]
    if not keywords:
        return nodes
    pattern = keyword_pattern(frozenset(keywords))
    prose_ranges: list[tuple[int, int]] = []
    cursor = 0

    def collect(items: Sequence[Node]) -> None:
        nonlocal cursor
        for node in items:
            if isinstance(node, Strong | Emph | Link | Summary):
                collect(node.children)
                continue
            end = cursor + len(plain_text((node,)))
            if isinstance(node, Text):
                if prose_ranges and prose_ranges[-1][1] == cursor:
                    prose_ranges[-1] = (prose_ranges[-1][0], end)
                else:
                    prose_ranges.append((cursor, end))
            cursor = end

    collect(nodes)
    matches = [
        (match.start(), match.end())
        for match in pattern.finditer(plain_text(nodes))
        if any(
            start <= match.start() and match.end() <= end for start, end in prose_ranges
        )
    ]
    cursor = 0

    def apply(items: Sequence[Node], *, in_strong: bool = False) -> tuple[Node, ...]:
        nonlocal cursor
        result: list[Node] = []
        for node in items:
            if isinstance(node, Strong | Emph | Link | Summary):
                result.append(
                    dataclasses.replace(
                        node,
                        children=apply(
                            node.children,
                            in_strong=in_strong or isinstance(node, Strong),
                        ),
                    )
                )
                continue
            end = cursor + len(plain_text((node,)))
            if isinstance(node, Text) and not in_strong:
                written = 0
                for start, stop in matches:
                    left, right = max(cursor, start), min(end, stop)
                    if left >= right:
                        continue
                    result.append(Text(node.text[written : left - cursor]))
                    result.append(
                        Strong((Text(node.text[left - cursor : right - cursor]),))
                    )
                    written = right - cursor
                result.append(Text(node.text[written:]))
            else:
                result.append(node)
            cursor = end
        return normalize(result)

    return apply(nodes)


# ======================================================================================
# Emission
# ======================================================================================

typst_escapes = str.maketrans(
    {character: "\\" + character for character in "\\*_`$#@<[]~"}
)
# `//` starts a comment (`/*` can't occur, since `*` is always escaped):
typst_comment_pattern = re.compile(r"/(?=/)")
markdown_escapes = str.maketrans(
    {character: "\\" + character for character in "\\*`<[]"}
)
# The block syntax that can start a line. Each pattern's group is the character whose
# escaping turns the line into text:
# Typst's whitespace is Unicode's (with no-break spaces), Markdown's is ASCII's:
typst_block_syntax_patterns = (
    re.compile(r"\s*(=)=*(?:\s|$)"),  # Heading
    re.compile(r"\s*([-+/])(?:\s|$)"),  # List, enumeration, or term item
    re.compile(r"\s*\d+(\.)(?:\s|$)"),  # Numbered enumeration item
)
markdown_block_syntax_patterns = (
    re.compile(r"[ \t]*(#)#{0,5}(?:[ \t]|$)"),  # Heading
    re.compile(r"[ \t]*(>)"),  # Block quote
    re.compile(r"[ \t]*([-+])(?:[ \t]|$)"),  # List item
    re.compile(r"[ \t]*\d{1,9}([.)])(?:[ \t]|$)"),  # Ordered list item
    re.compile(r"[ \t]*([-=])[-= \t]*$"),  # Thematic break or heading underline
    re.compile(r"[ \t]*(~)~~"),  # Code fence
)
markdown_underscore_pattern = re.compile(r"(?<![^\W_])_|_(?![^\W_])")
# Underscores at an edge of text that are literal only because a letter or a digit
# is on each side of them:
leading_underscores_pattern = re.compile(r"^_+(?=[^\W_])")
trailing_underscores_pattern = re.compile(r"(?<=[^\W_])_+$")
markdown_entity_pattern = re.compile(r"&(?=#?\w+;)")
markdown_math_pattern = re.compile(r"\$(?=\$)|(?<=\$)\$")
# What continues a Typst expression (arguments, content, a field) or ends it (`;`):
typst_continuation_pattern = re.compile(r"[(\[;]|\.[^\W\d]")


def escape_block_syntax(escaped: str, patterns: Sequence[re.Pattern[str]]) -> str:
    """Escape the block syntax (heading, list marker) that starts a line.

    Args:
        escaped: Text whose inline syntax is already escaped.
        patterns: Patterns of block syntax, each capturing the character to escape.

    Returns:
        The text with its leading block syntax escaped.
    """
    for pattern in patterns:
        if match := pattern.match(escaped):
            position = match.start(1)
            return escaped[:position] + "\\" + escaped[position:]
    return escaped


def escape_typst(text: str, *, at_block_start: bool) -> str:
    """Escape text so that Typst renders it literally.

    Args:
        text: Literal text.
        at_block_start: Whether the text starts a line or a content block, where
            `=` starts a heading and `-`, `+`, or `1.` a list.

    Returns:
        Typst markup that renders as the text.
    """
    escaped = typst_comment_pattern.sub(r"\\/", text.translate(typst_escapes))
    if at_block_start:
        escaped = escape_block_syntax(escaped, typst_block_syntax_patterns)
    return escaped


def escape_markdown(text: str, *, at_block_start: bool) -> str:
    """Escape text so that Markdown renders it literally.

    Args:
        text: Literal text.
        at_block_start: Whether the text starts a line, where `# `, `>`, and list
            markers are block syntax.

    Returns:
        Markdown that renders as the text.
    """
    escaped = text.translate(markdown_escapes)
    # Underscores between word characters never delimit emphasis:
    escaped = markdown_underscore_pattern.sub(r"\\_", escaped)
    escaped = markdown_entity_pattern.sub(r"\\&", escaped)
    # RenderCV's extensions: `$$` starts Typst math and `#` may start Typst code:
    escaped = markdown_math_pattern.sub(r"\\$", escaped)
    escaped = "".join(
        (
            "\\" + character
            if character == "#"
            and find_typst_expression_end(escaped, index) is not None
            else character
        )
        for index, character in enumerate(escaped)
    )
    if at_block_start:
        escaped = escape_block_syntax(escaped, markdown_block_syntax_patterns)
    return escaped


def typst_string(string: str | None) -> str:
    """Write an optional string as a Typst value.

    Args:
        string: Any string, or None.

    Returns:
        A Typst string literal (with quotes) whose value is the string, or `none`.
    """
    if string is None:
        return "none"
    return '"' + string.replace("\\", "\\\\").replace('"', '\\"') + '"'


type PieceKind = Literal["text", "markup", "end", "open", "close", "link"]


@dataclasses.dataclass(frozen=True)
class Piece:
    """A piece of an emitted line.

    Why:
        Whether markup works depends on its neighbors: a Typst expression continues
        into a following `(`, and a Markdown emphasis delimiter next to punctuation
        may neither open nor close. Lines are built from pieces, and `join_pieces`
        repairs the boundaries between them.

    Args:
        source: The emitted source.
        kind: `"text"` for escaped text, `"end"` for the end of a Typst
            expression, `"open"` and `"close"` for Markdown emphasis delimiters,
            `"link"` for the start of a Markdown link, and `"markup"` for other
            syntax.
    """

    source: str
    kind: PieceKind


@dataclasses.dataclass
class Line:
    """An emitted line: its list marker (if any) and its pieces."""

    marker: str = ""
    pieces: list[Piece] = dataclasses.field(default_factory=list)


def emit_lines(
    nodes: Sequence[Node],
    output_format: Format,
    *,
    in_container: bool = False,
    enclosing_delimiter: str = "",
) -> list[Line]:
    """Emit content as lines of Typst or Markdown pieces.

    Why:
        Templates are laid out line by line, so formatting that encloses a line
        break (a multi-line value inside `**...**`) is closed at the end of each
        line and reopened on the next one, and list markers stay at line starts.

    Args:
        nodes: Content in canonical form (see `normalize`).
        output_format: `"typst"` or `"markdown"`.
        in_container: Whether the nodes are the children of a container. A Typst
            content block starts a new block, a Markdown container doesn't.
        enclosing_delimiter: The Markdown delimiter character of the closest
            enclosing bold or italic container, if any.

    Returns:
        The emitted lines.
    """
    escape = escape_typst if output_format == "typst" else escape_markdown
    lines = [Line()]
    for node in nodes:
        current = lines[-1]
        # A list item's body starts a block too (`- - x` is a nested list):
        at_block_start = not current.pieces and (
            output_format == "typst" or not in_container
        )
        match node:
            case Break():
                lines.append(Line())
            case ListMarker(source) if not current.marker and not current.pieces:
                current.marker = source
            case ListMarker(source) | Text(source):
                text = escape(source, at_block_start=at_block_start)
                current.pieces.append(Piece(text, "text"))
            case Code(text):
                current.pieces.append(emit_code(text, output_format))
            case Raw(source) if output_format == "typst":
                current.pieces.append(Piece(source, "end"))
            case Raw(source):
                text = escape_markdown(source, at_block_start=at_block_start)
                current.pieces.append(Piece(text, "text"))
            case Math(source) if output_format == "typst":
                # Its source describes a formula to readers who can't see it:
                alt = typst_string(source.strip())
                math = f"#[#set math.equation(alt: {alt});${source}$]"
                current.pieces.append(Piece(math, "end"))
            case Math(source):
                math = escape_markdown(source, at_block_start=False)
                current.pieces.append(Piece(f"$${math}$$", "markup"))
            case Summary(children) if output_format == "typst":
                current.pieces.append(Piece("#summary[", "markup"))
                for index, line in enumerate(emit_lines(children, output_format)):
                    if index:
                        current.pieces.append(Piece(" \\ ", "markup"))
                    if line.marker:
                        marker = escape_typst(line.marker, at_block_start=True)
                        current.pieces.append(Piece(marker, "text"))
                    current.pieces.extend(line.pieces)
                current.pieces.append(Piece("]", "end"))
            case Summary(children):
                lines[-1:] = emit_lines(children, output_format)
            case Placeholder(name):
                message = f"The placeholder {name} was not filled."
                raise RenderCVInternalError(message)
            case Strong(children) | Emph(children) | Link(children=children):
                start, end = container_delimiters(
                    node, output_format, enclosing_delimiter=enclosing_delimiter
                )
                inner = emit_lines(
                    children,
                    output_format,
                    in_container=True,
                    enclosing_delimiter=(
                        start.source[0]
                        if isinstance(node, Strong | Emph) and start.source
                        else enclosing_delimiter
                    ),
                )
                for index, line in enumerate(inner):
                    pieces = line.pieces
                    if index:
                        lines.append(Line(line.marker))
                    elif line.marker and not current.marker and not current.pieces:
                        current.marker = line.marker
                    elif line.marker:
                        # A list marker after text on the line is text:
                        marker = escape(line.marker, at_block_start=True)
                        pieces = [Piece(marker, "text"), *pieces]
                    if pieces:
                        lines[-1].pieces.extend([start, *pieces, end])
    return lines


def container_delimiters(
    node: Strong | Emph | Link, output_format: Format, *, enclosing_delimiter: str
) -> tuple[Piece, Piece]:
    """Return the markup that opens and closes a container.

    Why:
        A Markdown delimiter run can be understood as either opening or closing
        when punctuation surrounds it, and it then closes an unclosed one with the
        same character. Nested bold and italic therefore alternate between `*` and
        `_`, which also keeps a container's delimiters from merging with its
        parent's (`*__x__*`, not `***x***`).

    Args:
        node: The container.
        output_format: `"typst"` or `"markdown"`.
        enclosing_delimiter: The Markdown delimiter character of the closest
            enclosing bold or italic container, if any.

    Returns:
        Opening and closing markup.
    """
    character = "_" if enclosing_delimiter == "*" else "*"
    match node:
        case Strong() if output_format == "typst":
            return Piece("#strong[", "markup"), Piece("]", "end")
        case Strong():
            return Piece(character * 2, "open"), Piece(character * 2, "close")
        case Emph() if output_format == "typst":
            return Piece("#emph[", "markup"), Piece("]", "end")
        case Emph():
            return Piece(character, "open"), Piece(character, "close")
        case Link(url) if not url:
            return Piece("", "markup"), Piece("", "markup")
        case Link(url) if output_format == "typst":
            return Piece(f"#link({typst_string(url)})[", "markup"), Piece("]", "end")
        case Link(url):
            destination = url.replace("<", "%3C").replace(">", "%3E")
            if re.search(r"[\s()]", destination):
                destination = f"<{destination}>"
            return Piece("[", "link"), Piece(f"]({destination})", "markup")


def emit_code(text: str, output_format: Format) -> Piece:
    """Emit inline code.

    Args:
        text: The code.
        output_format: `"typst"` or `"markdown"`.

    Returns:
        Typst or Markdown inline code.
    """
    if output_format == "typst":
        if "`" in text:
            return Piece(f"#raw({typst_string(text)})", "end")
        return Piece(f"`{text}`", "markup")
    fence = "`" * (max(map(len, re.findall(r"`+", text)), default=0) + 1)
    # A code span loses one space at each end if it has both, and ` next to the
    # fence would lengthen it:
    padded = text.startswith("`") or text.endswith("`")
    padded |= text.startswith(" ") and text.endswith(" ") and bool(text.strip(" "))
    padding = " " if padded else ""
    return Piece(fence + padding + text + padding + fence, "markup")


def character_class(character: str) -> Literal["space", "punctuation", "other"]:
    """Classify a character the way Markdown does for emphasis delimiters.

    Args:
        character: A character. The start and the end of a line count as a space.

    Returns:
        Its class.
    """
    code = ord(character)
    if markdown_it.common.utils.isWhiteSpace(code):
        return "space"
    if markdown_it.common.utils.isMdAsciiPunct(code) or (
        markdown_it.common.utils.isPunctChar(character)
    ):
        return "punctuation"
    return "other"


def can_open_and_close(delimiter: str, before: str, after: str) -> tuple[bool, bool]:
    """Tell whether a run of emphasis delimiters can open and close emphasis.

    Why:
        This is Markdown's flanking rule, as implemented by markdown-it.

    Args:
        delimiter: `*` or `_`.
        before: The character before the run.
        after: The character after the run.

    Returns:
        Whether the run can open, and whether it can close.
    """
    before_class, after_class = character_class(before), character_class(after)
    left_flanking = after_class != "space" and (
        after_class != "punctuation" or before_class != "other"
    )
    right_flanking = before_class != "space" and (
        before_class != "punctuation" or after_class != "other"
    )
    if delimiter == "*":
        return left_flanking, right_flanking
    return (
        left_flanking and (not right_flanking or before_class == "punctuation"),
        right_flanking and (not left_flanking or after_class == "punctuation"),
    )


def repair_delimiter_run(
    pieces: Sequence[Piece], sources: list[str], start: int, end: int
) -> bool:
    """Make a run of Markdown emphasis delimiters open and close as intended.

    Why:
        A run that can't open or close because of the characters around it is
        fixed by writing one of them as a character reference, which is literal
        text whose edges (`&` and `;`) are punctuation. Only text characters that
        are spaces or alphanumeric ever need it.

    Args:
        pieces: The pieces of a line.
        sources: Their sources, repaired in place.
        start: Index of the run's first piece.
        end: Index after the run's last piece.

    Returns:
        Whether a character was replaced.
    """
    opens = any(pieces[index].kind == "open" for index in range(start, end))
    closes = any(pieces[index].kind == "close" for index in range(start, end))
    previous = start - 1 if start else None
    following = end if end < len(pieces) else None
    before = sources[previous][-1] if previous is not None else " "
    after = sources[following][0] if following is not None else " "
    can_open, can_close = can_open_and_close(sources[start][0], before, after)
    if (can_open or not opens) and (can_close or not closes):
        return False
    if opens and not can_open:
        fix_after = character_class(after) == "space"
    else:
        fix_after = character_class(before) != "space"
    target = following if fix_after else previous
    if target is None or pieces[target].kind != "text":
        return False
    source = sources[target]
    # Underscores between word characters are literal, but a character reference
    # is punctuation, so the underscores next to it would become delimiters:
    if fix_after:
        rest = leading_underscores_pattern.sub(escape_underscores, source[1:])
        sources[target] = f"&#{ord(source[0])};" + rest
    else:
        rest = trailing_underscores_pattern.sub(escape_underscores, source[:-1])
        sources[target] = rest + f"&#{ord(source[-1])};"
    return True


def escape_typst_code_starts(source: str, line_rest: str) -> str:
    """Escape the `#`s of Markdown text that would start Typst code in its line.

    Why:
        RenderCV reads `#name(...)` in Markdown as Typst code, so text is escaped
        where it would be code. But what follows text in its line can complete
        an expression that the text only starts: `#a` before `[x](url)`, or `#a(`
        before `**)`.

    Args:
        source: Markdown of text.
        line_rest: The Markdown that follows it in its line.

    Returns:
        The Markdown, with those `#`s escaped.
    """
    characters: list[str] = []
    for position, character in enumerate(source):
        if (
            character == "#"
            and is_unescaped(source, position)
            and find_typst_expression_end(source[position:] + line_rest, 0) is not None
        ):
            characters.append("\\")
        characters.append(character)
    return "".join(characters)


def is_unescaped(source: str, position: int) -> bool:
    """Tell whether a character of Markdown isn't escaped by a backslash.

    Args:
        source: Markdown.
        position: Index of the character.

    Returns:
        Whether an even number of backslashes precedes the character.
    """
    before = source[:position]
    return (len(before) - len(before.rstrip("\\"))) % 2 == 0


def escape_underscores(match: re.Match[str]) -> str:
    """Escape every underscore of a match.

    Args:
        match: A match of underscores.

    Returns:
        The underscores, escaped.
    """
    return "\\_" * len(match.group())


def join_pieces(pieces: Sequence[Piece], output_format: Format) -> str:
    """Join the pieces of a line, repairing the boundaries between them.

    Why:
        In Typst, `(`, `[`, or `.field` right after an expression continues it
        (`#strong[Node].js` reads a field) and a `;` ends it, so `;` ends the
        expression first. In
        Markdown, an emphasis delimiter run must be flanked correctly to open or
        close (`**C++**17` isn't bold), so a text character next to it that
        prevents this is written as a character reference (`**C++**&#49;7`), and
        `#name` that what follows would make Typst code (`#a[link](url)`) is
        escaped.

    Args:
        pieces: The pieces of a line.
        output_format: `"typst"` or `"markdown"`.

    Returns:
        The line.
    """
    pieces = [piece for piece in pieces if piece.source]
    sources = [piece.source for piece in pieces]
    if output_format == "typst":
        for index in range(len(pieces) - 1):
            if pieces[index].kind == "end" and typst_continuation_pattern.match(
                sources[index + 1]
            ):
                sources[index] += ";"
        return "".join(sources)

    for index in range(1, len(pieces)):
        if pieces[index].kind == "link" and sources[index - 1].endswith("!"):
            # `![` would start an image:
            sources[index - 1] = sources[index - 1][:-1] + "\\!"

    # A `#` of text that the rest of the line makes Typst code (`#a` and `[x](url)`)
    # is escaped:
    for index, piece in enumerate(pieces):
        if piece.kind == "text":
            sources[index] = escape_typst_code_starts(
                sources[index], "".join(sources[index + 1 :])
            )

    # A repair can spoil a neighboring run, so runs are repaired until all work:
    repaired = True
    while repaired:
        repaired = False
        start = 0
        while start < len(pieces):
            if pieces[start].kind not in ("open", "close"):
                start += 1
                continue
            end = start + 1
            while (
                end < len(pieces)
                and pieces[end].kind in ("open", "close")
                and sources[end][0] == sources[start][0]
            ):
                end += 1
            repaired |= repair_delimiter_run(pieces, sources, start, end)
            start = end
    return "".join(sources)


def emit(nodes: Sequence[Node], output_format: Format) -> str:
    """Emit content as Typst or Markdown.

    Args:
        nodes: Content.
        output_format: `"typst"` or `"markdown"`.

    Returns:
        Typst or Markdown, one line per line of content.
    """
    lines = emit_lines(normalize(nodes), output_format)
    return "\n".join(
        line.marker + join_pieces(line.pieces, output_format) for line in lines
    )


def plain_text(nodes: Sequence[Node]) -> str:
    """Write content as plain text, without its formatting.

    Why:
        Metadata, like the document title, can't be formatted.

    Example:
        ```py
        plain_text(parse_content("**John** Doe's [CV](https://example.com)"))
        # Returns: "John Doe's CV"
        ```

    Args:
        nodes: Content.

    Returns:
        The text of the content. Typst code and math are kept as written.
    """
    parts: list[str] = []
    for node in nodes:
        match node:
            case Text(text) | Code(text):
                parts.append(text)
            case Raw(source) | ListMarker(source):
                parts.append(source)
            case Math(source):
                parts.append(f"$${source}$$")
            case Break():
                parts.append("\n")
            case (
                Strong(children)
                | Emph(children)
                | Link(children=children)
                | Summary(children)
            ):
                parts.append(plain_text(children))
            case Placeholder(name):
                message = f"The placeholder {name} was not filled."
                raise RenderCVInternalError(message)
    return "".join(parts)


def markdown_to_html(markdown: str, *, inline: bool = False) -> str:
    """Convert a Markdown document to HTML.

    Args:
        markdown: Markdown document.
        inline: Render inline content without a wrapping paragraph.

    Returns:
        HTML.
    """
    parser = markdown_it.MarkdownIt("commonmark")
    return parser.renderInline(markdown) if inline else parser.render(markdown)


def clean_url(url: str) -> str:
    """Shorten a URL for display by removing its scheme and trailing slash.

    Example:
        ```py
        clean_url("https://www.example.com/")
        # Returns: "www.example.com"
        ```

    Args:
        url: A URL.

    Returns:
        The URL without `https://`, `http://`, or a trailing slash.
    """
    return url.removeprefix("https://").removeprefix("http://").rstrip("/")
