import re
from datetime import date as Date

import pydantic

from rendercv.exception import RenderCVInternalError
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
    current_date: Date,
) -> dict[str, str]:
    if isinstance(entry, str):
        return {}

    templates = {
        key: value
        for key, value in entry_options.model_dump().items()
        if key.endswith("template") and isinstance(value, str)
    }
    placeholders = {
        key.upper(): value
        for key, value in entry.model_dump().items()
        if value is not None
    }

    # Handle special placeholders:
    if "HIGHLIGHTS" in placeholders:
        placeholders["HIGHLIGHTS"] = handle_highlights(placeholders["HIGHLIGHTS"])

    if "AUTHORS" in placeholders:
        placeholders["AUTHORS"] = handle_authors(placeholders["AUTHORS"])

    if (
        "DATE" in placeholders
        or "START_DATE" in placeholders
        or "END_DATE" in placeholders
    ):
        placeholders["DATE"] = handle_date(
            getattr(entry, "date", None),
            getattr(entry, "start_date", None),
            getattr(entry, "end_date", None),
            locale,
            show_time_spans,
            current_date,
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
        placeholders["URL"] = handle_url(entry)
        placeholders["DOI"] = handle_doi(entry)

    if "SUMMARY" in placeholders:
        placeholders["SUMMARY"] = handle_summary(placeholders["SUMMARY"])

    used_placeholders_in_templates = set(
        uppercase_word_pattern.findall(" ".join(templates.values()))
    )

    not_provided_placeholders = used_placeholders_in_templates - set(
        placeholders.keys()
    )

    # Remove the not provided placeholders from the templates, including characters
    # around them:
    if not_provided_placeholders:
        not_provided_placeholders_pattern = re.compile(
            r"\S*(?:" + "|".join(not_provided_placeholders) + r")\S*"
        )
        templates = {
            key: not_provided_placeholders_pattern.sub("", value)
            for key, value in templates.items()
        }

    return {
        key: clean_trailing_parts(substitute_placeholders(value, placeholders))
        for key, value in templates.items()
    }


unwanted_trailing_parts_pattern = re.compile(r"[^A-Za-z0-9.!?\[\]\(\)\*_]+$")


def clean_trailing_parts(text: str) -> str:
    new_lines = []
    for line in text.splitlines():
        new_line = line.rstrip()
        if new_line == "":
            continue
        new_lines.append(unwanted_trailing_parts_pattern.sub("", new_line).rstrip())
    return "\n".join(new_lines)


def handle_highlights(highlights: list[str]) -> str:
    highlights = ["- " + highlight.replace(" - ", "\n  - ") for highlight in highlights]
    return "\n".join(highlights)


def handle_authors(authors: list[str]) -> str:
    return ", ".join(authors)


def handle_date(
    date: str | int | None,
    start_date: str | int | None,
    end_date: str | int | None,
    locale: Locale,
    show_time_spans: bool,
    current_date: Date,
) -> str:
    date_string = compute_date_string(date, start_date, end_date, locale)
    if show_time_spans:
        time_span_string = compute_time_span_string(
            date, start_date, end_date, locale, current_date
        )
        if time_span_string:
            return f"{date_string}\n\n{time_span_string}"
    if date_string:
        return date_string
    raise RenderCVInternalError("Date is not provided for this entry.")


def handle_start_or_end_date(
    start_or_end_date: str | int | None,
    locale: Locale,
) -> str:
    date_string = compute_date_string(
        date=start_or_end_date, start_date=None, end_date=None, locale=locale
    )
    if date_string:
        return date_string
    raise RenderCVInternalError("Date is not provided for this entry.")


def handle_url(entry: Entry) -> str:
    if isinstance(entry, PublicationEntry):
        return handle_doi(entry)
    if hasattr(entry, "url") and entry.url:  # pyright: ignore[reportAttributeAccessIssue]
        url = entry.url  # pyright: ignore[reportAttributeAccessIssue]
        return f"[{clean_url(url)}]({url})"
    raise RenderCVInternalError("URL is not provided for this entry.")


def handle_doi(entry: Entry) -> str:
    if isinstance(entry, PublicationEntry) and entry.doi:
        return f"[{entry.doi}]({entry.doi_url})"
    raise RenderCVInternalError("DOI is not provided for this entry.")


def handle_summary(summary: str) -> str:
    return f"#summary[{summary}]"
