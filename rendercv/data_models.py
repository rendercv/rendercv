"""
This module contains the necessary classes to store CV data. These classes are named
data models. The YAML input file is transformed into instances of these classes (i.e.,
the input file is read) with the
[`read_input_file`][rendercv.data_models.read_input_file] function. RenderCV utilizes
these instances to generate a $\\LaTeX$ file which is then rendered into a PDF file.

The data models are initialized with data validation to prevent unexpected bugs. During
initialization, we ensure that everything is in the correct place and that the user
has provided a valid RenderCV input. This is achieved using
[Pydantic](https://pypi.org/project/pydantic/). Each class method decorated with
`pydantic.model_validator` or `pydantic.field_validator` is executed automatically
during data class initialization.
"""

from datetime import date as Date
from typing import Literal, Any, Type, Annotated, Optional, get_args
import importlib
import importlib.util
import importlib.machinery
import functools
from urllib.request import urlopen, HTTPError
from urllib.error import URLError
from http.client import InvalidURL
import json
import re
import ssl
import pathlib
import warnings
import annotated_types as at
import io

import pydantic
import pydantic_extra_types.phone_numbers as pydantic_phone_numbers
import ruamel.yaml

from .themes.classic import ClassicThemeOptions
from .themes.moderncv import ModerncvThemeOptions
from .themes.sb2nov import Sb2novThemeOptions
from .themes.engineeringresumes import EngineeringresumesThemeOptions

# Disable Pydantic warnings:
warnings.filterwarnings("ignore")

locale_catalog = {
    "month": "month",
    "months": "months",
    "year": "year",
    "years": "years",
    "present": "present",
    "to": "to",
    "abbreviations_for_months": [
        "Jan",
        "Feb",
        "Mar.",
        "Apr",
        "May",
        "June",
        "July",
        "Aug",
        "Sept",
        "Oct",
        "Nov",
        "Dec",
    ],
}


def get_date_object(date: str | int) -> Date:
    """
    Parse a date string in YYYY-MM-DD, YYYY-MM, or YYYY format and return a
    `datetime.date` object. This function is used throughout the validation process of
    the data models.

    Args:
        date (str | int): The date string to parse.
    Returns:
        Date (datetime.date): The parsed date.
    """
    if isinstance(date, int):
        date_object = Date.fromisoformat(f"{date}-01-01")
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        # Then it is in YYYY-MM-DD format
        date_object = Date.fromisoformat(date)
    elif re.fullmatch(r"\d{4}-\d{2}", date):
        # Then it is in YYYY-MM format
        date_object = Date.fromisoformat(f"{date}-01")
    elif re.fullmatch(r"\d{4}", date):
        # Then it is in YYYY format
        date_object = Date.fromisoformat(f"{date}-01-01")
    elif date == "present":
        date_object = Date.today()
    else:
        raise ValueError(
            "This is not a valid date! Please use either YYYY-MM-DD, YYYY-MM, or"
            " YYYY format."
        )

    return date_object


def format_date(date: Date) -> str:
    """
    Format a `Date` object to a string in the following format: "Jan 2021".

    It uses month abbreviations taken from
    [Yale University Library](https://web.library.yale.edu/cataloging/months).

    Example:
        ```python
        format_date(Date(2024, 5, 1))
        ```
        will return

        `#!python "May 2024"`

    Args:
        date (Date): The date to format.

    Returns:
        str: The formatted date.
    """
    # Month abbreviations,
    # taken from: https://web.library.yale.edu/cataloging/months
    abbreviations_of_months = locale_catalog["abbreviations_for_months"]

    month = int(date.strftime("%m"))
    month_abbreviation = abbreviations_of_months[month - 1]
    year = date.strftime(format="%Y")
    date_string = f"{month_abbreviation} {year}"

    return date_string


class RenderCVBaseModel(pydantic.BaseModel):
    """
    This class is the parent class for all the data models in RenderCV. It has only
    one difference from the default `pydantic.BaseModel`: It raises an error if an
    unknown key is provided in the input file.
    """

    model_config = pydantic.ConfigDict(extra="forbid")


# ======================================================================================
# Entry models: ========================================================================
# ======================================================================================

# Create a URL validator to validate social network URLs
url_validator = pydantic.TypeAdapter(pydantic.HttpUrl)  # type: ignore

# Create a custom type called RenderCVDate that accepts only strings in YYYY-MM-DD or
# YYYY-MM format:
# This type is used to validate the date fields in the data.
# See https://docs.pydantic.dev/2.5/concepts/types/#custom-types for more information
# about custom types.
date_pattern_for_validation = r"\d{4}-\d{2}(-\d{2})?"
RenderCVDate = Annotated[
    str,
    pydantic.Field(
        pattern=date_pattern_for_validation,
    ),
]


class OneLineEntry(RenderCVBaseModel):
    """This class is the data model of `OneLineEntry`."""

    label: str = pydantic.Field(
        title="Name",
        description="The label of the OneLineEntry.",
    )
    details: str = pydantic.Field(
        title="Details",
        description="The details of the OneLineEntry.",
    )


class BulletEntry(RenderCVBaseModel):
    """This class is the data model of `BulletEntry`."""

    bullet: str = pydantic.Field(
        title="Bullet",
        description="The bullet of the BulletEntry.",
    )


class EntryWithDate(RenderCVBaseModel):
    date: Optional[int | str] = pydantic.Field(
        default=None,
        title="Date",
        description=(
            "The date field can be filled in YYYY-MM-DD, YYYY-MM, or YYYY formats or as"
            ' an arbitrary string like "Fall 2023".'
        ),
        examples=["2020-09-24", "Fall 2023"],
    )

    @pydantic.field_validator("date", mode="before")
    @classmethod
    def check_date(
        cls, date: Optional[int | RenderCVDate | str]
    ) -> Optional[int | RenderCVDate | str]:
        """Check if date is provided correctly."""
        date_is_provided = date is not None

        if date_is_provided:
            if isinstance(date, str):
                date_pattern = r"\d{4}(-\d{2})?(-\d{2})?"
                if re.fullmatch(date_pattern, date):
                    # Then it is in YYYY-MM-DD, YYYY-MM, or YYYY format
                    # Check if it is a valid date:
                    get_date_object(date)

                    # Check if it is in YYYY format, and if so, convert it to an
                    # integer:
                    if re.fullmatch(r"\d{4}", date):
                        # This is not required for start_date and end_date because they
                        # can't be casted into a general string. For date, this needs to
                        # be done manually, because it can be a general string.
                        date = int(date)
            elif isinstance(date, Date):
                # Pydantic parses YYYY-MM-DD dates as datetime.date objects. We need to
                # convert them to strings because that is how RenderCV uses them.
                date = date.isoformat()

        return date

    @functools.cached_property
    def date_string(self) -> str:
        if self.date:
            if isinstance(self.date, int):
                # Then it means only the year is provided
                date_string = str(self.date)
            else:
                try:
                    date_object = get_date_object(self.date)
                    date_string = format_date(date_object)
                except ValueError:
                    # Then it is a custom date string (e.g., "My Custom Date")
                    date_string = str(self.date)
        else:
            date_string = ""

        return date_string


