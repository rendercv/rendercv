import re
from collections.abc import Iterable
from functools import lru_cache


@lru_cache(maxsize=64)
def _build_regex(keywords_frozen: frozenset[str]) -> re.Pattern:
    uniq = {k for k in keywords_frozen if k}
    if not uniq:
        # compile a regex that never matches
        return re.compile(r"(?!x)x")

    pattern = (
        r"\b(" + "|".join(sorted(map(re.escape, uniq), key=len, reverse=True)) + r")\b"
    )
    return re.compile(pattern, flags=re.IGNORECASE)


def make_keywords_bold(string: str, keywords: Iterable[str]) -> str:
    regex = _build_regex(frozenset(keywords))
    return regex.sub(lambda m: f"**{m.group(0)}**", string)
