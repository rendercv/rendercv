import functools
import re

import pydantic


def make_keywords_bold(string: str, keywords: list[str]) -> str:
    pattern = build_keyword_matcher_pattern(frozenset(keywords))
    return pattern.sub(lambda m: f"**{m.group(0)}**", string)


def markdown_to_typst(markdown_string: str) -> str:
    # Use a unique placeholder that won't appear in normal text
    escaped_asterisk = "\x00ESC_AST\x00"
    inline_code = "\x00CODE_{}\x00"

    # Step 1: Protect escaped asterisks (handle both \* and \\*)
    text = markdown_string.replace("\\\\*", escaped_asterisk)
    text = text.replace("\\*", escaped_asterisk)

    # Step 2: Protect inline code blocks (don't process anything inside backticks)
    code_blocks = []

    def save_code(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return inline_code.format(len(code_blocks) - 1)

    text = re.sub(r"`[^`]+`", save_code, text)

    # Step 3: Convert links [text](url) -> #link("url")[text]
    # Use non-greedy matching and handle nested brackets better
    def replace_link(match: re.Match) -> str:
        link_text = match.group(1)
        link_url = match.group(2)
        # Recursively process link text for nested formatting
        processed_text = process_formatting(link_text)
        return f'#link("{link_url}")[{processed_text}]'

    # Match links with proper bracket balancing
    text = re.sub(
        r"\[([^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*)\]\(([^)]+)\)", replace_link, text
    )

    # Step 4: Process formatting (bold/italic)
    text = process_formatting(text)

    # Step 5: Restore escaped asterisks as literal asterisks
    text = text.replace(escaped_asterisk, "*")

    # Step 6: Convert remaining literal asterisks to Typst symbols
    # This handles asterisks that weren't part of formatting
    text = re.sub(r"\*(?= )", "#sym.ast.basic", text)  # Asterisk followed by space
    text = re.sub(r"\*", "#sym.ast.basic#h(0pt, weak: true) ", text)  # Other asterisks

    # Step 7: Restore inline code blocks
    for idx, code in enumerate(code_blocks):
        text = text.replace(inline_code.format(idx), code)

    return text


bold_and_italic_pattern = re.compile(r"\*\*\*(?!\s)(.+?)(?<!\s)\*\*\*")
bold_pattern = re.compile(r"\*\*(?!\s)(.+?)(?<!\s)\*\*")
italic_pattern = re.compile(r"\*(?!\s)(.+?)(?<!\s)\*")


def process_formatting(text: str) -> str:
    # Order matters! Process longer patterns first to avoid conflicts

    # ***text*** -> #strong[#emph[text]] (bold + italic)
    text = re.sub(bold_and_italic_pattern, r"#strong[#emph[\1]]", text, flags=re.DOTALL)

    # **text** -> #strong[text] (bold)
    text = re.sub(bold_pattern, r"#strong[\1]", text, flags=re.DOTALL)

    # *text* -> #emph[text] (italic)
    return re.sub(italic_pattern, r"#emph[\1]", text, flags=re.DOTALL)


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


@functools.lru_cache(maxsize=64)
def build_keyword_matcher_pattern(keywords: frozenset[str]) -> re.Pattern:
    pattern = (
        r"\b("
        + "|".join(sorted(map(re.escape, keywords), key=len, reverse=True))
        + r")\b"
    )
    return re.compile(pattern)
