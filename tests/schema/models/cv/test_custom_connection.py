import pydantic
import pytest

from rendercv.schema.models.cv.custom_connection import CustomConnection


def test_url_can_be_omitted() -> None:
    connection = CustomConnection(fontawesome_icon="phone", placeholder="Call me")
    assert connection.url is None
    assert connection.model_dump()["url"] is None


@pytest.mark.parametrize("url", [None, "https://example.com/"])
def test_explicit_url(url: str | None) -> None:
    connection = CustomConnection.model_validate(
        {"fontawesome_icon": "link", "placeholder": "Website", "url": url}
    )
    assert connection.model_dump(mode="json")["url"] == url


def test_invalid_url_is_rejected() -> None:
    with pytest.raises(pydantic.ValidationError):
        CustomConnection.model_validate(
            {"fontawesome_icon": "link", "placeholder": "Website", "url": "bad"}
        )
