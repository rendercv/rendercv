import pydantic

from ..base import BaseModelWithoutExtraKeys


class CustomConnection(BaseModelWithoutExtraKeys):
    fontawesome_icon: str
    placeholder: str
    url: pydantic.HttpUrl | None