class PublicationEntryBase(RenderCVBaseModel):
    title: str = pydantic.Field(
        title="Publication Title",
        description="The title of the publication.",
    )
    authors: list[str] = pydantic.Field(
        title="Authors",
        description="The authors of the publication in order as a list of strings.",
    )
    doi: Optional[str] = pydantic.Field(
        default=None,
        title="DOI",
        description="The DOI of the publication.",
        examples=["10.48550/arXiv.2310.03138"],
    )
    journal: Optional[str] = pydantic.Field(
        default=None,
        title="Journal",
        description="The journal or conference name.",
    )

    @pydantic.field_validator("doi")
    @classmethod
    def check_doi(cls, doi: Optional[str]) -> Optional[str]:
        """Check if DOI exists in the DOI system."""
        if doi is not None:
            # See https://stackoverflow.com/a/60671292/18840665 for explanation of
            # next line:
            ssl._create_default_https_context = ssl._create_unverified_context  # type: ignore

            doi_url = f"http://doi.org/{doi}"

            # Validate URL:
            url_validator.validate_strings(doi_url)

            try:
                urlopen(doi_url)
            except HTTPError as err:
                if err.code == 404:
                    raise ValueError("DOI cannot be found in the DOI System!")
            except InvalidURL:
                # Unfortunately, url_validator does not catch all the invalid URLs
                raise ValueError("This DOI is invalid!")
            except URLError:
                # In this case, there is no internet connection, so don't raise an
                # error
                pass

        return doi

    @functools.cached_property
    def doi_url(self) -> str:
        """Return the URL of the DOI."""
        return f"https://doi.org/{self.doi}"


class PublicationEntry(EntryWithDate, PublicationEntryBase):
    """This class is the data model of `PublicationEntry`."""
    pass


class EntryBase(EntryWithDate):
    """
    This class is the parent class of some of the entry types. It is used
    because some entry types have common fields like dates, highlights, location, etc.
    """

    location: Optional[str] = pydantic.Field(
        default=None,
        title="Location",
        description="The location of the event.",
        examples=["Istanbul, Türkiye"],
    )
    start_date: Optional[int | RenderCVDate] = pydantic.Field(
        default=None,
        title="Start Date",
        description=(
            "The start date of the event in YYYY-MM-DD, YYYY-MM, or YYYY format."
        ),
        examples=["2020-09-24"],
    )
    end_date: Optional[Literal["present"] | int | RenderCVDate] = pydantic.Field(
        default=None,
        title="End Date",
        description=(
            "The end date of the event in YYYY-MM-DD, YYYY-MM, or YYYY format. If the"
            ' event is still ongoing, then type "present" or provide only the'
            " start_date."
        ),
        examples=["2020-09-24", "present"],
    )
    highlights: Optional[list[str]] = pydantic.Field(
        default=None,
        title="Highlights",
        description="The highlights of the event as a list of strings.",
        examples=["Did this.", "Did that."],
    )

    @pydantic.field_validator("start_date", "end_date", mode="before")
    @classmethod
    def check_and_parse_dates(
        cls,
        date: Optional[Literal["present"] | int | RenderCVDate],
    ) -> Optional[Literal["present"] | int | RenderCVDate]:
        date_is_provided = date is not None

        if date_is_provided:
            if isinstance(date, Date):
                # Pydantic parses YYYY-MM-DD dates as datetime.date objects. We need to
                # convert them to strings because that is how RenderCV uses them.
                date = date.isoformat()

            elif date != "present":
                # Validate date:
                get_date_object(date)

        return date

    @pydantic.model_validator(
        mode="after",
    )
    def check_and_adjust_dates(self) -> "EntryBase":
        """
        Check if dates are provided correctly and make the necessary adjustments.
        """
        date_is_provided = self.date is not None
        start_date_is_provided = self.start_date is not None
        end_date_is_provided = self.end_date is not None

        if date_is_provided:
            # If only date is provided, ignore start_date and end_date:
            self.start_date = None
            self.end_date = None
        elif not start_date_is_provided and end_date_is_provided:
            # If only end_date is provided, assume it is a one-day event and act like
            # only the date is provided:
            self.date = self.end_date
            self.start_date = None
            self.end_date = None
        elif start_date_is_provided:
            start_date = get_date_object(self.start_date)
            if not end_date_is_provided:
                # If only start_date is provided, assume it is an ongoing event, i.e.,
                # the end_date is present:
                self.end_date = "present"
                end_date = Date.today()
            else:
                end_date = get_date_object(self.end_date)

            if start_date > end_date:
                raise ValueError(
                    '"start_date" can not be after "end_date"!',
                    "start_date",  # This is the location of the error
                    str(start_date),  # This is value of the error
                )

        return self

    @functools.cached_property
    def date_string(self) -> str:
        """
        Return a date string based on the `date`, `start_date`, and `end_date` fields.

        Example:
            ```python
            entry = dm.EntryBase(start_date="2020-10-11", end_date="2021-04-04").date_string
            ```
            will return:
            `#!python "Nov. 2020 to Apr. 2021"`
        """
        date_is_provided = self.date is not None
        start_date_is_provided = self.start_date is not None
        end_date_is_provided = self.end_date is not None

        if date_is_provided:
            date_string = super().date_string

        elif start_date_is_provided and end_date_is_provided:
            if isinstance(self.start_date, int):
                # Then it means only the year is provided
                start_date = str(self.start_date)
            else:
                # Then it means start_date is either in YYYY-MM-DD or YYYY-MM format
                date_object = get_date_object(self.start_date)
                start_date = format_date(date_object)

            if self.end_date == "present":
                end_date = locale_catalog["present"]
            elif isinstance(self.end_date, int):
                # Then it means only the year is provided
                end_date = str(self.end_date)
            else:
                # Then it means end_date is either in YYYY-MM-DD or YYYY-MM format
                date_object = get_date_object(self.end_date)
                end_date = format_date(date_object)

            date_string = f"{start_date} {locale_catalog['to']} {end_date}"

        else:
            # Neither date, start_date, nor end_date are provided, so return an empty
            # string:
            date_string = ""

        return date_string

    @functools.cached_property
    def date_string_only_years(self) -> str:
        """
        Return a date string that only contains years based on the `date`, `start_date`,
        and `end_date` fields.

        Example:
            ```python
            entry = dm.EntryBase(start_date="2020-10-11", end_date="2021-04-04").date_string
            ```
            will return:
            `#!python "2020 to 2021"`
        """
        date_is_provided = self.date is not None
        start_date_is_provided = self.start_date is not None
        end_date_is_provided = self.end_date is not None

        if date_is_provided:
            try:
                date_object = get_date_object(self.date)
                date_string = str(date_object.year)
            except ValueError:
                # Then it is a custom date string (e.g., "My Custom Date")
                date_string = str(self.date)

        elif start_date_is_provided and end_date_is_provided:
            if isinstance(self.start_date, int):
                # Then it means only the year is provided
                start_date = str(self.start_date)
            else:
                # Then it means start_date is either in YYYY-MM-DD or YYYY-MM format
                date_object = get_date_object(self.start_date)
                start_date = date_object.year

            if self.end_date == "present":
                end_date = "present"
            elif isinstance(self.end_date, int):
                # Then it means only the year is provided
                end_date = str(self.end_date)
            else:
                # Then it means end_date is either in YYYY-MM-DD or YYYY-MM format
                date_object = get_date_object(self.end_date)
                end_date = date_object.year

            date_string = f"{start_date} {locale_catalog['to']} {end_date}"

        else:
            # Neither date/start_date/end_date are provided, so return an empty string
            date_string = ""

        return date_string

    @functools.cached_property
    def time_span_string(self) -> str:
        """
        Return a time span based on the `date`, `start_date`, and `end_date` fields.

        Example:
            ```python
            entry = dm.EntryBase(start_date="2020-01-01", end_date="2020-04-20").time_span
            ```
            will return:
            `#!python "4 months"`
        """
        date_is_provided = self.date is not None
        start_date_is_provided = self.start_date is not None
        end_date_is_provided = self.end_date is not None

        if date_is_provided:
            # If only the date is provided, the time span is irrelevant. So, return an
            # empty string.
            return ""

        elif not start_date_is_provided and not end_date_is_provided:
            # If neither start_date nor end_date is provided, return an empty string
            return ""

        elif isinstance(self.start_date, int) or isinstance(self.end_date, int):
            # Then it means one of the dates is year, so time span cannot be more
            # specific than years
            start_year = get_date_object(self.start_date).year  # type: ignore
            end_year = get_date_object(self.end_date).year  # type: ignore

            time_span_in_years = end_year - start_year

            if time_span_in_years < 2:
                time_span_string = "1 year"
            else:
                time_span_string = f"{time_span_in_years} years"

            return time_span_string

        else:
            # Then it means both start_date and end_date are in YYYY-MM-DD or YYYY-MM
            # format
            end_date = get_date_object(self.end_date)  # type: ignore
            start_date = get_date_object(self.start_date)  # type: ignore

            # Calculate number of days between start_date and end_date
            timespan_in_days = (end_date - start_date).days  # type: ignore

            # Calculate number of years between start_date and end_date
            how_many_years = timespan_in_days // 365
            if how_many_years == 0:
                how_many_years_string = None
            elif how_many_years == 1:
                how_many_years_string = f"1 {locale_catalog['year']}"
            else:
                how_many_years_string = f"{how_many_years} {locale_catalog['years']}"

            # Calculate number of months between start_date and end_date
            how_many_months = round((timespan_in_days % 365) / 30)
            if how_many_months <= 1:
                how_many_months_string = f"1 {locale_catalog['month']}"
            else:
                how_many_months_string = f"{how_many_months} {locale_catalog['months']}"

            # Combine howManyYearsString and howManyMonthsString
            if how_many_years_string is None:
                time_span_string = how_many_months_string
            else:
                time_span_string = f"{how_many_years_string} {how_many_months_string}"

            return time_span_string


