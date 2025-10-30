import pydantic

from .basis.entry import Entry
from .basis.entry_with_complex_fields import EntryWithComplexFields


class NormalEntryBase(Entry):
    name: str = pydantic.Field(
        description="The name of the entry, such as Some Project, Some Event, etc.",
        examples=["Some Project", "Some Event", "Some Award"],
    )


# This approach ensures NormalEntryBase keys appear first in the key order:
class NormalEntry(NormalEntryBase, EntryWithComplexFields):
    pass
