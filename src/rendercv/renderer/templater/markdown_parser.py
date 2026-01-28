import itertools
import re
from xml.etree.ElementTree import Element

import markdown
import markdown.core

from rendercv.exception import RenderCVUserError


def to_typst_string(elem: Element) -> str:
    """Recursively convert XML Element tree to Typst markup string.

    Why:
        Python Markdown library outputs XML Element tree. Typst requires its
        own markup syntax for bold, italic, links, etc. Recursive traversal
        converts entire element tree including nested formatting.

    Args:
        elem: XML Element from Markdown parser.

    Returns:
        Typst-formatted string.
    """
    result = []

    # Handle the element's text content
    if elem.text:
        result.append(escape_typst_characters(elem.text))

    # Process child elements
    for child in elem:
        match child.tag:
            case "strong":
                # Bold: **text** -> #strong[text]
                inner = to_typst_string(child)
                child_content = f"#strong[{inner}]"

            case "em":
                # Italic: *text* -> #emph[text]
                inner = to_typst_string(child)
                child_content = f"#emph[{inner}]"

            case "code":
                # Inline code: `text` -> `text`
                # Code content is already escaped by the parser
                child_content = f"`{child.text}`"

            case "a":
                # Link: [text](url) -> #link("url")[text]
                href = child.get("href", "")
                inner = to_typst_string(child)
                child_content = f'#link("{href}")[{inner}]'
                if not href:
                    message = (
                        f"Link url is not provided for [{inner}](url) in the YAML file!"
                    )
                    raise RenderCVUserError(message)

            case "div":
                child_content = (
                    "#summary["
                    + to_typst_string(child).strip("\n").replace("\n", " \\ ")
                    + "]"
                )

            case _:
                if getattr(child, "attrib", {}).get("class") == "admonition-title":
                    continue
                child_content = to_typst_string(child)

        result.append(child_content)

        # Handle tail text (text after the closing tag of child)
        if child.tail:
            result.append(escape_typst_characters(child.tail))

    return "".join(result)


typst_command_pattern = re.compile(r"#([A-Za-z][^\s()\[]*)(\([^)]*\))?(\[[^\]]*\])?")
math_pattern = re.compile(r"(\$\$.*?\$\$)")


def escape_typst_characters(string: str) -> str:
    """Escape Typst special characters while preserving Typst commands and math.

    Why:
        User content may contain Typst special characters like `#`, `$`, `[` that
        would break compilation. Escaping prevents interpretation as commands.
        Existing Typst commands and math must remain unescaped.

    Args:
        string: Text to escape.

    Returns:
        Escaped string safe for Typst.
    """
    if string == "\n":
        return string

    # Find all the Typst commands, and keep them separate so that nothing is escaped
    # inside the commands.
    typst_command_mapping = {}
    for i, match in enumerate(
        itertools.chain(
            math_pattern.finditer(string),
            typst_command_pattern.finditer(string),
        )
    ):
        dummy_name = f"RENDERCVTYPSTCOMMANDORMATH{i}"
        typst_command_mapping[dummy_name] = match.group(0)
        string = string.replace(typst_command_mapping[dummy_name], dummy_name)
        typst_command_mapping[dummy_name] = typst_command_mapping[dummy_name].replace(
            "$$", "$"
        )

    # Add the tail after the last match
    escape_dictionary = {
        "[": "\\[",
        "]": "\\]",
        "\\": "\\\\",
        '"': '\\"',
        "#": "\\#",
        "$": "\\$",
        "@": "\\@",
        "%": "\\%",
        "~": "\\~",
        "_": "\\_",
        "/": "\\/",
        ">": "\\>",
        "<": "\\<",
    }

    string = string.translate(str.maketrans(escape_dictionary))

    # string.translate() only supports single-character replacements, so we need to
    # handle the longer replacements separately.
    longer_escape_dictionary = {
        "* ": "#sym.ast.basic ",
        "*": "#sym.ast.basic#h(0pt, weak: true) ",
    }
    for key, value in longer_escape_dictionary.items():
        string = string.replace(key, value)

    # Replace the dummy names with the full Typst commands
    for dummy_name, full_command in typst_command_mapping.items():
        string = string.replace(dummy_name, full_command)

    return string


# Create a Markdown instance
md = markdown.core.Markdown(extensions=["admonition"])
md.output_formats["typst"] = to_typst_string  # pyright: ignore[reportArgumentType]
md.set_output_format("typst")  # pyright: ignore[reportArgumentType]
md.parser.blockprocessors.deregister("hashheader")
md.parser.blockprocessors.deregister("setextheader")
md.parser.blockprocessors.deregister("olist")
md.parser.blockprocessors.deregister("ulist")
md.parser.blockprocessors.deregister("quote")
md.stripTopLevelTags = False


def markdown_to_typst(markdown_string: str) -> str:
    """Convert Markdown string to Typst markup.

    Why:
        Users write content in Markdown for readability. Typst compilation
        requires Typst markup. Custom Markdown parser with Typst output
        format bridges this gap.

    Args:
        markdown_string: Markdown content.

    Returns:
        Typst-formatted string.
    """
    return md.convert(markdown_string)


def markdown_to_html(markdown_string: str) -> str:
    """Convert Markdown string to HTML using python-markdown library.

    Args:
        markdown_string: Markdown content.

    Returns:
        HTML-formatted string.
    """
    return markdown.markdown(markdown_string)