class NormalEntryBase(RenderCVBaseModel):
    name: str = pydantic.Field(
        title="Name",
        description="The name of the NormalEntry.",
    )


# The following class is to ensure NormalEntryBase keys come first, then the keys
# of the EntryBase class. The only way to achieve this in Pydantic is to do this.
class NormalEntry(EntryBase, NormalEntryBase):
    """This class is the data model of `NormalEntry`."""
    pass


class ExperienceEntryBase(RenderCVBaseModel):
    company: str = pydantic.Field(
        title="Company",
        description="The company name.",
    )
    position: str = pydantic.Field(
        title="Position",
        description="The position.",
    )


# The following class is to make sure ExperienceEntryBase keys come first, then the
# keys of the EntryBase class. The only way to achieve this in Pydantic is to do
# this.
class ExperienceEntry(EntryBase, ExperienceEntryBase):
    """This class is the data model of `ExperienceEntry`."""
    pass


class EducationEntryBase(RenderCVBaseModel):
    institution: str = pydantic.Field(
        title="Institution",
        description="The institution name.",
    )
    area: str = pydantic.Field(
        title="Area",
        description="The area of study.",
    )
    degree: Optional[str] = pydantic.Field(
        default=None,
        title="Degree",
        description="The type of the degree.",
        examples=["BS", "BTech", "BEng", "BA", "PhD", "MS"],
    )


# The following class is to ensure EducationEntryBase keys come first,
# then the keys of the EntryBase class. The only way to achieve this in Pydantic is
# to do this.
class EducationEntry(EntryBase, EducationEntryBase):
    """This class is the data model of `EducationEntry`."""
    pass


# Create custom types named Entry and ListOfEntries
Entry = (
    OneLineEntry
    | NormalEntry
    | ExperienceEntry
    | EducationEntry
    | PublicationEntry
    | BulletEntry
    | str
)
ListOfEntries = list[
    OneLineEntry
    | NormalEntry
    | ExperienceEntry
    | EducationEntry
    | PublicationEntry
    | BulletEntry
    | str
]
entry_types = Entry.__args__[:-1]  # A tuple of all the entry types except str
entry_type_names = [entry_type.__name__ for entry_type in entry_types] + ["TextEntry"]


# ======================================================================================
# Section models: ======================================================================
# ======================================================================================

# Each section data model has a field named `entry_type` and a field named `entries`.
# Since the same pydantic.Field object is used in each of the section models, it is
# defined as a separate variable and used in each of the section models:
entry_type_field_of_section_model = pydantic.Field(
    title="Entry Type",
    description="The type of the entries in the section.",
)
entries_field_of_section_model = pydantic.Field(
    title="Entries",
    description="The entries of the section. The format depends on the entry type.",
)


class SectionBase(RenderCVBaseModel):
    """This class is the parent class of all the section types. It is being used
    because all of the section types have a common field called `title`.
    """

    title: str
    entry_type: str
    entries: list[Entry]


