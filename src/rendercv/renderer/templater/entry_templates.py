import pydantic

from rendercv.data import PublicationEntry
from rendercv.schema.models.cv.section import Entry
from rendercv.schema.models.locale.locale import Locale

from .date import compute_date_string
from .regex import build_keyword_matcher_pattern
from .text_processor import clean_url


def compute_entry_templates(
    entry: Entry,
    entry_options: pydantic.BaseModel,
    locale: Locale,
) -> dict[str, str]:
    if isinstance(entry, str):
        return {}

    templates = {
        key: value.replace("\n", "\n\n")
        for key, value in entry_options.model_dump().items()
        if key.endswith("_template") and isinstance(value, str)
    }
    placeholders = {key.upper(): value for key, value in entry.model_dump().items()}

    # Handle special placeholders:
    if "HIGHLIGHTS" in placeholders:
        placeholders["HIGHLIGHTS"] = handle_highlights(placeholders["HIGHLIGHTS"])

    if "AUTHORS" in placeholders:
        placeholders["AUTHORS"] = handle_authors(placeholders["AUTHORS"])

    if "DATE" in placeholders:
        placeholders["DATE"] = handle_date(entry, locale)

    if "URL" in placeholders:
        placeholders["URL"] = handle_url(entry)

    pattern = build_keyword_matcher_pattern(frozenset(placeholders.keys()))

    return {
        key: pattern.sub(lambda match: placeholders[match.group(0)], value)
        for key, value in templates.items()
    }


def handle_highlights(highlights: list[str]) -> str:
    return "- ".join([highlight.replace("\n- ", "\n  - ") for highlight in highlights])


def handle_authors(authors: list[str]) -> str:
    return ", ".join(authors)


def handle_date(entry: Entry, locale: Locale) -> str:
    date_string = compute_date_string(entry, locale)
    if date_string:
        return date_string
    return ""


def handle_url(entry: Entry) -> str:
    assert isinstance(entry, PublicationEntry)
    if entry.doi:
        return f"[{entry.doi}]({entry.doi_url})"
    if entry.url:
        return f"[{clean_url(entry.url)}]({entry.url})"
    return ""
