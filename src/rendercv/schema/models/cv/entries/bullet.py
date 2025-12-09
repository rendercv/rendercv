import pydantic

from .bases.entry import BaseEntry


class BulletEntry(BaseEntry):
    bullet: str = pydantic.Field(
        examples=["Python, JavaScript, C++", "Excellent communication skills"],
    )
