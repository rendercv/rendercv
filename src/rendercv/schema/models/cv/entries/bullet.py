import pydantic

from .basis.entry import BaseEntry


class BulletEntry(BaseEntry):
    bullet: str = pydantic.Field(
        description=(
            "A single bullet point to display. Use this for simple lists of items like"
            " skills, technologies, or brief statements."
        ),
        examples=["Python, JavaScript, C++", "Excellent communication skills"],
    )
