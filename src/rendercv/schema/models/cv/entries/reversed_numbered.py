import pydantic

from .bases.entry import BaseEntry


class ReversedNumberedEntry(BaseEntry):
    reversed_number: str = pydantic.Field(
        description=(
            "The text for a reverse-numbered list item. The numbering will be in"
            " reverse order (e.g., 5, 4, 3, 2, 1), useful for publications where you"
            " want the most recent items to have higher numbers."
        ),
        examples=["Latest research paper", "Recent patent application"],
    )
