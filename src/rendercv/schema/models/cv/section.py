from collections import Counter
from functools import reduce
from operator import or_
from typing import Annotated, Any, Literal, get_args

import pydantic
import pydantic_core

from ...pydantic_error_handling import CustomPydanticErrorTypes
from ..base import BaseModelWithoutExtraKeys
from .entries.bullet import BulletEntry
from .entries.education import EducationEntry
from .entries.experience import ExperienceEntry
from .entries.normal import NormalEntry
from .entries.numbered import NumberedEntry
from .entries.one_line import OneLineEntry
from .entries.publication import PublicationEntry
from .entries.reversed_numbered import ReversedNumberedEntry
from .entries.skill_icons import SkillIconsEntry

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
    | SkillIconsEntry
)
type Entry = EntryModel | str
########################################################################################
available_entry_models: tuple[type[EntryModel], ...] = get_args(EntryModel.__value__)
available_entry_type_names: tuple[str, ...] = tuple(
    [entry_type.__name__ for entry_type in available_entry_models] + ["TextEntry"]
)
type ListOfEntries = list[str] | reduce(  # ty: ignore[invalid-type-form]
    or_, [list[entry_type] for entry_type in available_entry_models]
)


def get_characteristic_entry_fields(
    entry_types: tuple[type[EntryModel], ...],
) -> dict[type[EntryModel], set[str]]:
    """Calculate unique fields per entry type for automatic type detection.

    Why:
        Users provide entries without explicit type declarations. Detecting
        entry type by unique fields (e.g., `degree` for EducationEntry)
        enables automatic routing to correct validators.

    Args:
        entry_types: Entry type classes to analyze.

    Returns:
        Map of entry types to their unique field names.
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


class BaseRenderCVSection(BaseModelWithoutExtraKeys):
    title: str
    entry_type: str
    entries: list[Any]

    @property
    def snake_case_title(self) -> str:
        return self.title.lower().replace(" ", "_")


def create_section_models(
    entry_type: type[EntryModel] | type[str],
) -> type[BaseRenderCVSection]:
    """Generate Pydantic model for section containing specific entry type.

    Why:
        Each section validates that all entries match a single type. Dynamic
        model generation creates type-safe section models with proper validation
        constraints for each entry type.

    Args:
        entry_type: Entry class or str for TextEntry.

    Returns:
        Pydantic section model class.
    """
    if entry_type is str:
        model_name = "SectionWithTextEntries"
        entry_type_name = "TextEntry"
    else:
        model_name = "SectionWith" + entry_type.__name__.replace("Entry", "Entries")
        entry_type_name = entry_type.__name__

    return pydantic.create_model(
        model_name,
        entry_type=(Literal[entry_type_name], ...),  # ty: ignore[invalid-type-form]
        entries=(list[entry_type], ...),  # ty: ignore[invalid-type-form]
        __base__=BaseRenderCVSection,
    )


section_models: dict[type[EntryModel] | type[str], type[BaseRenderCVSection]] = {
    entry_type: create_section_models(entry_type)
    for entry_type in available_entry_models
}
section_models[str] = create_section_models(str)


def get_entry_type_name_and_section_model(
    entry: dict[str, str | list[str]] | str | EntryModel | None,
) -> tuple[str, type[BaseRenderCVSection]]:
    """Infer entry type from entry data and return corresponding section model.

    Why:
        Sections contain mixed raw entry data (dicts/strings) before validation.
        Type inference via characteristic fields enables routing each entry to
        its correct validator model.

    Args:
        entry: Raw or validated entry data.

    Returns:
        Tuple of entry type name and section model class.
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
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "The entry does not match any entry type.",
            )

    elif isinstance(entry, str):
        # Then it is a TextEntry
        entry_type_name = "TextEntry"
        section_model = section_models[str]

    elif entry is None:
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "The entry cannot be None.",
        )

    else:
        # Then the entry is already initialized with a data model:
        entry_type_name = entry.__class__.__name__
        section_model = section_models[entry.__class__]

    return entry_type_name, section_model


def validate_section(sections_input: Any) -> Any:
    """Validate section entries with automatic type detection and error reporting.

    Why:
        Section validation must infer entry type from first valid entry,
        then validate all entries against that type. Custom error messages
        identify detected type and aggregate nested validation errors.

    Args:
        sections_input: Raw section data (list of entries).

    Returns:
        Validated list of entry instances.
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
            except pydantic_core.PydanticCustomError:
                # If the entry type cannot be determined, try the next entry:
                continue

        if entry_type_name is None or section_type is None:
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "RenderCV couldn't match this section with any entry types. Please"
                " check the entries and make sure they are provided correctly.",
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
            new_error = pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.entry_validation.value,
                "There are problems with the entries. RenderCV detected the entry type"
                " of this section to be {entry_type_name}. The problems are shown"
                " below.",
                {"entry_type_name": entry_type_name, "caused_by": e.errors()},
            )
            raise new_error from e

    else:
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "Each section should be a list of entries! This is not a list.",
        )

    return sections_input


# Create a custom type named Section, which is a list of entries. The entries can be any
# of the available entry types. The section is validated with the `validate_section`
# function.
type Section = Annotated[
    pydantic.json_schema.SkipJsonSchema[Any] | ListOfEntries,
    pydantic.BeforeValidator(lambda entries: validate_section(entries)),
]


def dictionary_key_to_proper_section_title(key: str) -> str:
    """Convert snake_case section key to title case with proper capitalization.

    Why:
        Users write `education_and_training` in YAML for readability. Rendering
        requires "Education and Training" with proper title case rules (lowercase
        articles/prepositions).

    Example:
        ```py
        title = dictionary_key_to_proper_section_title("education_and_training")
        # Returns "Education and Training"
        ```

    Args:
        key: Section key from YAML.

    Returns:
        Properly capitalized section title.
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


def get_rendercv_sections(
    sections: dict[str, list[Any]] | None,
) -> list[BaseRenderCVSection]:
    """Transform user's section dictionary into list of typed section objects.

    Why:
        YAML sections are dicts for user convenience (e.g., `{education: [...]}`).
        Template rendering requires list of section objects with title and
        entry_type fields. This conversion happens after validation.

    Args:
        sections: User's section dictionary with titles as keys.

    Returns:
        List of section objects ready for template rendering.
    """
    sections_rendercv: list[BaseRenderCVSection] = []

    if sections is not None:
        for title, entries in sections.items():
            formatted_title = dictionary_key_to_proper_section_title(title)

            # The first entry can be used because all the entries in the section are
            # already validated with the `validate_a_section` function:
            entry_type_name, _ = get_entry_type_name_and_section_model(
                entries[0],
            )

            # SectionBase is used so that entries are not validated again:
            section = BaseRenderCVSection(
                title=formatted_title,
                entry_type=entry_type_name,
                entries=entries,
            )
            sections_rendercv.append(section)

    return sections_rendercv
