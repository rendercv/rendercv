import pydantic

from .bases.entry import BaseEntry
from .bases.entry_with_complex_fields import BaseEntryWithComplexFields


class BaseEducationEntry(BaseEntry):
    institution: str = pydantic.Field(
        examples=["Boğaziçi University", "MIT", "Harvard University"],
    )
    area: str = pydantic.Field(
        description="Field of study or major.",
        examples=[
            "Mechanical Engineering",
            "Computer Science",
            "Electrical Engineering",
        ],
    )
    degree: str | None = pydantic.Field(
        default=None,
        examples=["BS", "BA", "PhD", "MS"],
    )


# This approach ensures EducationEntryBase keys appear first in the key order:
class EducationEntry(BaseEntryWithComplexFields, BaseEducationEntry):
    pass
