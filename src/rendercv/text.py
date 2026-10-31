"""The string-rewriting kernel shared by every textual transformation of RenderCV.

Placeholder substitution, keyword bolding, and the recognition of raw Typst in
user content are all the same operation: find disjoint intervals of a string,
then rebuild the string from the intervals and the gaps between them. This module
implements that operation once: the output is assembled from the input exactly
once, in order, and replacements are never rescanned.
"""

import functools
import re
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class Segment:
    """A nonempty interval `[start, end)` of a string.

    Why:
        A partition of a string is a list of segments that are either matches
        (`matched=True`) or the gaps between them. Representing both the same way
        makes the reconstruction law `"".join(slices) == string` trivial to state.

    Args:
        start: Inclusive start index.
        end: Exclusive end index.
        matched: Whether the segment is a match (as opposed to a gap).
    """

    start: int
    end: int
    matched: bool


def partition(string: str, matches: Iterable[re.Match[str]]) -> Iterator[Segment]:
    """Split a string into its matches and the gaps between them.

    Why:
        Every textual rewrite in RenderCV is "replace some intervals, keep the
        rest". Rebuilding from a partition, instead of calling `str.replace`
        repeatedly, guarantees that replacements are never rescanned (no value
        can be mistaken for a placeholder) and that nothing is lost or duplicated.

    Example:
        ```py
        matches = re.finditer(r"\\d+", "a1b22")
        [(s.start, s.end, s.matched) for s in partition("a1b22", matches)]
        # [(0, 1, False), (1, 2, True), (2, 3, False), (3, 5, True)]
        ```

    Args:
        string: The string the matches refer to.
        matches: Nonempty, disjoint matches in increasing order (as produced by
            `re.finditer` with a pattern that cannot match the empty string).

    Yields:
        Segments covering the string exactly once, in order.
    """
    cursor = 0
    for match in matches:
        if cursor < match.start():
            yield Segment(cursor, match.start(), matched=False)
        yield Segment(match.start(), match.end(), matched=True)
        cursor = match.end()
    if cursor < len(string):
        yield Segment(cursor, len(string), matched=False)


def rewrite(
    string: str,
    pattern: re.Pattern[str],
    replace_match: Callable[[str], str],
    replace_gap: Callable[[str], str] = str,
) -> str:
    """Rebuild a string by transforming its matches and its gaps independently.

    Args:
        string: The string to rewrite.
        pattern: Pattern whose non-overlapping matches are transformed. It must
            not match the empty string.
        replace_match: Transformation of a matched substring.
        replace_gap: Transformation of an unmatched substring.

    Returns:
        The concatenation of the transformed segments, in order.
    """
    return "".join(
        (replace_match if segment.matched else replace_gap)(
            string[segment.start : segment.end]
        )
        for segment in partition(string, pattern.finditer(string))
    )


@functools.lru_cache(maxsize=128)
def literal_alternation(strings: frozenset[str]) -> re.Pattern[str]:
    """Compile a pattern matching any of the given strings, preferring longer ones.

    Why:
        Placeholder names overlap (`NAME` and `NAME_IN_SNAKE_CASE`), so the
        longest name must be tried first. Sorting by the length of the literal
        string (not of its escaped form) makes "longest wins" exact.

    Args:
        strings: Nonempty strings to match literally.

    Returns:
        Compiled pattern.
    """
    ordered = sorted(strings, key=lambda string: (-len(string), string))
    return re.compile("|".join(re.escape(string) for string in ordered))


@functools.lru_cache(maxsize=128)
def keyword_pattern(keywords: frozenset[str]) -> re.Pattern[str]:
    """Compile a pattern matching whole-word occurrences of keywords, longest first.

    Why:
        A keyword is bolded only where it stands on its own: `Python` doesn't
        match in `Pythonic`, `C++` doesn't match in `C++17`, and `.NET` doesn't
        match in `ASP.NET`. So the characters around a match must not be word
        characters, whatever the keyword's own first and last characters are.

    Args:
        keywords: Nonempty keywords to match literally.

    Returns:
        Compiled pattern.
    """
    return re.compile(rf"(?<!\w)(?:{literal_alternation(keywords).pattern})(?!\w)")


def substitute_placeholders(string: str, placeholders: dict[str, str]) -> str:
    """Replace every occurrence of a placeholder name with its value, in one pass.

    Why:
        Format strings (file names, dates, the PDF title) contain a fixed set of
        placeholder names, possibly glued to other text (`NAME_IN_SNAKE_CASE_CV`),
        so names are matched anywhere, longest first. Values are inserted verbatim
        and never scanned again.

    Example:
        ```py
        substitute_placeholders("NAME_CV_YEAR.pdf", {"NAME": "B", "YEAR": "2025"})
        # Returns: "B_CV_2025.pdf"
        ```

    Args:
        string: Format string.
        placeholders: Placeholder names mapped to their values.

    Returns:
        The format string with all placeholders replaced.
    """
    if not placeholders:
        return string
    pattern = literal_alternation(frozenset(placeholders))
    return rewrite(string, pattern, lambda name: placeholders[name])