def create_a_section_model(entry_type: Type[Entry]) -> Type[SectionBase]:
    """
    Create a section model based on the entry type. See [Pydantic's documentation
    about dynamic model
    creation](https://pydantic-docs.helpmanual.io/usage/models/#dynamic-model-creation)
    for more information.

    Args:
        entry_type (Type[Entry]): The entry type to create the section model.
    Returns:
        Type[SectionBase]: The section model.
    """
    if entry_type == str:
        model_name = "SectionWithTextEntries"
        entry_type_name = "TextEntry"
    else:
        model_name = "SectionWith" + entry_type.__name__.replace("Entry", "Entries")
        entry_type_name = entry_type.__name__

    SectionModel = pydantic.create_model(
        model_name,
        entry_type=(Literal[entry_type_name], ...),  # type: ignore
        entries=(list[entry_type], ...),
        __base__=SectionBase,
    )

    return SectionModel


def get_entry_and_section_type(
    entry: dict[str, Any] | Entry,
) -> tuple[
    str,
    Type[SectionBase],
]:
    """
    Determine the entry and section type based on the entry.

    Args:
        entry: The entry to determine the type.
    Returns:
        tuple[str, Type[Section]]: The entry type and the section type.
    """
    # Get the class attributes of EntryBase class
    common_attributes = set(EntryBase.model_fields.keys())

    if isinstance(entry, dict):
        entry_type = None  # The entry type is not determined yet

        for EntryType in entry_types:
            characteristic_entry_attributes = (
                set(EntryType.model_fields.keys()) - common_attributes
            )

            # If at least one of the characteristic_entry_attributes is in the entry,
            # then it means the entry is of this type
            if characteristic_entry_attributes & set(entry.keys()):
                entry_type = EntryType.__name__
                section_type = create_a_section_model(EntryType)
                break

        if entry_type is None:
            raise ValueError("The entry is not provided correctly.")

    elif isinstance(entry, str):
        # Then it is a TextEntry
        entry_type = "TextEntry"
        section_type = create_a_section_model(str)

    else:
        # Then the entry is already initialized with a data model
        entry_type = entry.__class__.__name__
        section_type = create_a_section_model(entry.__class__)

    return entry_type, section_type


def validate_section_input(
    sections_input: SectionBase | list[Any],
) -> SectionBase | list[Any]:
    """
    Validate a `SectionInput` object and raise an error if it is not valid.

    Sections input is very complex. It is either a `Section` object or a list of
    entries. Since there are multiple entry types, it is not possible to validate it
    directly. This function looks at the entry list's first element and determines the
    section's entry type based on the first element. Then, it validates the rest of the
    list based on the determined entry type. If it is a `Section` object, it then
    validates it directly.

    Args:
        sections_input (SectionBase | list[Any]): The sections input to validate.
    Returns:
        SectionBase | list[Any]: The validated sections input.
    """
    if isinstance(sections_input, list):
        # Find the entry type based on the first identifiable entry
        entry_type = None
        section_type = None
        for entry in sections_input:
            try:
                entry_type, section_type = get_entry_and_section_type(entry)
                break
            except ValueError:
                pass

        if entry_type is None or section_type is None:
            raise ValueError(
                "RenderCV couldn't match this section with any entry types! Please"
                " check the entries and make sure they are provided correctly.",
                "",  # This is the location of the error
                "",  # This is value of the error
            )

        test_section = {
            "title": "Test Section",
            "entry_type": entry_type,
            "entries": sections_input,
        }

        try:
            section_type.model_validate(
                test_section,
            )
        except pydantic.ValidationError as e:
            new_error = ValueError(
                "There are problems with the entries. RenderCV detected the entry type"
                f" of this section to be {entry_type}! The problems are shown below.",
                "",  # This is the location of the error
                "",  # This is value of the error
            )
            raise new_error from e

    return sections_input


# Create a custom type named SectionInput so that it can be validated with
# `validate_section_input` function.
SectionInput = Annotated[
    ListOfEntries,
    pydantic.BeforeValidator(validate_section_input),
]


# ======================================================================================
# Full RenderCV data models: ===========================================================
# ======================================================================================

SocialNetworkName = Literal[
    "LinkedIn",
    "GitHub",
    "GitLab",
    "Instagram",
    "ORCID",
    "Mastodon",
    "Twitter",
    "X",
    "StackOverflow",
    "ResearchGate",
    "YouTube",
    "Google Scholar",
]
available_social_networks = get_args(SocialNetworkName)


class SocialNetwork(RenderCVBaseModel):
    """This class is the data model of a social network."""

    network: SocialNetworkName = pydantic.Field(
        title="Social Network",
        description="Name of the social network.",
    )
    username: str = pydantic.Field(
        title="Username",
        description="The username of the social network. The link will be generated.",
    )

    @pydantic.field_validator("username")
    @classmethod
    def check_username(cls, username: str, info: pydantic.ValidationInfo) -> str:
        """Check if the username is provided correctly."""
        network = info.data["network"]

        if network == "Mastodon":
            mastodon_username_pattern = r"@[^@]+@[^@]+"
            if not re.fullmatch(mastodon_username_pattern, username):
                raise ValueError(
                    'Mastodon username should be in the format "@username@domain"!'
                )
        if network == "StackOverflow":
            stackoverflow_username_pattern = r"\d+\/[^\/]+"
            if not re.fullmatch(stackoverflow_username_pattern, username):
                raise ValueError(
                    'StackOverflow username should be in the format "user_id/username"!'
                )
        if network == "YouTube":
            youtube_username_pattern = r"@[^@]+"
            if not re.fullmatch(youtube_username_pattern, username):
                raise ValueError(
                    'YouTube username should be in the format "@username"!'
                )

        return username

    @pydantic.model_validator(mode="after")  # type: ignore
    def check_url(self) -> "SocialNetwork":
        """Validate the URLs of the social networks."""
        url = self.url
        url_validator.validate_strings(url)
        return self

    @functools.cached_property
    def url(self) -> str:
        """Return the URL of the social network."""
        if self.network == "Mastodon":
            # Split domain and username
            dummy, username, domain = self.username.split("@")
            url = f"https://{domain}/@{username}"
        else:
            url_dictionary = {
                "LinkedIn": "https://linkedin.com/in/",
                "GitHub": "https://github.com/",
                "GitLab": "https://gitlab.com/",
                "Instagram": "https://instagram.com/",
                "ORCID": "https://orcid.org/",
                "Twitter": "https://twitter.com/",
                "X": "https://x.com/",
                "StackOverflow": "https://stackoverflow.com/users/",
                "ResearchGate": "https://researchgate.net/profile/",
                "YouTube": "https://youtube.com/",
                "Google Scholar": "https://scholar.google.com/citations?user=",
            }
            url = url_dictionary[self.network] + self.username

        return url


