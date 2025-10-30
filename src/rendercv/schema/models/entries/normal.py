from .basis.complex_entry import ComplexEntry
from .basis.entry import Entry


class NormalEntryBase(Entry):
    name: str


class NormalEntry(NormalEntryBase, ComplexEntry):
    pass
