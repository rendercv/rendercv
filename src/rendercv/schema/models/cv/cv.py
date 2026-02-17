import functools
from typing import Any, Self

import pydantic
import pydantic_extra_types.phone_numbers as pydantic_phone_numbers

from rendercv.exception import RenderCVInternalError

from ..base import BaseModelWithExtraKeys
from ..path import ExistingPathRelativeToInput
from .custom_connection import CustomConnection
from .section import BaseRenderCVSection, Section, get_rendercv_sections
from .social_network import SocialNetwork

email_validator = pydantic.TypeAdapter[pydantic.EmailStr](pydantic.EmailStr)
emails_validator = pydantic.TypeAdapter[list[pydantic.EmailStr]](list[pydantic.EmailStr])
website_validator = pydantic.TypeAdapter[pydantic.HttpUrl](pydantic.HttpUrl)
websites_validator = pydantic.TypeAdapter[list[pydantic.HttpUrl]](list[pydantic.HttpUrl])
phone_validator = pydantic.TypeAdapter[pydantic_phone_numbers.PhoneNumber](pydantic_phone_numbers.PhoneNumber)
phones_validator = pydantic.TypeAdapter[list[pydantic_phone_numbers.PhoneNumber]](list[pydantic_phone_numbers.PhoneNumber])


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
        description="You can provide multiple emails as a list.",
        examples=[
            "john.doe@example.com",
            ["john.doe.1@example.com", "john.doe.2@example.com"],
        ],
    )
    photo: ExistingPathRelativeToInput | None = pydantic.Field(
        default=None,
        description="Photo file path, relative to the YAML file.",
        examples=["photo.jpg", "images/profile.png"],
    )
    phone: (
        pydantic_phone_numbers.PhoneNumber
        | list[pydantic_phone_numbers.PhoneNumber]
        | None
    ) = pydantic.Field(
        default=None,
        description=(
            "Your phone number with country code in international format (e.g., +1 for"
            " USA, +44 for UK). The display format in the output is controlled by"
            " `design.header.connections.phone_number_format`. You can provide multiple"
            " numbers as a list."
        ),
        examples=[
            "+1-234-567-8900",
            ["+1-234-567-8900", "+44 20 1234 5678"],
        ],
    )
    website: pydantic.HttpUrl | list[pydantic.HttpUrl] | None = pydantic.Field(
        default=None,
        description="You can provide multiple URLs as a list.",
        examples=[
            "https://johndoe.com",
            ["https://johndoe.com", "https://www.janesmith.dev"],
        ],
    )
    social_networks: list[SocialNetwork] | None = pydantic.Field(
        default=None,
    )
    custom_connections: list[CustomConnection] | None = pydantic.Field(
        default=None,
        description=(
            "Additional header connections you define yourself. Each item has a"
            " `placeholder` (the displayed text), an optional `url`, and the Font"
            " Awesome icon name to render (from https://fontawesome.com/search)."
        ),
        examples=[
            [
                {
                    "placeholder": "Book a call",
                    "url": "https://cal.com/johndoe",
                    "fontawesome_icon": "calendar-days",
                }
            ],
        ],
    )
    sections: dict[str, Section] | None = pydantic.Field(
        default=None,
        description=(
            "The sections of your CV. Keys are section titles (e.g., Experience,"
            " Education), and values are lists of entries. Entry types are"
            " automatically detected based on their fields."
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
        """Transform user's section dict to list of typed section objects.

        Why:
            Templates need sections as list with title/entry_type metadata.
            Cached property computes once after validation, enabling repeated
            template access without recomputation.

        Returns:
            List of section objects for template rendering.
        """
        return get_rendercv_sections(self.sections)

    @pydantic.model_validator(mode="wrap")  # ty: ignore[invalid-argument-type]
    @classmethod
    def capture_input_order(
        cls, data: Any, handler: pydantic.ModelWrapValidatorHandler[Self]
    ) -> "Cv":
        """Preserve YAML field order for header rendering.

        Why:
            Header fields (name, label, location, etc.) must render in user-defined
            order, not alphabetical. Wrap validator captures dict key order before
            Pydantic reorders fields.

        Args:
            data: Raw input data before validation.
            handler: Pydantic's validation handler.

        Returns:
            Validated CV instance with _key_order preserved.
        """
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
        """Validate fields that accept single value or list with type-specific errors.

        Why:
            Users provide either `email: "x@y.com"` or `email: ["x@y.com", "a@b.com"]`.
            Plain mode validator detects list vs scalar first, enabling specific error
            messages like "invalid email in list" instead of generic validation errors.

        Args:
            value: Single value or list to validate.
            info: Validation context containing field name.

        Returns:
            Validated single value or list.
        """
        # Allow None values since these fields are optional
        if value is None:
            return None

        if info.field_name is None:
            raise RenderCVInternalError("field_name is None in validator")

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

        return validators[0].validate_python(value)

    @pydantic.field_serializer("phone")
    def serialize_phone(
        self, phone: pydantic_phone_numbers.PhoneNumber | None
    ) -> str | None:
        """Remove tel: prefix from phone number for clean serialization.

        Why:
            phone number library adds "tel:" URI scheme for validation.
            Serialization strips prefix so templates render plain numbers.

        Args:
            phone: Validated phone number with tel: prefix.

        Returns:
            Phone string without tel: prefix, or None.
        """
        if phone is not None:
            return phone.replace("tel:", "")

        return phone
