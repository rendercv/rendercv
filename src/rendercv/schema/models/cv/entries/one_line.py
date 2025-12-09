import pydantic

from .bases.entry import BaseEntry


class OneLineEntry(BaseEntry):
    label: str = pydantic.Field(
        examples=["Languages", "Citizenship", "Security Clearance"],
    )
    details: str = pydantic.Field(
        examples=["English (native), Spanish (fluent)", "US Citizen", "Top Secret"],
    )
