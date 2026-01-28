import pydantic

from .bases.entry import BaseEntry


class ReversedNumberedEntry(BaseEntry):
    reversed_number: str = pydantic.Field(
        description=(
            "Reverse-numbered list item. Numbering goes in reverse (5, 4, 3, 2, 1),"
            " making recent items have higher numbers."
        ),
        examples=["Latest research paper", "Recent patent application"],
    )
