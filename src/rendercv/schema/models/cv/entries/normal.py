import pydantic

from .bases.entry import BaseEntry
from .bases.entry_with_complex_fields import BaseEntryWithComplexFields


class BaseNormalEntry(BaseEntry):
    name: str = pydantic.Field(
        examples=["Some Project", "Some Event", "Some Award"],
    )


# This approach ensures NormalEntryBase keys appear first in the key order:
class NormalEntry(BaseEntryWithComplexFields, BaseNormalEntry):
    pass