class CurriculumVitae(RenderCVBaseModel):
    """This class is the data model of the CV."""

    name: Optional[str] = pydantic.Field(
        default=None,
        title="Name",
        description="The name of the person.",
    )
    label: Optional[str] = pydantic.Field(
        default=None,
        title="Label",
        description="The label of the person.",
    )
    location: Optional[str] = pydantic.Field(
        default=None,
        title="Location",
        description="The location of the person.",
    )
    email: Optional[pydantic.EmailStr] = pydantic.Field(
        default=None,
        title="Email",
        description="The email address of the person.",
    )
    phone: Optional[pydantic_phone_numbers.PhoneNumber] = pydantic.Field(
        default=None,
        title="Phone",
        description="The phone number of the person.",
    )
    website: Optional[pydantic.HttpUrl] = pydantic.Field(
        default=None,
        title="Website",
        description="The website of the person.",
    )
    social_networks: Optional[list[SocialNetwork]] = pydantic.Field(
        default=None,
        title="Social Networks",
        description="The social networks of the person.",
    )
    sections_input: Optional[dict[str, SectionInput]] = pydantic.Field(
        default=None,
        title="Sections",
        description="The sections of the CV.",
        alias="sections",
    )

    @functools.cached_property
    def connections(self) -> list[dict[str, str]]:
        """Return all the connections of the person."""
        connections: list[dict[str, str]] = []

        if self.location is not None:
            connections.append(
                {
                    "latex_icon": "\\faMapMarker*",
                    "url": "",
                    "clean_url": "",
                    "placeholder": self.location,
                }
            )

        if self.email is not None:
            connections.append(
                {
                    "latex_icon": "\\faEnvelope[regular]",
                    "url": f"mailto:{self.email}",
                    "clean_url": self.email,
                    "placeholder": self.email,
                }
            )

        if self.phone is not None:
            phone_placeholder = self.phone.replace("tel:", "").replace("-", " ")
            connections.append(
                {
                    "latex_icon": "\\faPhone*",
                    "url": f"{self.phone}",
                    "clean_url": phone_placeholder,
                    "placeholder": phone_placeholder,
                }
            )

        if self.website is not None:
            website_placeholder = str(self.website).replace("https://", "").rstrip("/")
            connections.append(
                {
                    "latex_icon": "\\faLink",
                    "url": self.website,
                    "clean_url": website_placeholder,
                    "placeholder": website_placeholder,
                }
            )

        if self.social_networks is not None:
            icon_dictionary = {
                "LinkedIn": "\\faLinkedinIn",
                "GitHub": "\\faGithub",
                "GitLab": "\\faGitlab",
                "Instagram": "\\faInstagram",
                "Mastodon": "\\faMastodon",
                "ORCID": "\\faOrcid",
                "StackOverflow": "\\faStackOverflow",
                "Twitter": "\\faTwitter",
                "X": "\\faX",
                "ResearchGate": "\\faResearchgate",
                "YouTube": "\\faYoutube",
                "Google Scholar": "\\faGraduationCap",
            }
            for social_network in self.social_networks:
                clean_url = social_network.url.replace("https://", "").rstrip("/")
                connection = {
                    "latex_icon": icon_dictionary[social_network.network],
                    "url": social_network.url,
                    "clean_url": clean_url,
                    "placeholder": social_network.username,
                }

                if social_network.network == "StackOverflow":
                    username = social_network.username.split("/")[1]
                    connection["placeholder"] = username
                if social_network.network == "Google Scholar":
                    connection["placeholder"] = "Google Scholar"

                connections.append(connection)

        return connections

    @functools.cached_property
    def sections(self) -> list[SectionBase]:
        """Return all the sections of the CV with their titles."""
        sections: list[SectionBase] = []
        if self.sections_input is not None:
            for title, section_or_entries in self.sections_input.items():
                title = title.replace("_", " ").title()

                entry_type, section_type = get_entry_and_section_type(
                    section_or_entries[0]
                )

                section = section_type(
                    title=title,
                    entry_type=entry_type,  # type: ignore
                    entries=section_or_entries,  # type: ignore
                )
                sections.append(section)

        return sections


class LocaleCatalog(RenderCVBaseModel):
    """
    This class is the data model of the locale catalog. The values of each field
    updates the `locale_catalog` dictionary.
    """

    month: Optional[str] = pydantic.Field(
        default="month",
        title='Translation of "Month"',
        description='Translation of the word "month" in the locale.',
        validate_default=True,  # Initialize the locale catalog with the default values
    )
    months: Optional[str] = pydantic.Field(
        default="months",
        title='Translation of "Months"',
        description='Translation of the word "months" in the locale.',
        validate_default=True,  # Initialize the locale catalog with the default values
    )
    year: Optional[str] = pydantic.Field(
        default="year",
        title='Translation of "Year"',
        description='Translation of the word "year" in the locale.',
        validate_default=True,  # Initialize the locale catalog with the default values
    )
    years: Optional[str] = pydantic.Field(
        default="years",
        title='Translation of "Years"',
        description='Translation of the word "years" in the locale.',
        validate_default=True,  # Initialize the locale catalog with the default values
    )
    present: Optional[str] = pydantic.Field(
        default="present",
        title='Translation of "Present"',
        description='Translation of the word "present" in the locale.',
        validate_default=True,  # Initialize the locale catalog with the default values
    )
    to: Optional[str] = pydantic.Field(
        default="to",
        title='Translation of "To"',
        description='Translation of the word "to" in the locale.',
        validate_default=True,  # Initialize the locale catalog with the default values
    )
    abbreviations_for_months: Optional[
        Annotated[list[str], at.Len(min_length=12, max_length=12)]
    ] = pydantic.Field(
        default=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "June",
            "July",
            "Aug",
            "Sept",
            "Oct",
            "Nov",
            "Dec",
        ],
        title="Abbreviations of Months",
        description="Abbreviations of the months in the locale.",
        validate_default=True,  # To initialize the locale catalog with the default values
    )

    @pydantic.field_validator(
        "month", "months", "year", "years", "present", "abbreviations_for_months", "to"
    )
    @classmethod
    def update_translations(cls, value: str, info: pydantic.ValidationInfo) -> str:
        """Update the `locale_catalog` dictionary with the provided translations."""
        if value:
            locale_catalog[info.field_name] = value

        return value


# ======================================================================================
# ======================================================================================
# ======================================================================================

# Create a custom type named Design:
# It is a union of all the design options and the correct design option is determined by
# the theme field, thanks to Pydantic's discriminator feature.
# See https://docs.pydantic.dev/2.5/concepts/fields/#discriminator for more information
RenderCVDesign = Annotated[
    ClassicThemeOptions
    | ModerncvThemeOptions
    | Sb2novThemeOptions
    | EngineeringresumesThemeOptions,
    pydantic.Field(discriminator="theme"),
]
rendercv_design_validator = pydantic.TypeAdapter(RenderCVDesign)
available_themes = ["classic", "moderncv", "sb2nov", "engineeringresumes"]


