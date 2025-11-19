from typing import Literal, TypedDict

import phonenumbers
import pydantic

from rendercv.schema.models.rendercv_model import RenderCVModel


class Connection(TypedDict):
    icon_specifier: str
    url: str | None
    body: str


def parse_connections(rendercv_model: RenderCVModel) -> list[Connection]:
    connections: list[Connection] = []
    for key in rendercv_model.cv._key_order:
        match key:
            case "email":
                emails = rendercv_model.cv.email
                if not isinstance(emails, list):
                    emails = [emails]

                for email in emails:
                    url = f"mailto:{email}"
                    body = str(email)
                    connections.append(
                        Connection(icon_specifier=key, url=url, body=body)
                    )

            case "phone":
                phones = rendercv_model.cv.phone
                assert phones is not None
                if not isinstance(phones, list):
                    phones = [phones]

                for phone in phones:
                    url = str(rendercv_model.cv.phone)
                    body = phonenumbers.format_number(
                        phonenumbers.parse(phone, None),
                        getattr(
                            phonenumbers.PhoneNumberFormat,
                            rendercv_model.locale.phone_number_format.upper(),
                        ),
                    )
                    connections.append(
                        Connection(icon_specifier=key, url=url, body=body)
                    )

            case "website":
                websites = rendercv_model.cv.website
                assert websites
                if not isinstance(websites, list):
                    websites = [websites]

                for website in websites:
                    url = str(website)
                    body = clean_url(website)
                    connections.append(
                        Connection(icon_specifier=key, url=url, body=body)
                    )

            case "location":
                url = None
                body = str(rendercv_model.cv.location)
                connections.append(Connection(icon_specifier=key, url=None, body=body))

            case _:
                continue

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


def compute_connections_for_typst(rendercv_model: RenderCVModel) -> list[str]:
    connections = parse_connections(rendercv_model)

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


def compute_connections_for_markdown(rendercv_model: RenderCVModel) -> list[str]:
    connections = parse_connections(rendercv_model)

    return [
        (
            f"[{connection['body']}]({connection['url']})"
            if connection["url"]
            else connection["body"]
        )
        for connection in connections
    ]


def compute_connections(
    rendercv_model: RenderCVModel, file_type: Literal["typst", "markdown"]
) -> list[str]:
    return {
        "typst": compute_connections_for_typst,
        "markdown": compute_connections_for_markdown,
    }[file_type](rendercv_model)
