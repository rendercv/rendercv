import pydantic

from .bases.entry import BaseEntry


class BulletEntry(BaseEntry):
    """Single bullet point entry for simple list items.

    Why:
        Some sections contain standalone bullet points without dates or
        institutions. This minimal entry type captures just the text content.
    """

    bullet: str = pydantic.Field(
        examples=["Python, JavaScript, C++", "Excellent communication skills"],
    )
