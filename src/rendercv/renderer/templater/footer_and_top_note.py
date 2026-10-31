from collections.abc import Mapping

from .markup import Node, Raw, parse_content
from .template import compile_template, fill_template


def fill_document_template(
    template: str, placeholders: Mapping[str, str | tuple[Node, ...]]
) -> tuple[Node, ...]:
    """Fill a template about the whole document (the title, the footer, the top note).

    Why:
        Typst code in these templates is filled for Typst: the footer and the top
        note exist only in Typst, and the title is plain text.

    Args:
        template: Template with document placeholders.
        placeholders: Placeholder names mapped to strings (parsed as content) or
            content.

    Returns:
        The filled template.
    """
    values = {
        name: parse_content(value) if isinstance(value, str) else value
        for name, value in placeholders.items()
    }
    return fill_template(compile_template(template, frozenset(values)), values, "typst")


def render_top_note_template(
    top_note_template: str, *, placeholders: Mapping[str, str], last_updated: str
) -> tuple[Node, ...]:
    """Fill the top note template, e.g. "Last updated in Jan 2025".

    Args:
        top_note_template: Template with LAST_UPDATED and document placeholders.
        placeholders: The document placeholders (name and current date).
        last_updated: The locale's translation of "Last updated in".

    Returns:
        The top note.
    """
    return fill_document_template(
        top_note_template, {**placeholders, "LAST_UPDATED": last_updated}
    )


def render_footer_template(
    footer_template: str, *, placeholders: Mapping[str, str]
) -> tuple[Node, ...]:
    """Fill the footer template, e.g. "John Doe -- 1/2".

    Args:
        footer_template: Template with PAGE_NUMBER, TOTAL_PAGES, and document
            placeholders.
        placeholders: The document placeholders (name and current date).

    Returns:
        The footer. Page numbers are Typst code evaluated on each page.
    """
    return fill_document_template(
        footer_template,
        {
            **placeholders,
            "PAGE_NUMBER": (Raw("#str(here().page())"),),
            "TOTAL_PAGES": (Raw("#str(counter(page).final().first())"),),
        },
    )
