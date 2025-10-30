"""
The `rendercv.models.data.entry_types` module contains the data models of all the available
entry types in RenderCV.
"""

import functools
import re
from datetime import date as Date
from typing import Annotated

import pydantic

from . import computers
from .base import RenderCVBaseModelWithExtraKeys


def make_keywords_bold_in_a_string(string: str, keywords: list[str]) -> str:
    """Make the given keywords bold in the given string, handling capitalization and substring issues.

    Examples:
        >>> make_keywords_bold_in_a_string("I know java and javascript", ["java"])
        'I know **java** and javascript'

        >>> make_keywords_bold_in_a_string("Experience with aws, Aws and AWS", ["aws"])
        'Experience with **aws**, **Aws** and **AWS**'
    """

    def bold_match(match):
        return f"**{match.group(0)}**"

    for keyword in keywords:
        # Use re.escape to ensure special characters in keywords are handled
        pattern = r"\b" + re.escape(keyword) + r"\b"
        string = re.sub(pattern, bold_match, string, flags=re.IGNORECASE)

    return string


# ======================================================================================
# Create custom types based on the entry models: =======================================
# ======================================================================================
# Create a custom type named Entry:
Entry = (
    OneLineEntry
    | NormalEntry
    | ExperienceEntry
    | EducationEntry
    | PublicationEntry
    | BulletEntry
    | NumberedEntry
    | ReversedNumberedEntry
    | str
)

# Create a custom type named ListOfEntries:
ListOfEntries = (
    list[OneLineEntry]
    | list[NormalEntry]
    | list[ExperienceEntry]
    | list[EducationEntry]
    | list[PublicationEntry]
    | list[BulletEntry]
    | list[NumberedEntry]
    | list[ReversedNumberedEntry]
    | list[str]
)

# ======================================================================================
# Store the available entry types: =====================================================
# ======================================================================================
# Entry.__args__[:-1] is a tuple of all the entry types except `str``:
# `str` (TextEntry) is not included because it's validation handled differently. It is
# not a Pydantic model, but a string.
available_entry_models: tuple[type[Entry]] = tuple(Entry.__args__[:-1])

available_entry_type_names = tuple(
    [entry_type.__name__ for entry_type in available_entry_models] + ["TextEntry"]
)


def compute_dates_for_sorting(
    start_date: StartDate,
    end_date: EndDate,
    date: ArbitraryDate,
) -> tuple[Date | None, Date | None]:
    """Return end and start dates for sorting based on entry date fields."""

    start_date, end_date, date = validate_and_adjust_dates_for_an_entry(
        start_date=start_date, end_date=end_date, date=date
    )

    # If only ``date`` is provided, use it for both end and start dates
    if date is not None:
        try:
            date_obj = computers.get_date_object(date)
            return date_obj, date_obj
        except ValueError:
            return None, None

    end_date_obj: Date | None = None
    if end_date is not None:
        try:
            end_date_obj = computers.get_date_object(end_date)
        except ValueError:
            end_date_obj = None

    start_date_obj: Date | None = None
    if start_date is not None:
        try:
            start_date_obj = computers.get_date_object(start_date)
        except ValueError:
            start_date_obj = None

    return end_date_obj, start_date_obj


def sort_entries_by_date(entries: list[Entry], order: str) -> list[Entry]:
    """Sort the given entries based on the provided order."""

    if order not in {"reverse-chronological", "chronological"}:
        return entries

    processed: list[tuple[Entry, Date | None, Date | None]] = []
    for entry in entries:
        if isinstance(entry, str):
            processed.append((entry, None, None))
        else:
            start = getattr(entry, "start_date", None)
            end = getattr(entry, "end_date", None)
            d = getattr(entry, "date", None)
            end_obj, start_obj = compute_dates_for_sorting(
                start_date=start,
                end_date=end,
                date=d,
            )
            processed.append((entry, end_obj, start_obj))

    reverse = order == "reverse-chronological"
    default_end = Date.min if reverse else Date.max
    default_start = Date.min if reverse else Date.max

    def key(item: tuple[Entry, Date | None, Date | None]):
        _entry, end_obj, start_obj = item
        return (
            end_obj or default_end,
            start_obj or default_start,
        )

    processed.sort(key=key, reverse=reverse)

    return [item[0] for item in processed]
