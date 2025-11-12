"""Base for all entry types. Allows custom fields via BaseModelWithExtraKeys."""

import pydantic

from ....base import BaseModelWithExtraKeys


class BaseEntry(BaseModelWithExtraKeys):
    """Parent class for all entry types. Permits custom user fields."""

    model_config = pydantic.ConfigDict(json_schema_extra={"description": None})
