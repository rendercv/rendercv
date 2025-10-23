"""
The `rendercv.models.data.entry_types` module contains the data models of all the available
entry types in RenderCV.
"""

import abc
import functools
import re
from datetime import date as Date
from typing import Annotated, Literal

import pydantic

from . import computers
from .base import RenderCVBaseModelWithExtraKeys

# ======================================================================================
# Create validator functions: ==========================================================
# ======================================================================================


def validate_date_field(date: int | str | None) -> int | str | None:
    """Check if the `date` field is provided correctly.

    Args:
        date: The date to validate.

    Returns:
        The validated date.
    """
    date_is_provided = date is not None

    if date_is_provided:
        if isinstance(date, str):
            if re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", date):
                # Then it is in YYYY-MM-DD or YYYY-MMY format
                # Check if it is a valid date:
                computers.get_date_object(date)
            elif re.fullmatch(r"\d{4}", date):
                # Then it is in YYYY format, so, convert it to an integer:

                # This is not required for start_date and end_date because they
                # can't be casted into a general string. For date, this needs to
                # be done manually, because it can be a general string.
                date = int(date)

        elif isinstance(date, Date):
            # Pydantic parses YYYY-MM-DD dates as datetime.date objects. We need to
            # convert them to strings because that is how RenderCV uses them.
            date = date.isoformat()

    return date


def validate_start_and_end_date_fields(
    date: str | Date,
) -> str:
    """Check if the `start_date` and `end_date` fields are provided correctly.

    Args:
        date: The date to validate.

    Returns:
        The validated date.
    """
    date_is_provided = date is not None

    if date_is_provided:
        if isinstance(date, Date):
            # Pydantic parses YYYY-MM-DD dates as datetime.date objects. We need to
            # convert them to strings because that is how RenderCV uses them.
            date = date.isoformat()

        elif date != "present":
            # Validate the date:
            computers.get_date_object(date)

    return date


# See https://peps.python.org/pep-0484/#forward-references for more information about
# the quotes around the type hints.
def validate_and_adjust_dates_for_an_entry(
    start_date: "StartDate",
    end_date: "EndDate",
    date: "ArbitraryDate",
) -> tuple["StartDate", "EndDate", "ArbitraryDate"]:
    """Check if the dates are provided correctly and make the necessary adjustments.

    Args:
        start_date: The start date of the event.
        end_date: The end date of the event.
        date: The date of the event.

    Returns:
        The validated and adjusted `start_date`, `end_date`, and `date`.
    """
    date_is_provided = date is not None
    start_date_is_provided = start_date is not None
    end_date_is_provided = end_date is not None

    if date_is_provided:
        # If only date is provided, ignore start_date and end_date:
        start_date = None
        end_date = None
    elif not start_date_is_provided and end_date_is_provided:
        # If only end_date is provided, assume it is a one-day event and act like
        # only the date is provided:
        date = end_date
        start_date = None
        end_date = None
    elif start_date_is_provided:
        start_date_object = computers.get_date_object(start_date)
        if not end_date_is_provided:
            # If only start_date is provided, assume it is an ongoing event, i.e.,
            # the end_date is present:
            end_date = "present"

        if end_date != "present":
            end_date_object = computers.get_date_object(end_date)

            if start_date_object > end_date_object:
                message = '"start_date" can not be after "end_date"!'

                raise ValueError(
                    message,
                    "start_date",  # This is the location of the error
                    str(start_date),  # This is value of the error
                )

    return start_date, end_date, date


# ======================================================================================
# Create custom types: =================================================================
# ======================================================================================


# See https://docs.pydantic.dev/2.7/concepts/types/#custom-types and
# https://docs.pydantic.dev/2.7/concepts/validators/#annotated-validators
# for more information about custom types.

# ExactDate that accepts only strings in YYYY-MM-DD or YYYY-MM format:
ExactDate = Annotated[
    str,
    pydantic.Field(
        pattern=r"\d{4}-\d{2}(-\d{2})?",
    ),
]

# ArbitraryDate that accepts either an integer or a string, but it is validated with
# `validate_date_field` function:
ArbitraryDate = Annotated[
    int | str | None,
    pydantic.BeforeValidator(validate_date_field),
]

