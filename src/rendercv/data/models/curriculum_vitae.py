"""
The `rendercv.data.models.curriculum_vitae` module contains the data model of the `cv`
field of the input file.
"""

import functools
import importlib
import pathlib
import re
from typing import Annotated, Any, Literal, get_args

import pydantic
import pydantic_extra_types.phone_numbers as pydantic_phone_numbers

from . import computers, entry_types
from .base import RenderCVBaseModelWithExtraKeys, RenderCVBaseModelWithoutExtraKeys

# ======================================================================================
# Create validator functions: ==========================================================
# ======================================================================================


class SectionBase(RenderCVBaseModelWithoutExtraKeys):
    """This class is the parent class of all the section types. It is being used
    in RenderCV internally, and it is not meant to be used directly by the users.
    It is used by `rendercv.data_models.utilities.create_a_section_model` function to
    create a section model based on any entry type.
    """

    title: str
    entry_type: str
    entries: list[Any]


# Create a URL validator:
url_validator = pydantic.TypeAdapter(pydantic.HttpUrl)


def validate_url(url: str) -> str:
    """Validate a URL.

    Args:
        url: The URL to validate.

    Returns:
        The validated URL.
    """
    url_validator.validate_strings(url)
    return url


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
    all_attributes = []
    for EntryType in entry_types:
        all_attributes.extend(EntryType.model_fields.keys())

    common_attributes = {
        attribute for attribute in all_attributes if all_attributes.count(attribute) > 1
    }

    # Store each entry type's characteristic attributes in a dictionary:
    characteristic_entry_attributes = {}
    for EntryType in entry_types:
        characteristic_entry_attributes[EntryType] = (
            set(EntryType.model_fields.keys()) - common_attributes
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


def validate_a_social_network_username(username: str, network: str) -> str:
    """Check if the `username` field in the `SocialNetwork` model is provided correctly.

    Args:
        username: The username to validate.

    Returns:
        The validated username.
    """
    if network == "Mastodon":
        mastodon_username_pattern = r"@[^@]+@[^@]+"
        if not re.fullmatch(mastodon_username_pattern, username):
            message = 'Mastodon username should be in the format "@username@domain"!'
            raise ValueError(message)
    elif network == "StackOverflow":
        stackoverflow_username_pattern = r"\d+\/[^\/]+"
        if not re.fullmatch(stackoverflow_username_pattern, username):
            message = (
                'StackOverflow username should be in the format "user_id/username"!'
            )
            raise ValueError(message)
    elif network == "YouTube":
        if username.startswith("@"):
            message = (
                'YouTube username should not start with "@"! Remove "@" from the'
                " beginning of the username."
            )
            raise ValueError(message)
    elif network == "ORCID":
        orcid_username_pattern = r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]"
        if not re.fullmatch(orcid_username_pattern, username):
            message = "ORCID username should be in the format 'XXXX-XXXX-XXXX-XXX'!"
            raise ValueError(message)
    elif network == "IMDB":
        imdb_username_pattern = r"nm\d{7}"
        if not re.fullmatch(imdb_username_pattern, username):
            message = "IMDB name should be in the format 'nmXXXXXXX'!"
            raise ValueError(message)

    return username


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

# Create a custom type named SectionInput, which is a dictionary where the keys are the
# section titles and the values are the list of entries in that section.
Sections = dict[str, SectionContents] | None

# Create a custom type named SocialNetworkName, which is a literal type of the available
# social networks.
SocialNetworkName = Literal[
    "LinkedIn",
    "GitHub",
    "GitLab",
    "IMDB",
    "Instagram",
    "ORCID",
    "Mastodon",
    "StackOverflow",
    "ResearchGate",
    "YouTube",
    "Google Scholar",
    "Telegram",
    "Leetcode",
    "X",
]

available_social_networks = get_args(SocialNetworkName)

# ======================================================================================
# Create the models: ===================================================================
# ======================================================================================


