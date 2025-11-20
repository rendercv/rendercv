import re
from xml.etree.ElementTree import Element

from markdown.core import Markdown


def to_typst_string(elem: Element) -> str:
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

            case _:
                child_content = to_typst_string(child)

        result.append(child_content)

        # Handle tail text (text after the closing tag of child)
        if child.tail:
            result.append(escape_typst_characters(child.tail))

    return "".join(result)


typst_command_pattern = re.compile(r"#([A-Za-z][^\s()\[]*)(\([^)]*\))?(\[[^\]]*\])?")


def escape_typst_characters(string: str) -> str:
    # Find all the Typst commands, and keep them seperate so that nothing is escaped
    # inside the commands.
    typst_command_mapping = {}
    result = []
    last_end = 0
    for i, match in enumerate(typst_command_pattern.finditer(string)):
        # Add text before this match
        start, end = match.span()
        result.append(string[last_end:start])

        dummy_name = f"RENDERCVTYPSTCOMMAND{i}"
        result.append(dummy_name)

        # Store the full matched command
        typst_command_mapping[dummy_name] = match.group(0)

        last_end = end

    # Add the tail after the last match
    result.append(string[last_end:])
    string = "".join(result)

    escape_dictionary = {
        "[": "\\[",
        "]": "\\]",
        "(": "\\(",
        ")": "\\)",
        "\\": "\\\\",
        '"': '\\"',
        "#": "\\#",
        "$": "\\$",
        "@": "\\@",
        "%": "\\%",
        "~": "\\~",
        "_": "\\_",
        "/": "\\/",
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
md = Markdown()

# Disable stripping of top-level tags since Typst doesn't use HTML wrapper tags
md.stripTopLevelTags = False

# Register the Typst serializer
md.output_formats["typst"] = to_typst_string  # pyright: ignore[reportArgumentType]


def markdown_to_typst(markdown_string: str) -> str:
    md.set_output_format("typst")  # pyright: ignore[reportArgumentType]
    return md.convert(markdown_string)


def markdown_to_html(markdown_string: str) -> str:
    md.set_output_format("html")
    return md.convert(markdown_string)