# StartDate that accepts either an integer or an ExactDate, but it is validated with
# `validate_start_and_end_date_fields` function:
StartDate = Annotated[
    int | ExactDate | None,
    pydantic.BeforeValidator(validate_start_and_end_date_fields),
]

# EndDate that accepts either an integer, the string "present", or an ExactDate, but it
# is validated with `validate_start_and_end_date_fields` function:
EndDate = Annotated[
    Literal["present"] | int | ExactDate | None,
    pydantic.BeforeValidator(validate_start_and_end_date_fields),
]

# ======================================================================================
# Create the entry models: =============================================================
# ======================================================================================


class EntryType(abc.ABC):
    """This class is an abstract class that defines all the methods an entry type should
    have."""

    @abc.abstractmethod
    def make_keywords_bold(self, keywords: list[str]) -> "EntryType": ...


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


class OneLineEntry(RenderCVBaseModelWithExtraKeys, EntryType):
    """This class is the data model of `OneLineEntry`."""

    model_config = pydantic.ConfigDict(title="One Line Entry")
    label: str = pydantic.Field(
        title="Label",
    )
    details: str = pydantic.Field(
        title="Details",
    )

    def make_keywords_bold(self, keywords: list[str]) -> "OneLineEntry":
        """Make the given keywords bold in the `details` field.

        Args:
            keywords: The keywords to make bold.

        Returns:
            A OneLineEntry with the keywords made bold in the `details` field.
        """
        self.details = make_keywords_bold_in_a_string(self.details, keywords)
        return self


class BulletEntry(RenderCVBaseModelWithExtraKeys, EntryType):
    """This class is the data model of `BulletEntry`."""

    model_config = pydantic.ConfigDict(title="Bullet Entry")
    bullet: str = pydantic.Field(
        title="Bullet",
    )

    def make_keywords_bold(self, keywords: list[str]) -> "BulletEntry":
        """Make the given keywords bold in the `bullet` field.

        Args:
            keywords: The keywords to make bold.

        Returns:
            A BulletEntry with the keywords made bold in the `bullet` field.
        """
        self.bullet = make_keywords_bold_in_a_string(self.bullet, keywords)
        return self


class NumberedEntry(RenderCVBaseModelWithExtraKeys, EntryType):
    """This class is the data model of `NumberedEntry`."""

    model_config = pydantic.ConfigDict(title="Numbered Entry")

    number: str = pydantic.Field(
        title="Number",
    )

    def make_keywords_bold(self, keywords: list[str]) -> "NumberedEntry":
        """Make the given keywords bold in the `number` field.

        Args:
            keywords: The keywords to make bold.

        Returns:
            A NumberedEntry with the keywords made bold in the `number` field.
        """
        self.number = make_keywords_bold_in_a_string(str(self.number), keywords)
        return self


class ReversedNumberedEntry(RenderCVBaseModelWithExtraKeys, EntryType):
    """This class is the data model of `ReversedNumberedEntry`."""

    model_config = pydantic.ConfigDict(title="Reversed Numbered Entry")
    reversed_number: str = pydantic.Field(
        title="Reversed Number",
    )

    def make_keywords_bold(self, keywords: list[str]) -> "ReversedNumberedEntry":
        """Make the given keywords bold in the `reversed_number` field.

        Args:
            keywords: The keywords to make bold.

        Returns:
            A ReversedNumberedEntry with the keywords made bold in the `reversed_number` field.
        """
        self.reversed_number = make_keywords_bold_in_a_string(
            str(self.reversed_number), keywords
        )
        return self


class EntryWithDate(RenderCVBaseModelWithExtraKeys):
    """This class is the parent class of some of the entry types that have date
    fields.
    """

    date: ArbitraryDate = pydantic.Field(
        default=None,
        title="Date",
        description=(
            "The date can be written in the formats YYYY-MM-DD, YYYY-MM, or YYYY, or as"
            ' an arbitrary string such as "Fall 2023."'
        ),
        examples=["2020-09-24", "Fall 2023"],
    )

    @functools.cached_property
    def date_string(self) -> str:
        """Return a date string based on the `date` field and cache `date_string` as
        an attribute of the instance.
        """
        return computers.compute_date_string(
            start_date=None, end_date=None, date=self.date
        )


