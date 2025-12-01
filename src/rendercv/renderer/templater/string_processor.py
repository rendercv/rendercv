import functools
import re
from collections.abc import Callable
from typing import overload

import pydantic

from rendercv.exception import RenderCVInternalError


@overload
def apply_string_processors(
    string: None, string_processors: list[Callable[[str], str]]
) -> None: ...
@overload
def apply_string_processors(
    string: str, string_processors: list[Callable[[str], str]]
) -> str: ...
def apply_string_processors(
    string: str | None, string_processors: list[Callable[[str], str]]
) -> str | None:
    """Apply sequence of string transformation functions via reduce.

    Why:
        Multiple transformations (markdown parsing, keyword bolding, escaping)
        need sequential application. Functional reduce pattern chains processors
        cleanly without intermediate variables.

    Args:
        string: Input string or None.
        string_processors: Functions to apply in order.

    Returns:
        Transformed string, or None if input was None.
    """
    if string is None:
        return string
    return functools.reduce(lambda v, f: f(v), string_processors, string)


@functools.lru_cache(maxsize=64)
def build_keyword_matcher_pattern(keywords: frozenset[str]) -> re.Pattern:
    """Build cached regex pattern for matching keywords with longest-first priority.

    Why:
        Keyword matching happens repeatedly during rendering. Cached patterns
        avoid recompilation. Longest-first sorting prevents "Python" from matching
        before "Python 3" in same text.

    Args:
        keywords: Set of keywords to match.

    Returns:
        Compiled regex pattern.
    """
    if not keywords:
        message = "Keywords cannot be empty"
        raise RenderCVInternalError(message)

    pattern = (
        "(" + "|".join(sorted(map(re.escape, keywords), key=len, reverse=True)) + ")"
    )
    return re.compile(pattern)


def make_keywords_bold(string: str, keywords: list[str]) -> str:
    """Wrap all keyword occurrences in Markdown bold syntax.

    Why:
        Users configure keywords like "Python" or "Machine Learning" to highlight
        in their CV. Automatic bolding applies consistent emphasis across all
        content without manual markup.

    Example:
        ```py
        result = make_keywords_bold("Expert in Python and Java", ["Python"])
        # Returns: "Expert in **Python** and Java"
        ```

    Args:
        string: Text to process.
        keywords: Keywords to make bold.

    Returns:
        String with keywords wrapped in ** markers.
    """
    if not keywords:
        return string

    pattern = build_keyword_matcher_pattern(frozenset(keywords))
    return pattern.sub(lambda m: f"**{m.group(0)}**", string)


def substitute_placeholders(string: str, placeholders: dict[str, str]) -> str:
    """Replace all placeholder occurrences with their values.

    Why:
        Output file names use placeholders like NAME and YEAR for dynamic naming.
        Pattern matching with longest-first ensures "YEAR_IN_TWO_DIGITS" matches
        before "YEAR" in same string.

    Example:
        ```py
        result = substitute_placeholders(
            "NAME_CV_YEAR.pdf",
            {"NAME": "John_Doe", "YEAR": "2025"}
        )
        # Returns: "John_Doe_CV_2025.pdf"
        ```

    Args:
        string: Template string with placeholders.
        placeholders: Map of placeholder names to replacement values.

    Returns:
        String with all placeholders replaced.
    """
    if not placeholders:
        return string

    pattern = build_keyword_matcher_pattern(frozenset(placeholders.keys()))
    return pattern.sub(lambda m: placeholders[m.group(0)], string).strip()


def clean_url(url: str | pydantic.HttpUrl) -> str:
    """Remove protocol, www, and trailing slashes from URL.

    Why:
        CV formatting displays cleaner URLs without https:// prefix. Used as
        Jinja2 filter in templates for consistent URL presentation.

    Example:
        ```py
        result = clean_url("https://www.example.com/")
        # Returns: "example.com"
        ```

    Args:
        url: URL to clean.

    Returns:
        Clean URL string.
    """
    url = str(url).replace("https://", "").replace("http://", "")
    if url.endswith("/"):
        url = url[:-1]

    return url
