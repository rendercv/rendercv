import pydantic

from .bases.entry import BaseEntry
from .bases.entry_with_complex_fields import BaseEntryWithComplexFields


class BaseEducationEntry(BaseEntry):
    """Education entry fields without date and complex fields.

    Why:
        Separating education-specific fields (institution, area, degree) from
        date/location fields enables EducationEntry to inherit from both this
        class and BaseEntryWithComplexFields, controlling field ordering in
        the final model so institution/area/degree appear before dates.
    """

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
