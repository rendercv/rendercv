import functools
import re


@functools.lru_cache(maxsize=64)
def build_keyword_matcher_pattern(keywords: frozenset[str]) -> re.Pattern:
    pattern = (
        r"\b("
        + "|".join(sorted(map(re.escape, keywords), key=len, reverse=True))
        + r")\b"
    )
    return re.compile(pattern)
