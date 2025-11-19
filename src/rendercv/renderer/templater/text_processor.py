import re

from .regex import build_keyword_matcher_pattern


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


def process_formatting(text: str) -> str:
    # Order matters! Process longer patterns first to avoid conflicts

    # ***text*** -> #strong[#emph[text]] (bold + italic)
    text = re.sub(
        r"\*\*\*(?!\s)(.+?)(?<!\s)\*\*\*", r"#strong[#emph[\1]]", text, flags=re.DOTALL
    )

    # **text** -> #strong[text] (bold)
    text = re.sub(r"\*\*(?!\s)(.+?)(?<!\s)\*\*", r"#strong[\1]", text, flags=re.DOTALL)

    # *text* -> #emph[text] (italic)
    return re.sub(r"\*(?!\s)(.+?)(?<!\s)\*", r"#emph[\1]", text, flags=re.DOTALL)