class SocialNetwork(RenderCVBaseModelWithoutExtraKeys):
    """This class is the data model of a social network."""

    model_config = pydantic.ConfigDict(
        title="Social Network",
    )
    network: SocialNetworkName = pydantic.Field(
        title="Social Network",
    )
    username: str = pydantic.Field(
        title="Username",
        description=(
            "The username used in the social network. The link will be generated"
            " automatically."
        ),
    )

    @pydantic.field_validator("username")
    @classmethod
    def check_username(cls, username: str, info: pydantic.ValidationInfo) -> str:
        """Check if the username is provided correctly."""
        if "network" not in info.data:
            # the network is either not provided or not one of the available social
            # networks. In this case, don't check the username, since Pydantic will
            # raise an error for the network.
            return username

        network = info.data["network"]

        return validate_a_social_network_username(username, network)

    @pydantic.model_validator(mode="after")  # type: ignore
    def check_url(self) -> "SocialNetwork":
        """Validate the URL of the social network."""
        if self.network == "Mastodon":
            # All the other social networks have valid URLs. Mastodon URLs contain both
            # the username and the domain. So, we need to validate if the url is valid.
            validate_url(self.url)

        return self

    @functools.cached_property
    def url(self) -> str:
        """Return the URL of the social network and cache `url` as an attribute of the
        instance.
        """
        if self.network == "Mastodon":
            # Split domain and username
            _, username, domain = self.username.split("@")
            url = f"https://{domain}/@{username}"
        else:
            url_dictionary = {
                "LinkedIn": "https://linkedin.com/in/",
                "GitHub": "https://github.com/",
                "GitLab": "https://gitlab.com/",
                "IMDB": "https://imdb.com/name/",
                "Instagram": "https://instagram.com/",
                "ORCID": "https://orcid.org/",
                "StackOverflow": "https://stackoverflow.com/users/",
                "ResearchGate": "https://researchgate.net/profile/",
                "YouTube": "https://youtube.com/@",
                "Google Scholar": "https://scholar.google.com/citations?user=",
                "Telegram": "https://t.me/",
                "Leetcode": "https://leetcode.com/u/",
                "X": "https://x.com/",
            }
            url = url_dictionary[self.network] + self.username

        return url


