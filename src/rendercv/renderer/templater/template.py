"""Templates: content with UPPERCASE placeholders, filled with content.

A template (`design.templates.*`, the footer, the top note, locale phrases) is
content in which UPPERCASE words are placeholders. Filling a template is a tree
operation: the template is parsed once, missing placeholders are removed together
with the formatting, brackets, and separators that only existed for them, and the
remaining placeholders are replaced by their values, which are themselves parsed
content. Values are never parsed or scanned again, so a value can never be
mistaken for a placeholder or for Markdown.
"""

import dataclasses
import functools
import itertools
import re
from collections.abc import Callable, Mapping, Sequence

from rendercv.text import literal_alternation, partition, rewrite

from .markup import (
    Break,
    Emph,
    Format,
    Link,
    Node,
    Placeholder,
    Raw,
    Strong,
    Summary,
    Text,
    emit,
    normalize,
    parse_content,
)

# A known name followed by an UPPERCASE letter is part of a longer word. In entry
# templates, a known name after an underscore is too: `CO_AUTHORS` names an
# arbitrary key, not `AUTHORS`. Document templates have no arbitrary keys, so there
# an underscore separates names, as in `NAME_CV_YEAR`:
known_placeholder_patterns = {
    True: "(?<![A-Z0-9_])(?:{names})(?![A-Z])",
    False: "(?<![A-Z0-9])(?:{names})(?![A-Z])",
}
# An unknown UPPERCASE word names an arbitrary key that the entry doesn't have:
unknown_placeholder_pattern = "(?<![A-Za-z0-9_])[A-Z][A-Z0-9_]+(?![A-Za-z0-9_])"


@functools.lru_cache(maxsize=256)
def placeholder_pattern(
    names: frozenset[str], *, open_vocabulary: bool
) -> re.Pattern[str]:
    """Compile the pattern that finds placeholders in template text.

    Why:
        A placeholder is a known name at the start of a run of UPPERCASE letters,
        digits, and underscores, not followed by another UPPERCASE letter. So
        `NAME_IN_SNAKE_CASE_CV` contains `NAME_IN_SNAKE_CASE`, `DAYth` contains
        `DAY`, and `בAREA` contains `AREA`, but `UNNAMED` doesn't contain `NAME`.
        With an open vocabulary (entry templates can reference arbitrary keys),
        any other UPPERCASE word of two or more characters is a placeholder too.
        With a closed one, a known name may also follow an underscore, so
        `NAME_CV_YEAR` contains `NAME` and `YEAR`.

    Args:
        names: Known placeholder names.
        open_vocabulary: Whether unknown UPPERCASE words are placeholders.

    Returns:
        Compiled pattern.
    """
    alternatives = []
    if names:
        alternatives.append(
            known_placeholder_patterns[open_vocabulary].format(
                names=literal_alternation(names).pattern
            )
        )
    if open_vocabulary:
        alternatives.append(unknown_placeholder_pattern)
    return re.compile("|".join(alternatives) if alternatives else "(?!)")


@dataclasses.dataclass(frozen=True)
class Template:
    """A parsed template.

    Args:
        nodes: Content with placeholders.
        pattern: Pattern of the template's placeholders, used inside Typst code.
    """

    nodes: tuple[Node, ...]
    pattern: re.Pattern[str]


def compile_template(
    source: str,
    names: frozenset[str],
    *,
    open_vocabulary: bool = False,
    phrases: Mapping[str, str] | None = None,
) -> Template:
    """Parse a template.

    Args:
        source: The template.
        names: Known placeholder names.
        open_vocabulary: Whether unknown UPPERCASE words are placeholders.
        phrases: Phrase placeholders (e.g. `DEGREE_WITH_AREA`) mapped to their
            templates (e.g. `DEGREE in AREA`), which are spliced in, so that their
            placeholders take part in the removal of missing placeholders.

    Returns:
        The parsed template.
    """
    phrases = phrases or {}
    pattern = placeholder_pattern(
        names | frozenset(phrases), open_vocabulary=open_vocabulary
    )
    inner_pattern = placeholder_pattern(names, open_vocabulary=open_vocabulary)

    def convert(nodes: Sequence[Node]) -> tuple[Node, ...]:
        converted: list[Node] = []
        for node in nodes:
            match node:
                case Text(text):
                    for segment in partition(text, pattern.finditer(text)):
                        substring = text[segment.start : segment.end]
                        if not segment.matched:
                            converted.append(Text(substring))
                        elif substring in phrases:
                            phrase = compile_template(
                                phrases[substring],
                                names,
                                open_vocabulary=open_vocabulary,
                            )
                            converted.extend(phrase.nodes)
                        else:
                            converted.append(Placeholder(substring))
                case Strong(children) | Emph(children) | Link(children=children):
                    converted.append(
                        dataclasses.replace(node, children=convert(children))
                    )
                case _:
                    converted.append(node)
        return tuple(converted)

    return Template(convert(parse_content(source)), inner_pattern)