class RenderCVDataModel(RenderCVBaseModel):
    """This class binds both the CV and the design information together."""

    cv: CurriculumVitae = pydantic.Field(
        title="Curriculum Vitae",
        description="The data of the CV.",
    )
    design: pydantic.json_schema.SkipJsonSchema[Any] | RenderCVDesign = pydantic.Field(
        default=ClassicThemeOptions(theme="classic"),
        title="Design",
        description=(
            "The design information of the CV. The default is the classic theme."
        ),
    )
    locale_catalog: Optional[LocaleCatalog] = pydantic.Field(
        default=None,
        title="Locale Catalog",
        description=(
            "The locale catalog of the CV to allow the support of multiple languages."
        ),
        validate_default=True,  # To initialize the locale catalog with the default values
    )

    @pydantic.field_validator("design", mode="before")
    @classmethod
    def initialize_if_custom_theme_is_used(
        cls, design: RenderCVDesign | Any
    ) -> RenderCVDesign | Any:
        """Initialize the custom theme if it is used and validate it. Otherwise, return
        the built-in theme."""
        # `get_args` for an Annotated object returns the arguments when Annotated is
        # used. The first argument is actually the union of the types, so we need to
        # access the first argument to use isinstance function.
        theme_data_model_types = get_args(RenderCVDesign)[0]

        if isinstance(design, theme_data_model_types):
            # Then it means RenderCVDataModel is already initialized with a design, so
            # return it as is
            return design
        elif design["theme"] in available_themes:  # type: ignore
            # Then it means it's a built-in theme, but it is not initialized (validated)
            # yet. So, validate and return it:=
            return rendercv_design_validator.validate_python(design)
        else:
            # Then it means it is a custom theme, so initialize and validate it
            theme_name: str = str(design["theme"])

            # Check if the theme name is valid
            if not theme_name.isalpha():
                raise ValueError(
                    "The custom theme name should contain only letters.",
                    "theme",  # This is the location of the error
                    theme_name,  # This is value of the error
                )

            # Then it is a custom theme
            custom_theme_folder = pathlib.Path(theme_name)

            # Check if the custom theme folder exists
            if not custom_theme_folder.exists():
                raise ValueError(
                    f"The custom theme folder `{custom_theme_folder}` does not exist."
                    " It should be in the working directory as the input file.",
                    "",  # This is the location of the error
                    theme_name,  # This is value of the error
                )

            # Check if all the necessary files are provided in the custom theme folder
            required_entry_files = [
                entry_type_name + ".j2.tex" for entry_type_name in entry_type_names
            ]
            required_files = [
                "SectionBeginning.j2.tex",  # Section beginning template
                "SectionEnding.j2.tex",  # Section ending template
                "Preamble.j2.tex",  # Preamble template
                "Header.j2.tex",  # Header template
            ] + required_entry_files

            for file in required_files:
                file_path = custom_theme_folder / file
                if not file_path.exists():
                    raise ValueError(
                        f"You provided a custom theme, but the file `{file}` is not"
                        f" found in the folder `{custom_theme_folder}`.",
                        "",  # This is the location of the error
                        theme_name,  # This is value of the error
                    )

            # Import __init__.py file from the custom theme folder if it exists
            path_to_init_file = pathlib.Path(f"{theme_name}/__init__.py")

            if path_to_init_file.exists():
                spec = importlib.util.spec_from_file_location(
                    "theme",
                    path_to_init_file,
                )

                theme_module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(theme_module)  # type: ignore
                except SyntaxError:
                    raise ValueError(
                        f"The custom theme {theme_name}'s __init__.py file has a syntax"
                        " error. Please fix it.",
                    )
                except ImportError:
                    raise ValueError(
                        f"The custom theme {theme_name}'s __init__.py file has an"
                        " import error. If you have copy-pasted RenderCV's built-in"
                        " themes, make sure tto update the import statements (e.g.,"
                        ' "from . import..." to "from rendercv.themes import...").',
                    )

                ThemeDataModel = getattr(
                    theme_module, f"{theme_name.capitalize()}ThemeOptions"  # type: ignore
                )

                # Initialize and validate the custom theme data model
                theme_data_model = ThemeDataModel(**design)
            else:
                # Then it means there is no __init__.py file in the custom theme folder.
                # Create a dummy data model and use that instead.
                class ThemeOptionsAreNotProvided(RenderCVBaseModel):
                    theme: str = theme_name

                theme_data_model = ThemeOptionsAreNotProvided(theme=theme_name)

            return theme_data_model

    @pydantic.field_validator("locale_catalog")
    @classmethod
    def initialize_locale_catalog(cls, locale_catalog: LocaleCatalog) -> LocaleCatalog:
        """Even if the locale catalog is not provided, initialize it with the default
        values."""
        if locale_catalog is None:
            LocaleCatalog()

        return locale_catalog


def set_or_update_a_value(
    data_model: pydantic.BaseModel | dict | list,
    key: str,
    value: str,
    sub_model: pydantic.BaseModel | dict | list = None,
):
    """
    Set or update a value in a data model for a specific key. For example, a key can
    be `cv.sections.education.3.institution` and the value can be "Bogazici University".

    Args:
        data_model (pydantic.BaseModel | dict | list): The data model to set or update
            the value.
        key (str): The key to set or update the value.
        value (Any): The value to set or update.
        sub_model (pydantic.BaseModel | dict | list, optional): The sub model to set or
            update the value. This is used for recursive calls. When the value is set
            to a sub model, the original data model is validated. Defaults to None.
    """
    # Recursively call this function until the last key is reached:

    # Rename `sections` with `sections_input` since the key is `sections` is an alias:
    key = key.replace("sections.", "sections_input.")
    keys = key.split(".")

    if sub_model is not None:
        model = sub_model
    else:
        model = data_model

    if len(keys) == 1:
        # Set the value
        if value.startswith("{") and value.endswith("}"):
            # Allow users to assign dictionaries
            value = eval(value)
        elif value.startswith("[") and value.endswith("]"):
            # Allow users to assign lists
            value = eval(value)

        if isinstance(model, pydantic.BaseModel):
            setattr(model, key, value)
        elif isinstance(model, dict):
            model[key] = value
        elif isinstance(model, list):
            model[int(key)] = value
        else:
            raise ValueError(
                "The data model should be either a Pydantic data model, dictionary, or"
                " list.",
            )

        data_model = type(data_model).model_validate(
            (data_model.model_dump(by_alias=True))
        )
        return data_model
    else:
        # Get the first key and call the function with remaining keys
        first_key = keys[0]
        key = ".".join(keys[1:])
        if isinstance(model, pydantic.BaseModel):
            sub_model = getattr(model, first_key)
        elif isinstance(model, dict):
            sub_model = model[first_key]
        elif isinstance(model, list):
            sub_model = model[int(first_key)]
        else:
            raise ValueError(
                "The data model should be either a Pydantic data model, dictionary, or"
                " list.",
            )

        set_or_update_a_value(data_model, key, value, sub_model)


