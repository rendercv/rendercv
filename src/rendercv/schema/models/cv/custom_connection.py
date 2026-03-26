import pydantic

from ..base import BaseModelWithoutExtraKeys


class CustomConnection(BaseModelWithoutExtraKeys):
    """User-defined contact method with custom icon and URL.

    Why:
        Built-in social networks cover common platforms, but users need
        arbitrary contact methods (personal websites, custom platforms).
        CustomConnection provides a FontAwesome icon, display text, and
        optional URL for any contact channel.
    """

    fontawesome_icon: str
    placeholder: str
    url: pydantic.HttpUrl | None
