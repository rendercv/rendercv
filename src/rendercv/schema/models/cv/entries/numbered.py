import pydantic

from .bases.entry import BaseEntry


class NumberedEntry(BaseEntry):
    number: str = pydantic.Field(
        examples=["First publication about XYZ", "Patent for ABC technology"],
    )