def read_input_file(
    file_path_or_contents: pathlib.Path | str,
) -> RenderCVDataModel:
    """
    Read the input file and return two instances of
    [RenderCVDataModel][rendercv.data_models.RenderCVDataModel]. The first instance is
    the data model with $\\LaTeX$ strings and the second instance is the data model with
    markdown strings.

    Args:
        file_path_or_contents (str): The path to the input file or the contents of the
            input file as a string.

    Returns:
        RenderCVDataModel: The data models with $\\LaTeX$ and markdown strings.
    """
    if isinstance(file_path_or_contents, pathlib.Path):
        # Check if the file exists
        if not file_path_or_contents.exists():
            raise FileNotFoundError(
                f"The input file [magenta]{file_path_or_contents}[/magenta] doesn't"
                " exist!"
            )

        # Check file extension
        accepted_extensions = [".yaml", ".yml", ".json", ".json5"]
        if file_path_or_contents.suffix not in accepted_extensions:
            user_friendly_accepted_extensions = [
                f"[green]{ext}[/green]" for ext in accepted_extensions
            ]
            user_friendly_accepted_extensions = ", ".join(
                user_friendly_accepted_extensions
            )
            raise ValueError(
                "The input file should have one of the following extensions:"
                f" {user_friendly_accepted_extensions}. The input file is"
                f" [magenta]{file_path_or_contents}[/magenta]."
            )

        file_content = file_path_or_contents.read_text(encoding="utf-8")
    else:
        file_content = file_path_or_contents

    input_as_dictionary: dict[str, Any] = ruamel.yaml.YAML().load(file_content)  # type: ignore

    # Validate parsed dictionary by creating an instance of RenderCVDataModel
    rendercv_data_model = RenderCVDataModel(**input_as_dictionary)

    return rendercv_data_model


def get_a_sample_data_model(
    name: str = "John Doe", theme: str = "classic"
) -> RenderCVDataModel:
    """Return a sample data model for new users to start with.

    Args:
        name (str, optional): The name of the person. Defaults to "John Doe".
    Returns:
        RenderCVDataModel: A sample data model.
    """
    # Check if theme is valid:
    if theme not in available_themes:
        available_themes_string = ", ".join(available_themes)
        raise ValueError(
            f"The theme should be one of the following: {available_themes_string}!"
            f' The provided theme is "{theme}".'
        )

    name = name.encode().decode("unicode-escape")

    sections = {
        "welcome_to_rendercv!": [
            (
                "[RenderCV](https://github.com/sinaatalay/rendercv) is a LaTeX-based"
                " CV/resume framework. It allows you to create a high-quality CV or"
                " resume as a PDF file from a YAML file, with **full Markdown syntax"
                " support** and **complete control over the LaTeX code**."
            ),
            (
                "The boilerplate content is taken from"
                " [here](https://github.com/dnl-blkv/mcdowell-cv), where a"
                " *clean and tidy CV* pattern is proposed by"
                " **[Gayle Laakmann McDowell](https://www.gayle.com/)**."
            ),
        ],
        "quick_guide": [
            BulletEntry(
                bullet=(
                    "Each section title is arbitrary, and each section contains a list"
                    " of entries."
                ),
            ),
            BulletEntry(
                bullet=(
                    "There are 7 unique entry types: *BulletEntry*, *TextEntry*,"
                    " *EducationEntry*, *ExperienceEntry*, *NormalEntry*,"
                    " *PublicationEntry*, and *OneLineEntry*."
                ),
            ),
            BulletEntry(
                bullet=(
                    "Select a section title, pick an entry type, and start writing your"
                    " section!"
                )
            ),
            BulletEntry(
                bullet=(
                    "[Here](https://docs.rendercv.com/user_guide/), you can find a"
                    " comprehensive user guide for RenderCV."
                )
            ),
        ],
        "education": [
            EducationEntry(
                institution="University of Pennsylvania",
                area="Computer Science",
                degree="BS",
                start_date="2000-09",
                end_date="2005-05",
                highlights=[
                    "GPA: 3.9/4.0 ([Transcript](https://example.com))",
                    (
                        "**Coursework:** Computer Architecture,"
                        " Comparison of Learning Algorithms,"
                        " Deep Learning"
                    ),
                ],
            ),
        ],
        "experience": [
            ExperienceEntry(
                company="Apple",
                position="Software Engineer",
                start_date="2005-06",
                end_date="2007-08",
                location="Cupertino, CA",
                highlights=[
                    (
                        "Reduced time to render the user's buddy list by 75% by"
                        " implementing a prediction algorithm"
                    ),
                    (
                        "Implemented iChat integration with OS X Spotlight Search by"
                        " creating a tool to extract metadata from saved chat"
                        " transcripts and provide metadata to a system-wide search"
                        " database"
                    ),
                    (
                        "Redesigned chat file format and implemented backward"
                        " compatibility for search"
                    ),
                ],
            ),
            ExperienceEntry(
                company="Microsoft",
                position="Lead Student Ambassador",
                start_date="2003-09",
                end_date="2005-04",
                location="Redmond, WA",
                highlights=[
                    (
                        "Promoted to Lead Student Ambassador in the Fall of 2004,"
                        " supervised 10-15 Student Ambassadors"
                    ),
                    (
                        "Created and taught the computer science course CSE 099:"
                        " Software Design and Development"
                    ),
                ],
            ),
            ExperienceEntry(
                company="University of Pennsylvania",
                position="Head Teaching Assistant",
                start_date="2001-10",
                end_date="2003-05",
                location="Philadelphia, PA",
                highlights=[
                    (
                        "Implemented a user interface for the VS open file switcher"
                        " (ctrl-tab) and extended it to tool windows"
                    ),
                    (
                        "Created a service to provide gradient across VS and VS"
                        " add-ins, optimizing its performance via caching"
                    ),
                    "Programmer Productivity Research Center (Summers 2001, 2002)",
                    (
                        "Built an app to compute the similarity of all methods in a"
                        " code base, reducing the time from $\\mathcal{O}(n^2)$ to"
                        " $\\mathcal{O}(n \\log n)$"
                    ),
                    (
                        "Created a test case generation tool that creates random XML"
                        " docs from XML Schema"
                    ),
                ],
            ),
            ExperienceEntry(
                company="Microsoft",
                position="Software Engineer Intern",
                start_date="2003-06",
                end_date="2003-08",
                location="Redmond, WA",
                highlights=[
                    (
                        "Automated the extraction and processing of large datasets from"
                        " legacy systems using SQL and Perl scripts"
                    ),
                ],
            ),
        ],
        "publications": [
            PublicationEntry(
                title=(
                    "Magneto-Thermal Thin Shell Approximation for 3D Finite Element"
                    " Analysis of No-Insulation Coils"
                ),
                authors=[
                    "Albert Smith",
                    f"***{name}***",
                    "Jane Derry",
                ],
                date="2004-01",
                doi="10.1109/TASC.2023.3340648",
            )
        ],
        "projects": [
            NormalEntry(
                name="Multi-User Drawing Tool",
                date="[github.com/username/repo](https://github.com/sinaatalay/rendercv)",
                highlights=[
                    (
                        "Developed an electronic classroom where multiple users can"
                        ' view and simultaneously draw on a "chalkboard" with each'
                        " person's edits synchronized"
                    ),
                    "Tools Used: C++, MFC",
                ],
            ),
            NormalEntry(
                name="Synchronized Calendar",
                date="[github.com/username/repo](https://github.com/sinaatalay/rendercv)",
                highlights=[
                    (
                        "Developed a desktop calendar with globally shared and"
                        " synchronized calendars, allowing users to schedule meetings"
                        " with other users"
                    ),
                    "Tools Used: C#, .NET, SQL, XML",
                ],
            ),
            NormalEntry(
                name="Operating System",
                date="2002",
                highlights=[
                    (
                        "Developed a UNIX-style OS with a scheduler, file system, text"
                        " editor, and calculator"
                    ),
                    "Tools Used: C",
                ],
            ),
        ],
        "additional_experience_and_awards": [
            OneLineEntry(
                label="Instructor (2003-2005)",
                details="Taught 2 full-credit computer science courses",
            ),
            OneLineEntry(
                label="Third Prize, Senior Design Project",
                details=(
                    "Awarded 3rd prize for a synchronized calendar project out of 100"
                    " entries"
                ),
            ),
        ],
        "technologies": [
            OneLineEntry(
                label="Languages",
                details="C++, C, Java, Objective-C, C#, SQL, JavaScript",
            ),
            OneLineEntry(
                label="Technologies",
                details=".NET, Microsoft SQL Server, XCode, Interface Builder",
            ),
        ],
    }
    cv = CurriculumVitae(
        name=name,
        location="Your Location",
        email="youremail@yourdomain.com",
        phone="+905419999999",  # type: ignore
        website="https://yourwebsite.com",  # type: ignore
        social_networks=[
            SocialNetwork(network="LinkedIn", username="yourusername"),
            SocialNetwork(network="GitHub", username="yourusername"),
        ],
        sections=sections,  # type: ignore
    )

    if theme == "classic":
        design = ClassicThemeOptions(theme="classic", show_timespan_in=["Experience"])
    else:
        design = rendercv_design_validator.validate_python({"theme": theme})  # type: ignore

    return RenderCVDataModel(cv=cv, design=design)


