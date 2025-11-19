from .regex import build_keyword_matcher_pattern


def make_keywords_bold(string: str, keywords: list[str]) -> str:
    pattern = build_keyword_matcher_pattern(frozenset(keywords))
    return pattern.sub(lambda m: f"**{m.group(0)}**", string)
