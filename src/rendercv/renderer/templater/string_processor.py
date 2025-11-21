import functools
import re

import pydantic


@functools.lru_cache(maxsize=64)
def build_keyword_matcher_pattern(keywords: frozenset[str]) -> re.Pattern:
    if not keywords:
        message = "Keywords cannot be empty"
        raise ValueError(message)
    pattern = (
        r"\b("
        + "|".join(sorted(map(re.escape, keywords), key=len, reverse=True))
        + r")\b"
    )
    return re.compile(pattern)


def make_keywords_bold(string: str, keywords: list[str]) -> str:
    if not keywords:
        return string
    pattern = build_keyword_matcher_pattern(frozenset(keywords))
    return pattern.sub(lambda m: f"**{m.group(0)}**", string)


def substitute_placeholders(string: str, placeholders: dict[str, str]) -> str:
    if not placeholders:
        return string

    pattern = build_keyword_matcher_pattern(frozenset(placeholders.keys()))
    return pattern.sub(lambda m: placeholders[m.group(0)], string)


def clean_url(url: str | pydantic.HttpUrl) -> str:
    """Make a URL clean by removing the protocol, www, and trailing slashes.

    Example:
        ```python
        make_a_url_clean("https://www.example.com/")
        ```
        returns
        `"example.com"`

    Args:
        url: The URL to make clean.

    Returns:
        The clean URL.
    """
    url = str(url).replace("https://", "").replace("http://", "")
    if url.endswith("/"):
        url = url[:-1]

    return url