def dictionary_to_yaml(dictionary: dict[str, Any]) -> str:
    """
    Convert a dictionary to a YAML string.

    Args:
        dictionary (dict[str, Any]): The dictionary to be converted to YAML.
    Returns:
        str: The YAML string.
    """
    yaml_object = ruamel.yaml.YAML()
    yaml_object.encoding = "utf-8"
    yaml_object.width = 60
    yaml_object.indent(mapping=2, sequence=4, offset=2)
    with io.StringIO() as string_stream:
        yaml_object.dump(dictionary, string_stream)
        yaml_string = string_stream.getvalue()
    return yaml_string


def create_a_sample_yaml_input_file(
    input_file_path: Optional[pathlib.Path] = None,
    name: str = "John Doe",
    theme: str = "classic",
) -> str:
    """
    Create a sample YAML input file and return it as a string. If the input file path
    is provided, then also save the contents to the file.

    Args:
        input_file_path (pathlib.Path, optional): The path to save the input file.
            Defaults to None.
        name (str, optional): The name of the person. Defaults to "John Doe".
        theme (str, optional): The theme of the CV. Defaults to "classic".
    Returns:
        str: The sample YAML input file as a string.
    """
    data_model = get_a_sample_data_model(name=name, theme=theme)

    # Instead of getting the dictionary with data_model.model_dump() directly, we
    # convert it to JSON and then to a dictionary. Because the YAML library we are
    # using sometimes has problems with the dictionary returned by model_dump().

    # We exclude "cv.sections" because the data model automatically generates them.
    # The user's "cv.sections" input is actually "cv.sections_input" in the data
    # model. It is shown as "cv.sections" in the YAML file because an alias is being
    # used. If"cv.sections" were not excluded, the automatically generated
    # "cv.sections" would overwrite the "cv.sections_input". "cv.sections" are
    # automatically generated from "cv.sections_input" to make the templating
    # process easier. "cv.sections_input" exists for the convenience of the user.
    data_model_as_json = data_model.model_dump_json(
        exclude_none=True, by_alias=True, exclude={"cv": {"sections"}}
    )
    data_model_as_dictionary = json.loads(data_model_as_json)

    yaml_string = dictionary_to_yaml(data_model_as_dictionary)

    if input_file_path is not None:
        input_file_path.write_text(yaml_string, encoding="utf-8")

    return yaml_string


def generate_json_schema() -> dict[str, Any]:
    """
    Generate the JSON schema of RenderCV.

    JSON schema is generated for the users to make it easier for them to write the input
    file. The JSON Schema of RenderCV is saved in the `docs` directory of the repository
    and distributed to the users with the
    [JSON Schema Store](https://www.schemastore.org/).

    Returns:
        dict: The JSON schema of RenderCV.
    """

    class RenderCVSchemaGenerator(pydantic.json_schema.GenerateJsonSchema):
        def generate(self, schema, mode="validation"):  # type: ignore
            json_schema = super().generate(schema, mode=mode)

            # Basic information about the schema:
            json_schema["title"] = "RenderCV"
            json_schema["description"] = "RenderCV data model."
            json_schema["$id"] = (
                "https://raw.githubusercontent.com/sinaatalay/rendercv/main/schema.json"
            )
            json_schema["$schema"] = "http://json-schema.org/draft-07/schema#"

            # Loop through $defs and remove docstring descriptions and fix optional
            # fields
            for object_name, value in json_schema["$defs"].items():
                # Don't allow additional properties
                value["additionalProperties"] = False

                # If a type is optional, then Pydantic sets the type to a list of two
                # types, one of which is null. The null type can be removed since we
                # already have the required field. Moreover, we would like to warn
                # users if they provide null values. They can remove the fields if they
                # don't want to provide them.
                null_type_dict = {
                    "type": "null",
                }
                for field_name, field in value["properties"].items():
                    if "anyOf" in field:
                        if null_type_dict in field["anyOf"]:
                            field["anyOf"].remove(null_type_dict)

                        field["oneOf"] = field["anyOf"]
                        del field["anyOf"]

            return json_schema

    schema = RenderCVDataModel.model_json_schema(
        schema_generator=RenderCVSchemaGenerator
    )

    return schema


def generate_json_schema_file(json_schema_path: pathlib.Path):
    """
    Generate the JSON schema of RenderCV and save it to a file.

    Args:
        json_schema_path (pathlib.Path): The path to save the JSON schema.
    """
    schema = generate_json_schema()
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
    json_schema_path.write_text(schema_json, encoding="utf-8")
