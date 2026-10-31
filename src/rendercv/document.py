"""The name and date vocabulary shared by document metadata and output paths."""

from __future__ import annotations

from datetime import date as Date
from typing import TYPE_CHECKING

from rendercv.text import substitute_placeholders

if TYPE_CHECKING:
    from rendercv.schema.models.locale.locale import Locale
    from rendercv.schema.models.rendercv_model import RenderCVModel


def build_name_variants(name: str | None) -> dict[str, str]:
    """Generate all case/separator variants of a name for placeholder substitution.

    Why:
        Output file paths use placeholders like NAME_IN_LOWER_SNAKE_CASE.
        Centralizing variant generation avoids repeating the same
        null-check-and-transform pattern for each variant.

    Args:
        name: The CV owner's name, or None.

    Returns:
        Dictionary mapping placeholder names to their values, which are empty if
        there is no name.
    """
    name = name or ""
    return {
        "NAME": name,
        "NAME_IN_SNAKE_CASE": name.replace(" ", "_"),
        "NAME_IN_LOWER_SNAKE_CASE": name.replace(" ", "_").lower(),
        "NAME_IN_UPPER_SNAKE_CASE": name.replace(" ", "_").upper(),
        "NAME_IN_KEBAB_CASE": name.replace(" ", "-"),
        "NAME_IN_LOWER_KEBAB_CASE": name.replace(" ", "-").lower(),
        "NAME_IN_UPPER_KEBAB_CASE": name.replace(" ", "-").upper(),
    }


def build_document_placeholders(rendercv_model: RenderCVModel) -> dict[str, str]:
    """Build the placeholders of the document's file names, title, footer, and top note.

    Why:
        These are all about the same document, so they share one vocabulary: the
        CV owner's name (in several cases) and the current date.

    Args:
        rendercv_model: CV model.

    Returns:
        Placeholder names mapped to their values.
    """
    current_date = rendercv_model.settings._resolved_current_date
    locale = rendercv_model.locale
    return {
        "CURRENT_DATE": date_object_to_string(
            current_date,
            locale=locale,
            single_date_template=rendercv_model.design.templates.single_date,
        ),
        **build_date_placeholders(current_date, locale=locale),
        **build_name_variants(rendercv_model.cv.name),
    }


def build_date_placeholders(date: Date, *, locale: Locale) -> dict[str, str]:
    """Build all date-related template placeholders from a date and locale.

    Why:
        Date placeholders are needed in single_date templates, footer, top_note,
        and file path resolution. Centralizing construction eliminates duplication
        and ensures new placeholders propagate everywhere.

    Args:
        date: Date to extract components from.
        locale: Locale providing month names and abbreviations.

    Returns:
        Dict mapping placeholder names to their string values.
    """
    month = date.month
    day = date.day
    year = date.year

    return {
        "MONTH_NAME": locale.month_names[month - 1],
        "MONTH_ABBREVIATION": locale.month_abbreviations[month - 1],
        "MONTH": str(month),
        "MONTH_IN_TWO_DIGITS": f"{month:02d}",
        "DAY": str(day),
        "DAY_IN_TWO_DIGITS": f"{day:02d}",
        "DAY_ORDINAL": locale.day_ordinals[day - 1],
        "YEAR": str(year),
        "YEAR_IN_TWO_DIGITS": f"{year % 100:02d}",
    }


def date_object_to_string(
    date: Date, *, locale: Locale, single_date_template: str
) -> str:
    """Convert date object to localized string using template placeholders.

    Why:
        Date display varies by locale and user preference. Template-based
        formatting allows MONTH_ABBREVIATION YEAR or MONTH_NAME, YEAR without
        hardcoding formats for each language.

    Example:
        ```py
        result = date_object_to_string(
            Date(2025, 3, 15),
            locale=english_locale,
            single_date_template="MONTH_ABBREVIATION YEAR",
        )
        # Returns: "Mar 2025"
        ```

    Args:
        date: Date to format.
        locale: Locale providing month names and abbreviations.
        single_date_template: Template with date placeholders.

    Returns:
        Formatted date string with placeholders substituted.
    """
    return substitute_placeholders(
        single_date_template, build_date_placeholders(date, locale=locale)
    ).strip()
