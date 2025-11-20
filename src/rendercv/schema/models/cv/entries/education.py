import pydantic

from .basis.entry import BaseEntry
from .basis.entry_with_complex_fields import BaseEntryWithComplexFields


class BaseEducationEntry(BaseEntry):
    institution: str = pydantic.Field(
        description="The name of the educational institution.",
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
        description="Degree type (e.g., BS, MS, PhD). Leave empty if not applicable.",
        examples=["BS", "BA", "PhD", "MS"],
    )


# This approach ensures EducationEntryBase keys appear first in the key order:
class EducationEntry(BaseEducationEntry, BaseEntryWithComplexFields):
    pass
