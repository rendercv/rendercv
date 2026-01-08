import pydantic

from .bases.entry import BaseEntry
from .bases.entry_with_complex_fields import BaseEntryWithComplexFields
from .skill_icons import SkillIcons


class BaseNormalEntry(BaseEntry):
    name: str = pydantic.Field(
        examples=["Some Project", "Some Event", "Some Award"],
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


# This approach ensures NormalEntryBase keys appear first in the key order:
class NormalEntry(BaseEntryWithComplexFields, BaseNormalEntry):
    pass
