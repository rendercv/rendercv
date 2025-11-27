import functools
import re

import pydantic

from ....base import BaseModelWithExtraKeys

entry_type_to_snake_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


class BaseEntry(BaseModelWithExtraKeys):
    model_config = pydantic.ConfigDict(json_schema_extra={"description": None})

    @functools.cached_property
    def entry_type_in_snake_case(self) -> str:
        return entry_type_to_snake_case_pattern.sub(
            "_", self.__class__.__name__
        ).lower()
