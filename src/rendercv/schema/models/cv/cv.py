import functools
from typing import Any, Self

import pydantic
import pydantic_core
import pydantic_extra_types.phone_numbers as pydantic_phone_numbers

from ...pydantic_error_handling import CustomPydanticErrorTypes
from ..base import BaseModelWithExtraKeys
from ..path import ExistingInputRelativePath
from .section import BaseRenderCVSection, Section, get_rendercv_sections
from .social_network import SocialNetwork

email_validator = pydantic.TypeAdapter(pydantic.EmailStr)
emails_validator = pydantic.TypeAdapter(list[pydantic.EmailStr])
website_validator = pydantic.TypeAdapter(pydantic.HttpUrl)
websites_validator = pydantic.TypeAdapter(list[pydantic.HttpUrl])
phone_validator = pydantic.TypeAdapter(pydantic_phone_numbers.PhoneNumber)
phones_validator = pydantic.TypeAdapter(list[pydantic_phone_numbers.PhoneNumber])


class Cv(BaseModelWithExtraKeys):
    name: str | None = pydantic.Field(
        default=None,
        examples=["John Doe", "Jane Smith"],
    )
    headline: str | None = pydantic.Field(
        default=None,
        examples=["Software Engineer", "Data Scientist", "Product Manager"],
    )
    location: str | None = pydantic.Field(
        default=None,
        examples=["New York, NY", "London, UK", "Istanbul, Türkiye"],
    )
    email: pydantic.EmailStr | list[pydantic.EmailStr] | None = pydantic.Field(
        default=None,
        description=(
            "Accepts either a single email address (string) or a list of email"
            " addresses."
        ),
        examples=[
            "john.doe@example.com",
            ["john.doe.1@example.com", "john.doe.2@example.com"],
        ],
    )
    photo: ExistingInputRelativePath | None = pydantic.Field(
        default=None,
        description="Path to the photo file, relative to the input YAML file.",
        examples=["photo.jpg", "images/profile.png"],
    )
    phone: (
        pydantic_phone_numbers.PhoneNumber
        | list[pydantic_phone_numbers.PhoneNumber]
        | None
    ) = pydantic.Field(
        default=None,
        description=(
            "Phone number with country code. Use international format starting"
            " with '+' (e.g., +1 for USA, +44 for UK). Accepts either a single phone"
            " number as a string or a list of phone numbers."
        ),
        examples=[
            "+1-234-567-8900",
            ["+1-234-567-8900", "+44 20 1234 5678"],
        ],
    )
    website: pydantic.HttpUrl | list[pydantic.HttpUrl] | None = pydantic.Field(
        default=None,
        description=(
            "Personal website or portfolio URL. Accepts either a single website URL as"
            " as a list."
        ),
        examples=[
            "https://johndoe.com",
            ["https://johndoe.com", "https://www.janesmith.dev"],
        ],
    )
    social_networks: list[SocialNetwork] | None = pydantic.Field(
        default=None,
        description="List of social network profiles (e.g., LinkedIn, GitHub).",
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

    @functools.cached_property
    def rendercv_sections(self) -> list[BaseRenderCVSection]:
        return get_rendercv_sections(self.sections)

    @pydantic.model_validator(mode="wrap")
    @classmethod
    def capture_input_order(
        cls, data: Any, handler: pydantic.ModelWrapValidatorHandler[Self]
    ) -> "Cv":
        # If data is already a Cv instance, preserve its _key_order
        if isinstance(data, cls):
            return data

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
        | None
    ):
        """We have this custom plain validator to have better error messages. For
        example, we don't want to raise regular email validation error, when the input
        is clearly a list."""
        # Allow None values since these fields are optional
        if value is None:
            return None

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
