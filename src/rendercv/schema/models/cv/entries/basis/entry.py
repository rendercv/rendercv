import pydantic

from ....base import BaseModelWithExtraKeys


class BaseEntry(BaseModelWithExtraKeys):
    """Parent class for all the entry types. It's not an entry type itself.

    It is used to ensure all the entry types use `BaseModelWithExtraKeys` as the
    parent class. Also, other things can be added to all the entry types in the future.
    """

    model_config = pydantic.ConfigDict(json_schema_extra={"description": None})
