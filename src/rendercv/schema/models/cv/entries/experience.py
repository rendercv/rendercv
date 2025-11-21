import pydantic

from .bases.entry import BaseEntry
from .bases.entry_with_complex_fields import BaseEntryWithComplexFields


class BaseExperienceEntry(BaseEntry):
    company: str = pydantic.Field(
        description="Name of the company or organization.",
        examples=["Microsoft", "Google", "Princeton Plasma Physics Laboratory"],
    )
    position: str = pydantic.Field(
        description="Job title or role at the company.",
        examples=["Software Engineer", "Research Assistant", "Project Manager"],
    )


# This approach ensures ExperienceEntryBase keys appear first in the key order:
class ExperienceEntry(BaseExperienceEntry, BaseEntryWithComplexFields):
    pass
