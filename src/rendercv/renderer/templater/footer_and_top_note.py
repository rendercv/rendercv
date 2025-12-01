from collections.abc import Callable
from datetime import date as Date

from rendercv.schema.models.locale.locale import Locale

from .date import date_object_to_string
from .string_processor import apply_string_processors, substitute_placeholders


def render_top_note_template(
    top_note_template: str,
    *,
    locale: Locale,
    current_date: Date,
    name: str | None,
    single_date_template: str,
    string_processors: list[Callable[[str], str]] | None = None,
) -> str:
    """Render top note by substituting placeholders and applying string processors.

    Why:
        Top notes display generation metadata like "Last Updated: Jan 2025" at
        document top. Template-based generation allows localization and custom
        formatting per user preference.

    Example:
        ```py
        result = render_top_note_template(
            "LAST_UPDATED: CURRENT_DATE",
            locale=english_locale,
            current_date=date(2025, 1, 15),
            name="John Doe",
            single_date_template="MONTH_ABBREVIATION YEAR"
        )
        # Returns: "Last Updated: Jan 2025"
        ```

    Args:
        top_note_template: Template with CURRENT_DATE, LAST_UPDATED, NAME placeholders.
        locale: Locale providing last_updated translation.
        current_date: Date for timestamp.
        name: CV owner name for placeholder substitution.
        single_date_template: Template for date formatting.
        string_processors: Optional processors for markdown parsing and formatting.

    Returns:
        Rendered top note with substituted placeholders.
    """
    if string_processors is None:
        string_processors = []

    placeholders: dict[str, str] = {
        "CURRENT_DATE": date_object_to_string(
            current_date,
            locale=locale,
            single_date_template=single_date_template,
        ),
        "LAST_UPDATED": locale.last_updated,
        "NAME": name or "",
    }
    return apply_string_processors(
        substitute_placeholders(top_note_template, placeholders), string_processors
    )


def render_footer_template(
    footer_template: str,
    *,
    locale: Locale,
    current_date: Date,
    name: str | None,
    single_date_template: str,
    string_processors: list[Callable[[str], str]] | None = None,
) -> str:
    """Render footer by substituting placeholders and wrapping in Typst context block.

    Why:
        Footers show page numbers and metadata on each page. Typst context blocks
        enable dynamic page number access. Template substitution handles localized
        dates and names before wrapping in required Typst syntax.

    Example:
        ```py
        result = render_footer_template(
            "NAME - Page PAGE_NUMBER of TOTAL_PAGES",
            locale=english_locale,
            current_date=date(2025, 1, 15),
            name="John Doe",
            single_date_template="MONTH_ABBREVIATION YEAR"
        )
        # Returns: "context { [John Doe - Page #str(here().page()) of #str(counter(page).final().first())] }"
        ```

    Args:
        footer_template: Template with NAME, PAGE_NUMBER, TOTAL_PAGES, CURRENT_DATE placeholders.
        locale: Locale for date formatting.
        current_date: Date for timestamp.
        name: CV owner name for placeholder substitution.
        single_date_template: Template for date formatting.
        string_processors: Optional processors for markdown parsing and formatting.

    Returns:
        Typst context block with rendered footer content.
    """
    if string_processors is None:
        string_processors = []

    placeholders: dict[str, str] = {
        "CURRENT_DATE": date_object_to_string(
            current_date,
            locale=locale,
            single_date_template=single_date_template,
        ),
        "NAME": name or "",
        "PAGE_NUMBER": "#str(here().page())",
        "TOTAL_PAGES": "#str(counter(page).final().first())",
    }
    return (
        "context {"
        f" [{apply_string_processors(substitute_placeholders(footer_template, placeholders), string_processors)}] }}"
    )