class PublicationEntryBase(RenderCVBaseModelWithExtraKeys):
    """This class is the parent class of the `PublicationEntry` class."""

    title: str = pydantic.Field(
        title="Publication Title",
    )
    authors: list[str] = pydantic.Field(
        title="Authors",
    )
    doi: Annotated[str, pydantic.Field(pattern=r"\b10\..*")] | None = pydantic.Field(
        default=None,
        title="DOI",
        examples=["10.48550/arXiv.2310.03138"],
    )
    url: pydantic.HttpUrl | None = pydantic.Field(
        default=None,
        title="URL",
        description="If DOI is provided, it will be ignored.",
    )
    journal: str | None = pydantic.Field(
        default=None,
        title="Journal",
    )

    @pydantic.model_validator(mode="after")  # type: ignore
    def ignore_url_if_doi_is_given(self) -> "PublicationEntryBase":
        """Check if DOI is provided and ignore the URL if it is provided."""
        doi_is_provided = self.doi is not None

        if doi_is_provided:
            self.url = None

        return self

    @functools.cached_property
    def doi_url(self) -> str:
        """Return the URL of the DOI and cache `doi_url` as an attribute of the
        instance.
        """
        doi_is_provided = self.doi is not None

        if doi_is_provided:
            return f"https://doi.org/{self.doi}"
        return ""

    @functools.cached_property
    def clean_url(self) -> str:
        """Return the clean URL of the publication and cache `clean_url` as an attribute
        of the instance.
        """
        url_is_provided = self.url is not None

        if url_is_provided:
            return computers.make_a_url_clean(str(self.url))  # type: ignore
        return ""

    def make_keywords_bold(
        self,
        keywords: list[str],  # NOQA: ARG002
    ) -> "PublicationEntryBase":
        return self


# The following class is to ensure PublicationEntryBase keys come first,
# then the keys of the EntryWithDate class. The only way to achieve this in Pydantic is
# to do this. The same thing is done for the other classes as well.
class PublicationEntry(EntryWithDate, PublicationEntryBase, EntryType):
    """This class is the data model of `PublicationEntry`. `PublicationEntry` class is
    created by combining the `EntryWithDate` and `PublicationEntryBase` classes to have
    the fields in the correct order.
    """

    model_config = pydantic.ConfigDict(title="Publication Entry")


