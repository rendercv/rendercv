from .basis.complex_entry import ComplexEntry
from .basis.entry import Entry


class ExperienceEntryBase(Entry):
    company: str
    position: str


class ExperienceEntry(ExperienceEntryBase, ComplexEntry):
    pass
