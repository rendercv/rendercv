from xml.etree.ElementTree import Element

from markdown.core import Markdown


def to_typst_string(elem: Element) -> str:
    """
    Recursively serialize an ElementTree Element to Typst format.

    Args:
        elem: The Element to serialize

    Returns:
        A string in Typst format
    """
    result = []

    # Handle the element's text content
    if elem.text:
        result.append(elem.text)

    # Process child elements
    for child in elem:
        tag = child.tag

        match tag:
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
            result.append(child.tail)

    return "".join(result)


# Create a Markdown instance
md = Markdown()

# Register the Typst serializer
md.output_formats["typst"] = to_typst_string  # pyright: ignore[reportArgumentType]


def markdown_to_typst(markdown_string: str) -> str:
    md.set_output_format("typst")  # pyright: ignore[reportArgumentType]
    return md.convert(markdown_string)