class EntryBase(EntryWithDate):
    """This class is the parent class of some of the entry types. It is being used
    because some of the entry types have common fields like dates, highlights, location,
    etc.
    """

    start_date: StartDate = pydantic.Field(
        default=None,
        title="Start Date",
        description=(
            "The event's start date, written in YYYY-MM-DD, YYYY-MM, or YYYY format."
        ),
        examples=["2020-09-24"],
    )
    end_date: EndDate = pydantic.Field(
        default=None,
        title="End Date",
        description=(
            "The event's end date, written in YYYY-MM-DD, YYYY-MM, or YYYY format. If"
            " the event is ongoing, type “present” or provide only the start date."
        ),
        examples=["2020-09-24", "present"],
    )
    location: str | None = pydantic.Field(
        default=None,
        title="Location",
        examples=["Istanbul, Türkiye"],
    )
    summary: str | None = pydantic.Field(
        default=None,
        title="Summary",
        examples=["Did this and that."],
    )
    highlights: list[str] | None = pydantic.Field(
        default=None,
        title="Highlights",
        examples=["Did this.", "Did that."],
    )

    @pydantic.field_validator("highlights", mode="after")
    @classmethod
    def handle_nested_bullets_in_highlights(
        cls, highlights: list[str] | None
    ) -> list[str] | None:
        """Handle nested bullets in the `highlights` field."""
        if highlights:
            return [highlight.replace(" - ", "\n    - ") for highlight in highlights]

        return highlights

    @pydantic.model_validator(mode="after")  # type: ignore
    def check_and_adjust_dates(self) -> "EntryBase":
        """Call the `validate_adjust_dates_of_an_entry` function to validate the
        dates.
        """
        self.start_date, self.end_date, self.date = (
            validate_and_adjust_dates_for_an_entry(
                start_date=self.start_date, end_date=self.end_date, date=self.date
            )
        )
        return self

    @functools.cached_property
    def date_string(self) -> str:
        """Return a date string based on the `date`, `start_date`, and `end_date` fields
        and cache `date_string` as an attribute of the instance.

        Example:
            ```python
            entry = dm.EntryBase(
                start_date="2020-10-11", end_date="2021-04-04"
            ).date_string
            ```
            returns
            `"Nov 2020 to Apr 2021"`
        """
        return computers.compute_date_string(
            start_date=self.start_date, end_date=self.end_date, date=self.date
        )

    @functools.cached_property
    def date_string_only_years(self) -> str:
        """Return a date string that only contains years based on the `date`,
        `start_date`, and `end_date` fields and cache `date_string_only_years` as an
        attribute of the instance.

        Example:
            ```python
            entry = dm.EntryBase(
                start_date="2020-10-11", end_date="2021-04-04"
            ).date_string_only_years
            ```
            returns
            `"2020 to 2021"`
        """
        return computers.compute_date_string(
            start_date=self.start_date,
            end_date=self.end_date,
            date=self.date,
            show_only_years=True,
        )

    @functools.cached_property
    def time_span_string(self) -> str:
        """Return a time span string based on the `date`, `start_date`, and `end_date`
        fields and cache `time_span_string` as an attribute of the instance.
        """
        return computers.compute_time_span_string(
            start_date=self.start_date, end_date=self.end_date, date=self.date
        )

    def make_keywords_bold(self, keywords: list[str]) -> "EntryBase":
        """Make the given keywords bold in the `summary` and `highlights` fields.

        Args:
            keywords: The keywords to make bold.

        Returns:
            An EntryBase with the keywords made bold in the `summary` and `highlights`
            fields.
        """
        if self.summary:
            self.summary = make_keywords_bold_in_a_string(self.summary, keywords)

        if self.highlights:
            self.highlights = [
                make_keywords_bold_in_a_string(highlight, keywords)
                for highlight in self.highlights
            ]

        return self


class NormalEntryBase(RenderCVBaseModelWithExtraKeys):
    """This class is the parent class of the `NormalEntry` class."""

    name: str = pydantic.Field(
        title="Name",
    )


class NormalEntry(EntryBase, NormalEntryBase, EntryType):
    """This class is the data model of `NormalEntry`. `NormalEntry` class is created by
    combining the `EntryBase` and `NormalEntryBase` classes to have the fields in the
    correct order.
    """

    model_config = pydantic.ConfigDict(title="Normal Entry")


class ExperienceEntryBase(RenderCVBaseModelWithExtraKeys):
    """This class is the parent class of the `ExperienceEntry` class."""

    company: str = pydantic.Field(
        title="Company",
    )
    position: str = pydantic.Field(
        title="Position",
    )


class ExperienceEntry(EntryBase, ExperienceEntryBase, EntryType):
    """This class is the data model of `ExperienceEntry`. `ExperienceEntry` class is
    created by combining the `EntryBase` and `ExperienceEntryBase` classes to have the
    fields in the correct order.
    """

    model_config = pydantic.ConfigDict(title="Experience Entry")


class EducationEntryBase(RenderCVBaseModelWithExtraKeys):
    """This class is the parent class of the `EducationEntry` class."""

    institution: str = pydantic.Field(
        title="Institution",
    )
    area: str = pydantic.Field(
        title="Area",
    )
    degree: str | None = pydantic.Field(
        default=None,
        title="Degree",
        description="The type of the degree, such as BS, BA, PhD, MS.",
        examples=["BS", "BA", "PhD", "MS"],
    )
    grade: str | None = pydantic.Field(
        default=None,
        title="Grade",
        examples=["GPA: 3.00/4.00"],
    )


class EducationEntry(EntryBase, EducationEntryBase, EntryType):
    """This class is the data model of `EducationEntry`. `EducationEntry` class is
    created by combining the `EntryBase` and `EducationEntryBase` classes to have the
    fields in the correct order.
    """

    model_config = pydantic.ConfigDict(title="Education Entry")


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
