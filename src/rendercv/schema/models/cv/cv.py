import functools
import pathlib
from typing import Any, Self

import pydantic
import pydantic_core
import pydantic_extra_types.phone_numbers as pydantic_phone_numbers

from ...context import get_input_file_path
from ...pydantic_error_handling import CustomPydanticErrorTypes
from ..base import BaseModelWithoutExtraKeys
from .section import BaseRenderCVSection, Section, get_rendercv_sections
from .social_network import SocialNetwork

email_validator = pydantic.TypeAdapter(pydantic.EmailStr)
emails_validator = pydantic.TypeAdapter(list[pydantic.EmailStr])
website_validator = pydantic.TypeAdapter(pydantic.HttpUrl)
websites_validator = pydantic.TypeAdapter(list[pydantic.HttpUrl])
phone_validator = pydantic.TypeAdapter(pydantic_phone_numbers.PhoneNumber)
phones_validator = pydantic.TypeAdapter(list[pydantic_phone_numbers.PhoneNumber])


class Cv(BaseModelWithoutExtraKeys):
    name: str | None = pydantic.Field(
        default=None,
        description="Your full name as you want it to appear on your CV.",
        examples=["John Doe", "Jane Smith"],
    )
    location: str | None = pydantic.Field(
        default=None,
        description=(
            "Your location (city, state/country, or full address). This appears in your"
            " CV header."
        ),
        examples=["New York, NY", "London, UK", "Istanbul, Türkiye"],
    )
    email: pydantic.EmailStr | list[pydantic.EmailStr] | None = pydantic.Field(
        default=None,
        description=(
            "Your email address. Multiple email addresses may be provided as a list."
        ),
        examples=[
            "john.doe@example.com",
            ["john.doe.1@example.com", "john.doe.2@example.com"],
        ],
    )
    photo: pathlib.Path | None = pydantic.Field(
        default=None,
        description=(
            "Path to your photo file, relative to your CV YAML file. The photo will"
            " appear in your CV header."
        ),
        examples=["photo.jpg", "images/profile.png"],
    )
    phone: (
        pydantic_phone_numbers.PhoneNumber
        | list[pydantic_phone_numbers.PhoneNumber]
        | None
    ) = pydantic.Field(
        default=None,
        description=(
            "Your phone number with country code. Use international format starting"
            " with '+' (e.g., +1 for USA, +44 for UK). Multiple phone numbers may be"
            " provided as a list."
        ),
        examples=[
            "+1-234-567-8900",
            ["+1-234-567-8900", "+44 20 1234 5678"],
        ],
    )
    website: pydantic.HttpUrl | list[pydantic.HttpUrl] | None = pydantic.Field(
        default=None,
        description=(
            "Your personal website or portfolio URL. Multiple websites may be provided"
            " as a list."
        ),
        examples=[
            "https://johndoe.com",
            ["https://johndoe.com", "https://www.janesmith.dev"],
        ],
    )
    social_networks: list[SocialNetwork] | None = pydantic.Field(
        default=None,
        description=(
            "List of your social network profiles (e.g., LinkedIn, GitHub). These"
            " appear as clickable links in your CV header."
        ),
    )
    sections: dict[str, Section] | None = pydantic.Field(
        default=None,
        description=(
            "The sections of your CV (e.g., Experience, Education, Projects). The keys"
            " are section titles, and the values are lists of entries. Entries are"
            " automatically typed based on their fields."
        ),
        examples=[
            {
                "Experience": "...",
                "Education": "...",
                "Projects": "...",
                "Skills": "...",
            }
        ],
    )

    # Store the order of the keys so that the header can be rendered in the same order
    # that the user defines.
    _key_order: list[str] = pydantic.PrivateAttr(default_factory=list)

    @pydantic.field_validator("photo")
    @classmethod
    def update_photo_path(
        cls, value: pathlib.Path | None, info: pydantic.ValidationInfo
    ) -> pathlib.Path | None:
        if value:
            if not value.is_absolute():
                input_file_path = get_input_file_path(info)
                value = input_file_path / str(value)

            if not value.exists():
                raise pydantic_core.PydanticCustomError(
                    CustomPydanticErrorTypes.other.value,
                    "The photo file `{photo_file}` does not exist.",
                    {"photo_file": value.absolute()},
                )

        return value

    @functools.cached_property
    def rendercv_sections(self) -> list[BaseRenderCVSection]:
        return get_rendercv_sections(self.sections)

    @pydantic.model_validator(mode="wrap")
    @classmethod
    def capture_input_order(
        cls, data: Any, handler: pydantic.ModelWrapValidatorHandler[Self]
    ) -> "Cv":
        # Capture the input order before validation
        key_order = list(data.keys()) if isinstance(data, dict) else []

        # Let Pydantic do its validation
        instance = handler(data)

        # Set the private attribute on the instance:
        # If the values of those keys are None, remove the key from the key_order
        instance._key_order = [key for key in key_order if data.get(key) is not None]

        return instance

    @pydantic.field_validator("website", "email", "phone", mode="plain")
    @classmethod
    def validate_list_or_scalar_fields(
        cls, value: Any, info: pydantic.ValidationInfo
    ) -> (
        pydantic.EmailStr
        | pydantic.HttpUrl
        | pydantic_phone_numbers.PhoneNumber
        | list[pydantic.EmailStr]
        | list[pydantic.HttpUrl]
        | list[pydantic_phone_numbers.PhoneNumber]
    ):
        """We have this custom plain validator to have better error messages. For
        example, we don't want to raise regular email validation error, when the input
        is clearly a list."""
        assert info.field_name is not None
        validators: tuple[
            pydantic.TypeAdapter[pydantic.EmailStr]
            | pydantic.TypeAdapter[pydantic.HttpUrl]
            | pydantic.TypeAdapter[pydantic_phone_numbers.PhoneNumber],
            (
                pydantic.TypeAdapter[list[pydantic.EmailStr]]
                | pydantic.TypeAdapter[list[pydantic.HttpUrl]]
                | pydantic.TypeAdapter[list[pydantic_phone_numbers.PhoneNumber]]
            ),
        ] = {
            "website": (website_validator, websites_validator),
            "email": (email_validator, emails_validator),
            "phone": (phone_validator, phones_validator),
        }[info.field_name]

        if isinstance(value, list):
            return validators[1].validate_python(value)
        if isinstance(value, str):
            return validators[0].validate_strings(value)
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "`{field_name}` must be provided as a string or a list of strings.",
            {"field_name": info.field_name},
        )

    @pydantic.field_serializer("phone")
    def serialize_phone(
        self, phone: pydantic_phone_numbers.PhoneNumber | None
    ) -> str | None:
        if phone is not None:
            return phone.replace("tel:", "")

        return phone
