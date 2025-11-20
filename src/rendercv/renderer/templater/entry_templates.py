import re
from datetime import date as Date

import pydantic

from rendercv.schema.models.cv.entries.publication import PublicationEntry
from rendercv.schema.models.cv.section import Entry
from rendercv.schema.models.locale.locale import Locale

from .date import compute_date_string, compute_time_span_string
from .string_processor import clean_url, substitute_placeholders

uppercase_word_pattern = re.compile(r"\b[A-Z]+\b")


def compute_entry_templates(
    entry: Entry,
    entry_options: pydantic.BaseModel,
    locale: Locale,
    show_time_spans: bool,
    today: Date | None,
) -> dict[str, str]:
    if isinstance(entry, str):
        return {}

    templates = {
        key: value.replace("\n", "\n\n")
        for key, value in entry_options.model_dump().items()
        if key.endswith("template") and isinstance(value, str)
    }
    placeholders = {
        key.upper(): value
        for key, value in entry.model_dump().items()
        if value is not None
    }

    uppercase_words = set(uppercase_word_pattern.findall(" ".join(templates.values())))

    not_provided_placeholders = uppercase_words - set(placeholders.keys())

    # Remove the not provided placeholders from the templates, including characters
    # around them:
    not_provided_placeholders_pattern = re.compile(
        rf"\S*{'|'.join(not_provided_placeholders)}\S*"
    )
    templates = {
        key: not_provided_placeholders_pattern.sub("", value)
        for key, value in templates.items()
    }

    # Handle special placeholders:
    if "HIGHLIGHTS" in placeholders:
        placeholders["HIGHLIGHTS"] = handle_highlights(placeholders["HIGHLIGHTS"])

    if "AUTHORS" in placeholders:
        placeholders["AUTHORS"] = handle_authors(placeholders["AUTHORS"])

    if "DATE" in placeholders:
        placeholders["DATE"] = handle_date(
            getattr(entry, "date", None),
            getattr(entry, "start_date", None),
            getattr(entry, "end_date", None),
            locale,
            show_time_spans,
            today,
        )

    if "START_DATE" in placeholders:
        placeholders["START_DATE"] = handle_start_or_end_date(
            getattr(entry, "start_date", None),
            locale,
        )

    if "END_DATE" in placeholders:
        placeholders["END_DATE"] = handle_start_or_end_date(
            getattr(entry, "end_date", None),
            locale,
        )

    if "URL" in placeholders:
        placeholders["URL"] = handle_url(entry)

    if "DOI" in placeholders:
        placeholders["DOI"] = handle_doi(entry)

    return {
        key: substitute_placeholders(value, placeholders)
        for key, value in templates.items()
    }


def handle_highlights(highlights: list[str]) -> str:
    highlights = [
        "- " + highlight.replace("\n- ", "\n  - ") for highlight in highlights
    ]
    return "\n".join(highlights)


def handle_authors(authors: list[str]) -> str:
    return ", ".join(authors)


def handle_date(
    date: str | int | None,
    start_date: str | int | None,
    end_date: str | int | None,
    locale: Locale,
    show_time_spans: bool,
    today: Date | None,
) -> str:
    date_string = compute_date_string(date, start_date, end_date, locale)
    if show_time_spans:
        time_span_string = compute_time_span_string(
            date, start_date, end_date, locale, today
        )
        if time_span_string:
            return f"{date_string}\n\n{time_span_string}"
    if date_string:
        return date_string
    return ""


def handle_start_or_end_date(
    start_or_end_date: str | int | None,
    locale: Locale,
) -> str:
    date_string = compute_date_string(
        date=start_or_end_date, start_date=None, end_date=None, locale=locale
    )
    if date_string:
        return date_string
    return ""


def handle_url(entry: Entry) -> str:
    if isinstance(entry, PublicationEntry):
        return handle_doi(entry)
    if hasattr(entry, "url") and entry.url:  # pyright: ignore[reportAttributeAccessIssue]
        url = entry.url  # pyright: ignore[reportAttributeAccessIssue]
        return f"[{clean_url(url)}]({url})"
    return ""


def handle_doi(entry: Entry) -> str:
    if isinstance(entry, PublicationEntry) and entry.doi:
        return f"[{entry.doi}]({entry.doi_url})"
    return ""