def placeholder_names(nodes: Sequence[Node]) -> list[str]:
    """List the placeholders of a template's content in reading order.

    Args:
        nodes: Content of a template.

    Returns:
        The names of its placeholders, once per occurrence.
    """
    names: list[str] = []
    for node in nodes:
        match node:
            case Placeholder(name):
                names.append(name)
            case Strong(children) | Emph(children) | Link(children=children):
                names.extend(placeholder_names(children))
    return names


def fill_template(
    template: Template,
    values: Mapping[str, Sequence[Node]],
    output_format: Format,
) -> tuple[Node, ...]:
    """Fill a template with values.

    Why:
        Missing placeholders are removed first (see `remove_missing`), then the
        remaining placeholders are replaced by their values. A line that contains
        only `SUMMARY` is a summary block. Lines are independent.

    Args:
        template: The parsed template.
        values: Placeholder names mapped to content. A missing or blank value means
            the placeholder is missing.
        output_format: The format that Typst code in the template is filled for.

    Returns:
        The filled content.
    """

    def is_present(name: str) -> bool:
        return name in values and not is_blank(values[name])

    def fill(nodes: Sequence[Node]) -> list[Node]:
        filled: list[Node] = []
        for node in nodes:
            match node:
                case Placeholder(name):
                    filled.extend(values[name])
                case Raw(source):
                    filled.append(
                        Raw(
                            rewrite(
                                source,
                                template.pattern,
                                lambda name: (
                                    emit(values[name], output_format)
                                    if is_present(name)
                                    else ""
                                ),
                            )
                        )
                    )
                case Strong(children) | Emph(children) | Link(children=children):
                    filled.append(
                        dataclasses.replace(node, children=tuple(fill(children)))
                    )
                case _:
                    filled.append(node)
        return filled

    lines: list[tuple[Node, ...]] = []
    for line in split_lines(template.nodes):
        cleaned = remove_missing(line, is_present, template.pattern)
        if cleaned is None:
            continue
        if cleaned == (Placeholder("SUMMARY"),):
            lines.append((Summary(tuple(values["SUMMARY"])),))
        else:
            lines.append(strip_line(normalize(tuple(fill(cleaned)))))

    result: list[Node] = []
    for index, line in enumerate(lines):
        if index:
            result.append(Break())
        result.extend(line)
    return tuple(result)


def split_lines(nodes: Sequence[Node]) -> list[tuple[Node, ...]]:
    """Split content at its top-level line breaks.

    Args:
        nodes: Content.

    Returns:
        The lines.
    """
    lines: list[list[Node]] = [[]]
    for node in nodes:
        if isinstance(node, Break):
            lines.append([])
        else:
            lines[-1].append(node)
    return [tuple(line) for line in lines]


def strip_line(line: tuple[Node, ...]) -> tuple[Node, ...]:
    """Remove the whitespace at the start and the end of a line.

    Args:
        line: A line of content.

    Returns:
        The line without surrounding whitespace.
    """
    nodes = list(line)
    if nodes and isinstance(nodes[0], Text):
        nodes[0] = Text(nodes[0].text.lstrip())
    if nodes and isinstance(nodes[-1], Text):
        nodes[-1] = Text(nodes[-1].text.rstrip())
    return normalize(tuple(nodes))


def is_blank(nodes: Sequence[Node]) -> bool:
    """Tell whether content is empty or only whitespace.

    Args:
        nodes: Content.

    Returns:
        Whether the content is blank.
    """
    return all(isinstance(node, Text) and not node.text.strip() for node in nodes)


# ======================================================================================
# Removal of missing placeholders
# ======================================================================================


@dataclasses.dataclass(frozen=True)
class Group:
    """Template content enclosed by a pair of brackets, e.g. `(JOURNAL)`."""

    opening: str
    children: tuple["Node | Group", ...]
    closing: str


type Item = Node | Group

closing_bracket_of = {"(": ")", "[": "]", "{": "}"}


