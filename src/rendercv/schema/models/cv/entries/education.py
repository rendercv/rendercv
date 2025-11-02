import pydantic

from .basis.entry import BaseEntry
from .basis.entry_with_complex_fields import BaseEntryWithComplexFields


class BaseEducationEntry(BaseEntry):
    institution: str = pydantic.Field(
        examples=["Boğaziçi University", "MIT", "Harvard University"],
    )
    area: str = pydantic.Field(
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
class EducationEntry(BaseEducationEntry, BaseEntryWithComplexFields):
    pass
