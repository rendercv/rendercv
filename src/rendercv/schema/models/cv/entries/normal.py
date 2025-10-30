import pydantic

from .basis.complex_entry import ComplexEntry
from .basis.entry import Entry


class NormalEntryBase(Entry):
    name: str = pydantic.Field(
        description="The name of the entry, such as Some Project, Some Event, etc.",
        examples=["Some Project", "Some Event", "Some Award"],
    )


class NormalEntry(NormalEntryBase, ComplexEntry):
    pass
