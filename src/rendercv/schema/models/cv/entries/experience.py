import pydantic

from .basis.complex_entry import ComplexEntry
from .basis.entry import Entry


class ExperienceEntryBase(Entry):
    company: str = pydantic.Field(
        examples=["Microsoft", "Google", "Princeton Plasma Physics Laboratory"],
    )
    position: str = pydantic.Field(
        examples=["Software Engineer", "Research Assistant", "Project Manager"],
    )


class ExperienceEntry(ExperienceEntryBase, ComplexEntry):
    pass
