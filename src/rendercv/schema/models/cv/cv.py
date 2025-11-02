import functools
import importlib
import pathlib
from typing import Any, Self

import pydantic
import pydantic_extra_types.phone_numbers as pydantic_phone_numbers

from ..base import BaseModelWithoutExtraKeys
from .section import Section, get_sections_rendercv
from .social_network import SocialNetwork


class Cv(BaseModelWithoutExtraKeys):
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
    sections: dict[str, Section] | None = None

    # Store the order of the keys so that the header can be rendered in the same order
    # that the user defines.
    _key_order: list[str] = pydantic.PrivateAttr(default_factory=list)

    @pydantic.field_validator("photo")
    @classmethod
    def update_photo_path(cls, value: pathlib.Path | None) -> pathlib.Path | None:
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
    def sections_rendercv(self) -> list[Section]:
        return get_sections_rendercv(self.sections)

    @pydantic.model_validator(mode="wrap")
    @classmethod
    def capture_input_order(
        cls, data: Any, handler: pydantic.ModelWrapValidatorHandler[Self]
    ) -> "Cv":
        # Capture the input order before validation
        key_order = list(data.keys()) if isinstance(data, dict) else []

        # Let Pydantic do its validation
        instance = handler(data)

        # Set the private attribute on the instance
        instance._key_order = key_order

        return instance

    @pydantic.field_serializer("phone")
    def serialize_phone(
        self, phone: pydantic_phone_numbers.PhoneNumber | None
    ) -> str | None:
        if phone is not None:
            return phone.replace("tel:", "")

        return phone
