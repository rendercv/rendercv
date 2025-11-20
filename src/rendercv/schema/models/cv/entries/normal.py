import pydantic

from .basis.entry import BaseEntry
from .basis.entry_with_complex_fields import BaseEntryWithComplexFields


class BaseNormalEntry(BaseEntry):
    name: str = pydantic.Field(
        description="The name of the entry, such as `Some Project`, `Some Event`, etc.",
        examples=["Some Project", "Some Event", "Some Award"],
    )


# This approach ensures NormalEntryBase keys appear first in the key order:
class NormalEntry(BaseNormalEntry, BaseEntryWithComplexFields):
    pass
