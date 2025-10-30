import pydantic

from .basis.entry import Entry
from .basis.entry_with_complex_fields import EntryWithComplexFields


class ExperienceEntryBase(Entry):
    company: str = pydantic.Field(
        examples=["Microsoft", "Google", "Princeton Plasma Physics Laboratory"],
    )
    position: str = pydantic.Field(
        examples=["Software Engineer", "Research Assistant", "Project Manager"],
    )


# This approach ensures ExperienceEntryBase keys appear first in the key order:
class ExperienceEntry(ExperienceEntryBase, EntryWithComplexFields):
    pass
