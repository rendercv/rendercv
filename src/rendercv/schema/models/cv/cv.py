import functools
import importlib
import pathlib
from typing import Annotated, Any, Literal

import pydantic
import pydantic_extra_types.phone_numbers as pydantic_phone_numbers

from ..base import BaseModelWithoutExtraKeys
from .social_network import SocialNetwork


class SectionBase(BaseModelWithoutExtraKeys):
    """This class is the parent class of all the section types. It is being used
    in RenderCV internally, and it is not meant to be used directly by the users.
    """

    title: str
    entry_type: str
    entries: list[Any]


def create_a_section_validator(entry_type: type) -> type[SectionBase]:
    """Create a section model based on the entry type. See [Pydantic's documentation
    about dynamic model
    creation](https://pydantic-docs.helpmanual.io/usage/models/#dynamic-model-creation)
    for more information.

    The section model is used to validate a section.

    Args:
        entry_type: The entry type to create the section model. It's not an instance of
            the entry type, but the entry type itself.

    Returns:
        The section validator (a Pydantic model).
    """
    if entry_type is str:
        model_name = "SectionWithTextEntries"
        entry_type_name = "TextEntry"
    else:
        model_name = "SectionWith" + entry_type.__name__.replace("Entry", "Entries")
        entry_type_name = entry_type.__name__

    return pydantic.create_model(
        model_name,
        entry_type=(Literal[entry_type_name], ...),  # type: ignore
        entries=(list[entry_type], ...),
        __base__=SectionBase,
    )


def get_characteristic_entry_attributes(
    entry_types: tuple[type],
) -> dict[type, set[str]]:
    """Get the characteristic attributes of the entry types.

    Args:
        entry_types: The entry types to get their characteristic attributes. These are
            not instances of the entry types, but the entry types themselves. `str` type
            should not be included in this list.

    Returns:
        The characteristic attributes of the entry types.
    """
    # Look at all the entry types, collect their attributes with
    # EntryType.model_fields.keys() and find the common ones.
    all_attributes: list[str] = []
    for EntryType in entry_types:
        all_attributes.extend(EntryType.model_fields.keys())

    common_attributes = {
        attribute for attribute in all_attributes if all_attributes.count(attribute) > 1
    }

    # Store each entry type's characteristic attributes in a dictionary:
    characteristic_entry_attributes: dict[type, set[str]] = {}
    for EntryType in entry_types:
        characteristic_entry_attributes[EntryType] = (
            set[str](EntryType.model_fields.keys()) - common_attributes
        )

    return characteristic_entry_attributes


def get_entry_type_name_and_section_validator(
    entry: dict[str, str | list[str]] | str | type | None, entry_types: tuple[type]
) -> tuple[str, type[SectionBase]]:
    """Get the entry type name and the section validator based on the entry.

    It takes an entry (as a dictionary or a string) and a list of entry types. Then
    it determines the entry type and creates a section validator based on the entry
    type.

    Args:
        entry: The entry to determine its type.
        entry_types: The entry types to determine the entry type. These are not
            instances of the entry types, but the entry types themselves. `str` type
            should not be included in this list.

    Returns:
        The entry type name and the section validator.
    """

    if isinstance(entry, dict):
        entry_type_name = None  # the entry type is not determined yet
        characteristic_entry_attributes = get_characteristic_entry_attributes(
            entry_types
        )

        for (
            EntryType,
            characteristic_attributes,
        ) in characteristic_entry_attributes.items():
            # If at least one of the characteristic_entry_attributes is in the entry,
            # then it means the entry is of this type:
            if characteristic_attributes & set(entry.keys()):
                entry_type_name = EntryType.__name__
                section_type = create_a_section_validator(EntryType)
                break

        if entry_type_name is None:
            message = "The entry is not provided correctly."
            raise ValueError(message)

    elif isinstance(entry, str):
        # Then it is a TextEntry
        entry_type_name = "TextEntry"
        section_type = create_a_section_validator(str)

    elif entry is None:
        message = "The entry cannot be a null value."
        raise ValueError(message)

    else:
        # Then the entry is already initialized with a data model:
        entry_type_name = entry.__class__.__name__
        section_type = create_a_section_validator(entry.__class__)

    return entry_type_name, section_type  # type: ignore


