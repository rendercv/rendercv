"""CV sections with automatic entry type detection based on field intersection analysis."""

from collections import Counter
from typing import Annotated, Any, Literal, get_args

import pydantic

from ..base import BaseModelWithoutExtraKeys
from .entries.bullet import BulletEntry
from .entries.education import EducationEntry
from .entries.experience import ExperienceEntry
from .entries.normal import NormalEntry
from .entries.numbered import NumberedEntry
from .entries.one_line import OneLineEntry
from .entries.publication import PublicationEntry
from .entries.reversed_numbered import ReversedNumberedEntry

########################################################################################
# Below needs to be updated when new entry types are added.

# str is an entry type (TextEntry) but not a model, so it's not included in EntryModel.
type EntryModel = (
    OneLineEntry
    | NormalEntry
    | ExperienceEntry
    | EducationEntry
    | PublicationEntry
    | BulletEntry
    | NumberedEntry
    | ReversedNumberedEntry
)

type ListOfEntries = (
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
########################################################################################
available_entry_models: tuple[type[EntryModel], ...] = get_args(EntryModel.__value__)
available_entry_type_names: tuple[str, ...] = tuple(
    [entry_type.__name__ for entry_type in available_entry_models] + ["TextEntry"]
)


def get_characteristic_entry_fields(
    entry_types: tuple[type[EntryModel], ...],
) -> dict[type[EntryModel], set[str]]:
    """Returns fields unique to each entry type, used for automatic type detection.

    Args:
        entry_types: The entry types to get their characteristic fields.

    Returns:
        The characteristic fields of the entry types. 
    """
    all_attributes: list[str] = []
    for EntryType in entry_types:
        all_attributes.extend(EntryType.model_fields.keys())

    attribute_counts = Counter(all_attributes)
    common_attributes = {attr for attr, count in attribute_counts.items() if count > 1}

    characteristic_entry_fields: dict[type[EntryModel], set[str]] = {}
    for EntryType in entry_types:
        characteristic_entry_fields[EntryType] = (
            set(EntryType.model_fields.keys()) - common_attributes
        )

    return characteristic_entry_fields


characteristic_entry_fields = get_characteristic_entry_fields(available_entry_models)


class SectionBase(BaseModelWithoutExtraKeys):
    title: str
    entry_type: str
    entries: list[Any]


def create_section_models(
    entry_type: type[EntryModel] | type[str],
) -> type[SectionBase]:
    """Create a section model based on the entry type.

    Args:
        entry_type: The entry type to create the section model.

    Returns:
        The section model (a Pydantic model).
    """
    if entry_type is str:
        model_name = "SectionWithTextEntries"
        entry_type_name = "TextEntry"
    else:
        model_name = "SectionWith" + entry_type.__name__.replace("Entry", "Entries")
        entry_type_name = entry_type.__name__

    return pydantic.create_model(
        model_name,
        entry_type=(Literal[entry_type_name], ...),
        entries=(list[entry_type], ...),
        __base__=SectionBase,
    )


section_models: dict[type[EntryModel] | type[str], type[SectionBase]] = {
    entry_type: create_section_models(entry_type)
    for entry_type in available_entry_models
}
section_models[str] = create_section_models(str)


def get_entry_type_name_and_section_model(
    entry: dict[str, str | list[str]] | str | EntryModel | None,
) -> tuple[str, type[SectionBase]]:
    """Get the entry type name and the section model based on the entry.

    It takes an entry (as a dictionary or a string) and a list of entry types. Then
    it determines the entry type and creates a section model based on the entry
    type.

    Args:
        entry: The entry to determine its type.

    Returns:
        The entry type name and the section model.
    """

    if isinstance(entry, dict):
        entry_type_name = None
        section_model = None
        for EntryType, characteristic_fields in characteristic_entry_fields.items():
            # If at least one of the characteristic_fields is in the entry,
            # then it means the entry is of this type:
            if characteristic_fields & set(entry.keys()):
                entry_type_name = EntryType.__name__
                section_model = section_models[EntryType]
                break

        if section_model is None or entry_type_name is None:
            message = "The entry does not match any entry type."
            raise ValueError(message)

    elif isinstance(entry, str):
        # Then it is a TextEntry
        entry_type_name = "TextEntry"
        section_model = section_models[str]

    elif entry is None:
        message = "The entry cannot be None."
        raise ValueError(message)

    else:
        # Then the entry is already initialized with a data model:
        entry_type_name = entry.__class__.__name__
        section_model = section_models[entry.__class__]

    return entry_type_name, section_model


def validate_section(sections_input: Any) -> Any:
    """Validate a list of entries (a section) based on the entry types.

    Args:
        sections_input: The sections input to validate.

    Returns:
        The validated sections input.
    """
    if isinstance(sections_input, list):
        # Find the entry type based on the first identifiable entry:
        entry_type_name = None
        section_type = None
        for entry in sections_input:
            try:
                entry_type_name, section_type = get_entry_type_name_and_section_model(
                    entry
                )
                break
            except ValueError:
                # If the entry type cannot be determined, try the next entry:
                pass

        if entry_type_name is None or section_type is None:
            message = (
                "RenderCV couldn't match this section with any entry types! Please"
                " check the entries and make sure they are provided correctly."
            )
            raise ValueError(
                message,
                "",  # This is the location of the error
                "",  # This is value of the error
            )

        section = {
            "title": "Dummy Section for Validation",
            "entry_type": entry_type_name,
            "entries": sections_input,
        }

        try:
            section_object = section_type.model_validate(section)
            sections_input = section_object.entries
        except pydantic.ValidationError as e:
            new_error = ValueError(
                "There are problems with the entries. RenderCV detected the entry type"
                f" of this section to be {entry_type_name}! The problems are shown"
                " below.",
                "",  # This is the location of the error
                "",  # This is value of the error
            )
            raise new_error from e

    else:
        message = (
            "Each section should be a list of entries! Please see the documentation for"
            " more information about the sections."
        )
        raise ValueError(message)

    return sections_input


# Create a custom type named Section, which is a list of entries. The entries
# can be any of the available entry types. The section is validated with the
# `validate_section` function.
type Section = Annotated[
    pydantic.json_schema.SkipJsonSchema[Any] | ListOfEntries,
    pydantic.BeforeValidator(lambda entries: validate_section(entries)),
]


def dictionary_key_to_proper_section_title(key: str) -> str:
    """Convert a dictionary key to a proper section title.

    Example:
        ```python
        dictionary_key_to_proper_section_title("section_title")
        ```
        returns
        `"Section Title"`

    Args:
        key: The key to convert to a proper section title.

    Returns:
        The proper section title.
    """
    # If there is either a space or an uppercase letter in the key, return it as is.
    if " " in key or any(letter.isupper() for letter in key):
        return key

    title = key.replace("_", " ")
    words = title.split(" ")

    words_not_capitalized_in_a_title = [
        "a",
        "and",
        "as",
        "at",
        "but",
        "by",
        "for",
        "from",
        "if",
        "in",
        "into",
        "like",
        "near",
        "nor",
        "of",
        "off",
        "on",
        "onto",
        "or",
        "over",
        "so",
        "than",
        "that",
        "to",
        "upon",
        "when",
        "with",
        "yet",
    ]

    return " ".join(
        (word.capitalize() if (word not in words_not_capitalized_in_a_title) else word)
        for word in words
    )


def get_sections_rendercv(sections: dict[str, list[Any]] | None) -> list[SectionBase]:
    """Compute the sections of the CV based on the input sections.

    The original `sections` input is a dictionary where the keys are the section
    titles and the values are the list of entries in that section. This function
    converts the input sections to a list of `SectionBase` objects. This makes it
    easier to work with the sections in the rest of the code.

    Args:
        sections: The sections to compute.

    Returns:
        The computed sections.
    """
    sections_rendercv: list[SectionBase] = []

    if sections is not None:
        for title, entries in sections.items():
            formatted_title = dictionary_key_to_proper_section_title(title)

            # The first entry can be used because all the entries in the section are
            # already validated with the `validate_a_section` function:
            entry_type_name, _ = get_entry_type_name_and_section_model(
                entries[0],  # type: ignore
            )

            # SectionBase is used so that entries are not validated again:
            section = SectionBase(
                title=formatted_title,
                entry_type=entry_type_name,
                entries=entries,
            )
            sections_rendercv.append(section)

    return sections_rendercv
