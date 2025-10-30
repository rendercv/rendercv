import pydantic

from .basis.complex_entry import ComplexEntry
from .basis.entry import Entry


class EducationEntryBase(Entry):
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


class EducationEntry(EducationEntryBase, ComplexEntry):
    pass
