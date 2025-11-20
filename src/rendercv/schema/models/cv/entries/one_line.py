import pydantic

from .basis.entry import BaseEntry


class OneLineEntry(BaseEntry):
    label: str = pydantic.Field(
        description="The label/heading for this item (e.g., a category or field name).",
        examples=["Languages", "Citizenship", "Security Clearance"],
    )
    details: str = pydantic.Field(
        description="The details/value for this item.",
        examples=["English (native), Spanish (fluent)", "US Citizen", "Top Secret"],
    )
