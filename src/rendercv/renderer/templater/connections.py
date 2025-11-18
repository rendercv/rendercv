from typing import TypedDict

import phonenumbers
import pydantic

from rendercv.schema.models.rendercv_model import RenderCVModel


class Connection(TypedDict):
    icon_specifier: str
    url: str | None
    body: str


def compute_connections(rendercv_model: RenderCVModel) -> list[Connection]:
    connections: list[Connection] = []
    for key in rendercv_model.cv._key_order:
        match key:
            case "email":
                url = f"mailto:{rendercv_model.cv.email}"
                body = str(rendercv_model.cv.email)
            case "phone":
                assert rendercv_model.cv.phone
                url = str(rendercv_model.cv.phone)
                body = phonenumbers.format_number(
                    phonenumbers.parse(rendercv_model.cv.phone, None),
                    getattr(
                        phonenumbers.PhoneNumberFormat,
                        rendercv_model.locale.phone_number_format.upper(),
                    ),
                )
            case "website":
                assert rendercv_model.cv.website
                url = str(rendercv_model.cv.website)
                body = clean_url(rendercv_model.cv.website)
            case "location":
                url = None
                body = str(rendercv_model.cv.location)
            case _:
                continue

        connections.append(Connection(icon_specifier=key, url=url, body=body))

    if rendercv_model.cv.social_networks:
        for social_network in rendercv_model.cv.social_networks:
            url = social_network.url
            body = social_network.username
            connections.append(
                Connection(icon_specifier=social_network.network, url=url, body=body)
            )

    return connections


def clean_url(url: str | pydantic.HttpUrl) -> str:
    """Make a URL clean by removing the protocol, www, and trailing slashes.

    Example:
        ```python
        make_a_url_clean("https://www.example.com/")
        ```
        returns
        `"example.com"`

    Args:
        url: The URL to make clean.

    Returns:
        The clean URL.
    """
    url = str(url).replace("https://", "").replace("http://", "")
    if url.endswith("/"):
        url = url[:-1]

    return url


typst_fa_icons = {
    "LinkedIn": "linkedin",
    "GitHub": "github",
    "GitLab": "gitlab",
    "IMDB": "imdb",
    "Instagram": "instagram",
    "Mastodon": "mastodon",
    "ORCID": "orcid",
    "StackOverflow": "stack-overflow",
    "ResearchGate": "researchgate",
    "YouTube": "youtube",
    "Google Scholar": "graduation-cap",
    "Telegram": "telegram",
    "Leetcode": "code",
    "X": "x-twitter",
    "location": "location-dot",
    "email": "envelope",
    "phone": "phone",
    "website": "link",
}


def compute_typst_connections(rendercv_model: RenderCVModel) -> list[str]:
    connections = compute_connections(rendercv_model)

    use_icon = rendercv_model.design.header.use_icons_for_connections
    make_links = rendercv_model.design.header.make_connections_links

    placeholders = [
        (
            f"#connection-with-icon({typst_fa_icons[icon_specifier]}, {body})"
            if use_icon
            else body
        )
        for icon_specifier, _, body in connections
    ]

    return [
        (
            f"#link({connection['url']}, {placeholder}, icon: false)"
            if connection["url"] and make_links
            else placeholder
        )
        for connection, placeholder in zip(connections, placeholders, strict=True)
    ]


def compute_markdown_connections(rendercv_model: RenderCVModel) -> list[str]:
    connections = compute_connections(rendercv_model)

    return [
        (
            f"[{connection['body']}]({connection['url']})"
            if connection["url"]
            else connection["body"]
        )
        for connection in connections
    ]
