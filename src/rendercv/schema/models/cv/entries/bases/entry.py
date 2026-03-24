import functools
import re

import pydantic

from ....base import BaseModelWithExtraKeys

entry_type_to_snake_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


class BaseEntry(BaseModelWithExtraKeys):
    """Base class for all CV entry types.

    Why:
        All entry types share common configuration (extra keys allowed for
        template fields, JSON schema description suppressed). This base
        provides the shared config and entry type introspection.
    """

    model_config = pydantic.ConfigDict(json_schema_extra={"description": None})

    @functools.cached_property
    def entry_type_in_snake_case(self) -> str:
        """Convert class name to snake_case for template attribute lookup.

        Why:
            Template collections store entry templates keyed by snake_case
            entry type names (e.g., ``education_entry``). This property
            enables dynamic lookup from the class name.

        Returns:
            Snake_case version of the entry class name.
        """
        return entry_type_to_snake_case_pattern.sub(
            "_", self.__class__.__name__
        ).lower()