def group_brackets(nodes: Sequence[Item]) -> list[Item]:
    """Turn the balanced brackets in text into groups.

    Why:
        Brackets are structure: in `URL (JOURNAL)` the parentheses belong to
        `JOURNAL` and disappear with it; in `(URL JOURNAL)` they stay as long as
        one of the two is present.

    Args:
        nodes: The nodes of one line or container.

    Returns:
        The nodes, with balanced brackets grouped.
    """
    stack: list[tuple[str, list[Item]]] = [("", [])]
    for node in nodes:
        if not isinstance(node, Text):
            stack[-1][1].append(node)
            continue
        for piece in re.split(r"([()[\]{}])", node.text):
            if piece in closing_bracket_of:
                stack.append((piece, []))
            elif len(stack) > 1 and piece == closing_bracket_of[stack[-1][0]]:
                opening, children = stack.pop()
                stack[-1][1].append(Group(opening, tuple(children), piece))
            elif piece:
                stack[-1][1].append(Text(piece))
    # Unbalanced opening brackets are text:
    while len(stack) > 1:
        opening, children = stack.pop()
        stack[-1][1].extend([Text(opening), *children])
    return stack[0][1]


def remove_words(separator: str) -> str:
    """Remove the words (connectors like `in`, `at`, `en`) from a separator.

    Args:
        separator: Text between two items.

    Returns:
        The separator's punctuation, or an empty string if it had none.
    """
    kept = " ".join(
        token for token in separator.split() if not re.search(r"[^\W\d_]", token)
    )
    if not kept:
        return ""
    leading = " " if separator[0].isspace() else ""
    trailing = " " if separator[-1].isspace() else ""
    return leading + kept + trailing


def remove_missing(
    nodes: Sequence[Item],
    is_present: Callable[[str], bool],
    pattern: re.Pattern[str],
) -> tuple[Node, ...] | None:
    """Remove missing placeholders and everything that only existed for them.

    Why:
        `**INSTITUTION**, DEGREE in AREA -- LOCATION` must read naturally whichever
        fields are missing. The rule is structural and uniform. Content is a
        sequence of items (placeholders, formatting, bracket groups, Typst code)
        and the separator text between them. Formatting and groups that only
        contained missing placeholders disappear. Separators that touched a removed
        item disappear at the start or the end of a line or container; between two
        remaining items, a single separator is kept: the last one that has
        punctuation once its words (`in`, `at`) are removed, or else a space.
        Content without missing placeholders is never changed.

    Args:
        nodes: The nodes of one line or container.
        is_present: Whether a placeholder has a value.
        pattern: Pattern of placeholders inside Typst code.

    Returns:
        The cleaned nodes, or None if nothing remains: the line or container only
        existed for missing placeholders.
    """
    items: list[Item] = []
    removed: list[bool] = []
    for original in group_brackets(nodes):
        item = original
        match item:
            case Placeholder(name):
                is_removed = not is_present(name)
            case (
                Group(children=children)
                | Strong(children)
                | Emph(children)
                | Link(children=children)
            ):
                cleaned = remove_missing(children, is_present, pattern)
                is_removed = cleaned is None
                if cleaned is not None:
                    item = dataclasses.replace(item, children=cleaned)
            case Raw(source):
                names = pattern.findall(source)
                is_removed = bool(names) and not any(map(is_present, names))
            case _:
                is_removed = False
        items.append(item)
        removed.append(is_removed)

    if not any(removed):
        return flatten(items)

    kept = [
        index
        for index, item in enumerate(items)
        if not removed[index] and not isinstance(item, Text)
    ]
    if not kept:
        return None

    result: list[Item] = []
    boundaries = [-1, *kept, len(items)]
    for left, right in itertools.pairwise(boundaries):
        run = range(left + 1, right)
        if not any(removed[index] for index in run):
            result.extend(items[index] for index in run)
        elif left != -1 and right != len(items):
            separators = [
                remove_words(item.text)
                for index in run
                if isinstance(item := items[index], Text)
            ]
            punctuated = [separator for separator in separators if separator]
            result.append(Text(punctuated[-1] if punctuated else " "))
        if right != len(items):
            result.append(items[right])
    return flatten(result)


def flatten(items: Sequence[Item]) -> tuple[Node, ...]:
    """Turn bracket groups back into text.

    Args:
        items: Nodes and groups.

    Returns:
        Nodes.
    """
    nodes: list[Node] = []
    for item in items:
        if isinstance(item, Group):
            nodes.append(Text(item.opening))
            nodes.extend(flatten(item.children))
            nodes.append(Text(item.closing))
        else:
            nodes.append(item)
    return normalize(tuple(nodes))
