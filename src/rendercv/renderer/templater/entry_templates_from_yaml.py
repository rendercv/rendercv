import re
import textwrap
from datetime import date as Date

from rendercv.exception import RenderCVInternalError
from rendercv.schema.models.cv.entries.publication import PublicationEntry
from rendercv.schema.models.cv.section import Entry
from rendercv.schema.models.design.classic_theme import Templates
from rendercv.schema.models.locale.locale import Locale

from .date import compute_time_span_string, format_date_range, format_single_date
from .string_processor import clean_url, substitute_placeholders

uppercase_word_pattern = re.compile(r"\b[A-Z_]+\b")


def render_entry_templates[EntryType: Entry](
    entry: EntryType,
    *,
    templates: Templates,
    locale: Locale,
    show_time_span: bool,
    current_date: Date,
) -> EntryType:
    if isinstance(entry, str) or not hasattr(templates, entry.entry_type_in_snake_case):
        # It's a TextEntry, or an entry type without templates. Return it as is:
        return entry

    entry_templates: dict[str, str] = getattr(
        templates, entry.entry_type_in_snake_case
    ).model_dump(exclude_none=True)

    entry_fields: dict[str, str | str] = {
        key.upper(): value for key, value in entry.model_dump(exclude_none=True).items()
    }

    # Handle special placeholders:
    if "HIGHLIGHTS" in entry_fields:
        highlights = getattr(entry, "highlights", None)
        assert highlights is not None
        entry_fields["HIGHLIGHTS"] = process_highlights(highlights)

    if "AUTHORS" in entry_fields:
        authors = getattr(entry, "authors", None)
        assert authors is not None
        entry_fields["AUTHORS"] = process_authors(authors)

    if (
        "DATE" in entry_fields
        or "START_DATE" in entry_fields
        or "END_DATE" in entry_fields
    ):
        entry_fields["DATE"] = process_date(
            date=getattr(entry, "date", None),
            start_date=getattr(entry, "start_date", None),
            end_date=getattr(entry, "end_date", None),
            locale=locale,
            show_time_span=show_time_span,
            current_date=current_date,
            single_date_template=templates.single_date,
            date_range_template=templates.date_range,
            time_span_template=templates.time_span,
        )

    if "START_DATE" in entry_fields:
        start_date = getattr(entry, "start_date", None)
        assert start_date is not None
        entry_fields["START_DATE"] = format_single_date(
            start_date,
            locale=locale,
            single_date_template=templates.single_date,
        )

    if "END_DATE" in entry_fields:
        end_date = getattr(entry, "end_date", None)
        assert end_date is not None
        entry_fields["END_DATE"] = format_single_date(
            end_date,
            locale=locale,
            single_date_template=templates.single_date,
        )

    if "URL" in entry_fields:
        entry_fields["URL"] = process_url(entry)

    if "DOI" in entry_fields:
        entry_fields["URL"] = process_url(entry)
        entry_fields["DOI"] = process_doi(entry)

    if "SUMMARY" in entry_fields:
        entry_fields["SUMMARY"] = process_summary(entry_fields["SUMMARY"])

    entry_templates = remove_not_provided_placeholders(entry_templates, entry_fields)

    for template_name, template in entry_templates.items():
        setattr(entry, template_name, template)

    for template_name, template in entry_templates.items():
        setattr(
            entry,
            template_name,
            substitute_placeholders(template, entry_fields),
        )

    return entry


def process_highlights(highlights: list[str]) -> str:
    highlights = ["- " + highlight.replace(" - ", "\n  - ") for highlight in highlights]
    return "\n".join(highlights)


def process_authors(authors: list[str]) -> str:
    return ", ".join(authors)


def process_date(
    *,
    date: str | int | None,
    start_date: str | int | None,
    end_date: str | int | None,
    locale: Locale,
    current_date: Date,
    show_time_span: bool,
    single_date_template: str,
    date_range_template: str,
    time_span_template: str,
) -> str:
    if date and not (start_date or end_date):
        return format_single_date(
            date, locale=locale, single_date_template=single_date_template
        )
    if start_date and end_date:
        date_range = format_date_range(
            start_date,
            end_date,
            locale=locale,
            single_date_template=single_date_template,
            date_range_template=date_range_template,
        )
        if show_time_span:
            time_span = compute_time_span_string(
                start_date,
                end_date,
                locale=locale,
                current_date=current_date,
                time_span_template=time_span_template,
            )
            return f"{date_range}\n\n{time_span}"

        return date_range

    raise RenderCVInternalError("Date is not provided for this entry.")


def process_url(entry: Entry) -> str:
    if isinstance(entry, PublicationEntry) and entry.doi:
        return process_doi(entry)
    if hasattr(entry, "url") and entry.url:  # pyright: ignore[reportAttributeAccessIssue]
        url = entry.url  # pyright: ignore[reportAttributeAccessIssue]
        return f"[{clean_url(url)}]({url})"
    raise RenderCVInternalError("URL is not provided for this entry.")


def process_doi(entry: Entry) -> str:
    if isinstance(entry, PublicationEntry) and entry.doi:
        return f"[{entry.doi}]({entry.doi_url})"
    raise RenderCVInternalError("DOI is not provided for this entry.")


def process_summary(summary: str) -> str:
    return f"!!! note\n{textwrap.indent(summary, '    ')}"


def remove_not_provided_placeholders(
    entry_templates: dict[str, str], entry_fields: dict[str, str]
) -> dict[str, str]:
    # Remove the not provided placeholders from the templates, including characters
    # around them:
    used_placeholders_in_templates = set(
        uppercase_word_pattern.findall(" ".join(entry_templates.values()))
    )
    not_provided_placeholders = used_placeholders_in_templates - set(
        entry_fields.keys()
    )
    if not_provided_placeholders:
        not_provided_placeholders_pattern = re.compile(
            r"\S*(?:" + "|".join(not_provided_placeholders) + r")\S*"
        )
        entry_templates = {
            key: clean_trailing_parts(not_provided_placeholders_pattern.sub("", value))
            for key, value in entry_templates.items()
        }

    return entry_templates


unwanted_trailing_parts_pattern = re.compile(r"[^A-Za-z0-9.!?\[\]\(\)\*_%]+$")


def clean_trailing_parts(text: str) -> str:
    new_lines = []
    for line in text.splitlines():
        new_line = line.rstrip()
        if new_line == "":
            continue
        new_lines.append(unwanted_trailing_parts_pattern.sub("", new_line).rstrip())
    return "\n".join(new_lines)