class CurriculumVitae(RenderCVBaseModelWithExtraKeys):
    """This class is the data model of the `cv` field."""

    # ---------------------------------------------------------------------
    # Private attributes
    # ---------------------------------------------------------------------

    # Store the order of the keys in the YAML `cv` mapping so that the header
    # connections can be rendered in the same order that the user defines.
    _yaml_key_order: list[str] = pydantic.PrivateAttr(default_factory=list)

    # ---------------------------------------------------------------------
    # Model Validators
    # ---------------------------------------------------------------------

    @pydantic.model_validator(mode="before")
    @classmethod
    def _capture_yaml_key_order(cls, data: dict[str, Any]):  # type: ignore[override]
        """Capture the order of the keys in the YAML *before* validation.

        Pydantic gives us the raw input mapping during the *before* validation
        stage.  At this point the order of the keys is still exactly how the
        user wrote them in the YAML file (ruamel keeps the insertion order).
        We copy that order into a dedicated key so that it becomes available
        after validation.  The copied list is then assigned to a private
        attribute in an *after* validator.
        """

        # The input can be a `CommentedMap` which keeps insertion order.  We
        # convert to `dict` just in case but still preserve the order.
        if isinstance(data, dict):
            data["__yaml_key_order__"] = list(data.keys())

        return data

    @pydantic.model_validator(mode="after")  # type: ignore[override]
    def _populate_yaml_key_order(self):
        """Populate the private attribute that stores the YAML key order."""

        # `__yaml_key_order__` lives in the *extra* values (`__pydantic_extra__`)
        # because it is not a declared field.  Pop it if present.
        extra: dict[str, Any] | None = getattr(self, "__pydantic_extra__", None)

        if extra and "__yaml_key_order__" in extra:
            self._yaml_key_order = extra.pop("__yaml_key_order__")  # type: ignore[assignment]

        return self

    model_config = pydantic.ConfigDict(
        title="CV",
    )
    name: str | None = pydantic.Field(
        default=None,
        title="Name",
    )
    location: str | None = pydantic.Field(
        default=None,
        title="Location",
    )
    email: pydantic.EmailStr | None = pydantic.Field(
        default=None,
        title="Email",
    )
    photo: pathlib.Path | None = pydantic.Field(
        default=None,
        title="Photo",
        description="Path to the photo of the person, relative to the input file.",
    )
    phone: pydantic_phone_numbers.PhoneNumber | None = pydantic.Field(
        default=None,
        title="Phone",
        description=(
            "Country code should be included. For example, +1 for the United States."
        ),
    )
    website: pydantic.HttpUrl | None = pydantic.Field(
        default=None,
        title="Website",
    )
    social_networks: list[SocialNetwork] | None = pydantic.Field(
        default=None,
        title="Social Networks",
    )
    sections_input: Sections = pydantic.Field(
        default=None,
        title="Sections",
        description="The sections of the CV, like Education, Experience, etc.",
        # This is an alias to allow users to use `sections` in the YAML file:
        # `sections` key is preserved for RenderCV's internal use.
        alias="sections",
    )
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

    @pydantic.field_validator("name")
    @classmethod
    def update_curriculum_vitae(cls, value: str, info: pydantic.ValidationInfo) -> str:
        """Update the `curriculum_vitae` dictionary."""
        if value:
            curriculum_vitae[info.field_name] = value  # type: ignore

        return value

    @functools.cached_property
    def connections(self) -> list[dict[str, str | None]]:
        """Return all the connections of the person as a list of dictionaries and cache
        `connections` as an attribute of the instance. The connections are used in the
        header of the CV.

        Returns:
            The connections of the person.
        """
        # Helper functions to create each connection dictionary -----------------

        def _location_connection():
            return {
                "typst_icon": "location-dot",
                "url": None,
                "clean_url": None,
                "placeholder": self.location,
            }

        def _email_connection():
            return {
                "typst_icon": "envelope",
                "url": f"mailto:{self.email}",
                "clean_url": self.email,
                "placeholder": self.email,
            }

        def _phone_connection():
            phone_placeholder = computers.format_phone_number(self.phone) # type: ignore
            return {
                "typst_icon": "phone",
                "url": self.phone,
                "clean_url": phone_placeholder,
                "placeholder": phone_placeholder,
            }

        def _website_connection():
            website_placeholder = computers.make_a_url_clean(str(self.website))
            return {
                "typst_icon": "link",
                "url": str(self.website),
                "clean_url": website_placeholder,
                "placeholder": website_placeholder,
            }

        def _social_networks_connections():
            icon_dictionary = {
                "LinkedIn": "linkedin",
                "GitHub": "github",
                "GitLab": "gitlab",
                "IMDB": "imdb",
                "Instagram": "instagram",
                "Mastodon": "mastodon",
                "ORCID": "orcid",
                "StackOverflow": "stack-overflow",
                "ResearchGate": "researchgate",
                "YouTube": "youtube",
                "Google Scholar": "graduation-cap",
                "Telegram": "telegram",
                "Leetcode": "code",
                "X": "x-twitter",
            }

            connections_list: list[dict[str, str | None]] = []
            if self.social_networks is None:
                return connections_list

            for social_network in self.social_networks:
                clean_url = computers.make_a_url_clean(social_network.url)
                connection = {
                    "typst_icon": icon_dictionary[social_network.network],
                    "url": social_network.url,
                    "clean_url": clean_url,
                    "placeholder": social_network.username,
                }

                if social_network.network == "StackOverflow":
                    username = social_network.username.split("/")[1]
                    connection["placeholder"] = username
                if social_network.network == "Google Scholar":
                    connection["placeholder"] = "Google Scholar"
                if social_network.network == "IMDB":
                    connection["placeholder"] = "IMDB Profile"

                connections_list.append(connection)  # type: ignore[arg-type]

            return connections_list

        # ------------------------------------------------------------------
        # Build the connections list in the exact order of the YAML keys
        # ------------------------------------------------------------------

        key_to_handler = {
            "location": (self.location is not None, _location_connection),
            "email": (self.email is not None, _email_connection),
            "phone": (self.phone is not None, _phone_connection),
            "website": (self.website is not None, _website_connection),
            "social_networks": (self.social_networks is not None, _social_networks_connections),
        }

        connections: list[dict[str, str | None]] = []

        # Prefer the order captured from the YAML file. If, for any reason, it was
        # not captured, fall back to the traditional fixed ordering used before so
        # that existing behaviour remains unchanged.
        if self._yaml_key_order:
            ordered_keys = [key for key in self._yaml_key_order if key in key_to_handler]
        else:
            ordered_keys = list(key_to_handler.keys())

        for key in ordered_keys:
            present, handler = key_to_handler[key]
            if not present:
                continue
            if key == "social_networks":
                connections.extend(handler()) # type: ignore
            else:
                connections.append(handler())

        return connections

    @functools.cached_property
    def sections(self) -> list[SectionBase]:
        """Compute the sections of the CV based on the input sections.

        The original `sections` input is a dictionary where the keys are the section titles
        and the values are the list of entries in that section. This function converts the
        input sections to a list of `SectionBase` objects. This makes it easier to work with
        the sections in the rest of the code.

        Returns:
            The computed sections.
        """
        sections: list[SectionBase] = []

        if self.sections_input is not None:
            for title, entries in self.sections_input.items():
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


# The dictionary below will be overwritten by CurriculumVitae class, which will contain
# some important data for the CV.
curriculum_vitae: dict[str, str] = {}
