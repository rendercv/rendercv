import pydantic

from .basis.complex_entry import ComplexEntry
from .basis.entry import Entry


class EducationEntryBase(Entry):
    institution: str
    area: str
    degree: str | None = pydantic.Field(
        default=None,
        description="The type of the degree, such as BS, BA, PhD, MS.",
        examples=["BS", "BA", "PhD", "MS"]
    )
    grade: str | None = pydantic.Field(
        default=None,
        examples=["GPA: 3.00/4.00"],
    )


class EducationEntry(EducationEntryBase, ComplexEntry):
    pass