def validate_a_section(
    sections_input: list[Any], entry_types: tuple[type]
) -> list[entry_types.Entry]:
    """Validate a list of entries (a section) based on the entry types.

    Sections input is a list of entries. Since there are multiple entry types, it is not
    possible to validate it directly. Firstly, the entry type is determined with the
    `get_entry_type_name_and_section_validator` function. If the entry type cannot be
    determined, an error is raised. If the entry type is determined, the rest of the
    list is validated with the section validator.

    Args:
        sections_input: The sections input to validate.
        entry_types: The entry types to determine the entry type. These are not
            instances of the entry types, but the entry types themselves. `str` type
            should not be included in this list.

    Returns:
        The validated sections input.
    """
    if isinstance(sections_input, list):
        # Find the entry type based on the first identifiable entry:
        entry_type_name = None
        section_type = None
        for entry in sections_input:
            try:
                entry_type_name, section_type = (
                    get_entry_type_name_and_section_validator(entry, entry_types)
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
            "title": "Test Section",
            "entry_type": entry_type_name,
            "entries": sections_input,
        }

        try:
            section_object = section_type.model_validate(
                section,
            )
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


# ======================================================================================
# Create custom types: =================================================================
# ======================================================================================

# Create a custom type named SectionContents, which is a list of entries. The entries
# can be any of the available entry types. The section is validated with the
# `validate_a_section` function.
SectionContents = Annotated[
    pydantic.json_schema.SkipJsonSchema[Any] | entry_types.ListOfEntries,
    pydantic.BeforeValidator(
        lambda entries: validate_a_section(
            entries, entry_types=entry_types.available_entry_models
        )
    ),
]

# ======================================================================================
# Create the models: ===================================================================
# ======================================================================================


class CurriculumVitae(BaseModelWithoutExtraKeys):
    name: str | None = None
    location: str | None = None
    email: pydantic.EmailStr | None = None
    photo: pathlib.Path | None = pydantic.Field(
        default=None,
        description="Path to the photo of the person, relative to the input file.",
    )
    phone: pydantic_phone_numbers.PhoneNumber | None = pydantic.Field(
        default=None,
        description=(
            "Country code should be included. For example, +1 for the United States."
        ),
    )
    website: pydantic.HttpUrl | None = None
    social_networks: list[SocialNetwork] | None = None
    sections: dict[str, SectionContents] | None = None
    sort_entries: Literal["reverse-chronological", "chronological", "none"] = "none"

    @pydantic.field_validator("photo")
    @classmethod
    def update_photo_path(cls, value: pathlib.Path | None) -> pathlib.Path | None:
        """Cast `photo` to Path and make the path absolute"""
        if value:
            module = importlib.import_module(".rendercv_data_model", __package__)
            INPUT_FILE_DIRECTORY = module.INPUT_FILE_DIRECTORY

            if INPUT_FILE_DIRECTORY is not None:
                profile_picture_parent_folder = INPUT_FILE_DIRECTORY
            else:
                profile_picture_parent_folder = pathlib.Path.cwd()

            return profile_picture_parent_folder / str(value)

        return value

    @functools.cached_property
    def sections_rendercv(self) -> list[SectionBase]:
        """Compute the sections of the CV based on the input sections.

        The original `sections` input is a dictionary where the keys are the section titles
        and the values are the list of entries in that section. This function converts the
        input sections to a list of `SectionBase` objects. This makes it easier to work with
        the sections in the rest of the code.

        Returns:
            The computed sections.
        """
        sections: list[SectionBase] = []

        if self.sections is not None:
            for title, entries in self.sections.items():
                formatted_title = computers.dictionary_key_to_proper_section_title(
                    title
                )

                # The first entry can be used because all the entries in the section are
                # already validated with the `validate_a_section` function:
                entry_type_name, _ = get_entry_type_name_and_section_validator(
                    entries[0],  # type: ignore
                    entry_types=entry_types.available_entry_models,
                )

                sort_order = self.sort_entries
                sorted_entries = entry_types.sort_entries_by_date(entries, sort_order)

                # SectionBase is used so that entries are not validated again:
                section = SectionBase(
                    title=formatted_title,
                    entry_type=entry_type_name,
                    entries=sorted_entries,
                )
                sections.append(section)

        return sections

    @pydantic.field_serializer("phone")
    def serialize_phone(
        self, phone: pydantic_phone_numbers.PhoneNumber | None
    ) -> str | None:
        """Serialize the phone number."""
        if phone is not None:
            return phone.replace("tel:", "")

        return phone

    # Store the order of the keys in the YAML `cv` mapping so that the header
    # connections can be rendered in the same order that the user defines.
    _key_order: list[str] = pydantic.PrivateAttr(default_factory=list)

    @pydantic.model_validator(mode="wrap")
    @classmethod
    def capture_input_order(cls, data: Any, handler) -> "CurriculumVitae":
        # Capture the input order before validation
        key_order = list[str](data.keys()) if isinstance(data, dict) else []

        # Let Pydantic do its validation
        instance = handler(data)

        # Set the private attribute on the instance
        instance._key_order = key_order
