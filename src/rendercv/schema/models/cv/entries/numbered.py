import pydantic

from .bases.entry import BaseEntry


class NumberedEntry(BaseEntry):
    number: str = pydantic.Field(
        description=(
            "The numbered item text. Use this for ordered lists where you want"
            " numbering (e.g., publications, patents)."
        ),
        examples=["First publication about XYZ", "Patent for ABC technology"],
    )
