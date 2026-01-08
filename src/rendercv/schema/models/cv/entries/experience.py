import pydantic

from .bases.entry import BaseEntry
from .bases.entry_with_complex_fields import BaseEntryWithComplexFields
from .skill_icons import SkillIcons


class BaseExperienceEntry(BaseEntry):
    company: str = pydantic.Field(
        examples=["Microsoft", "Google", "Princeton Plasma Physics Laboratory"],
    )
    position: str = pydantic.Field(
        examples=["Software Engineer", "Research Assistant", "Project Manager"],
    )
    skillicons: SkillIcons | None = pydantic.Field(
        default=None,
        description=(
            "Optional skill icons to display with the entry. Icons are fetched from"
            " https://skillicons.dev/. Specify icon names, theme, size, etc."
        ),
        examples=[
            {"icons": "python,js,ts", "theme": "dark", "size": 24},
        ],
    )


# This approach ensures ExperienceEntryBase keys appear first in the key order:
class ExperienceEntry(BaseEntryWithComplexFields, BaseExperienceEntry):
    pass
