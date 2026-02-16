from dataclasses import dataclass
from typing import Literal

import phonenumbers

from rendercv.exception import RenderCVInternalError
from rendercv.schema.models.rendercv_model import RenderCVModel

from .markdown_parser import markdown_to_typst
from .string_processor import clean_url

fontawesome_icons = {
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
    "WhatsApp": "whatsapp",
    "Leetcode": "code",
    "X": "x-twitter",
    "Bluesky": "bluesky",
    "location": "location-dot",
    "email": "envelope",
    "phone": "phone",
    "website": "link",
    "Reddit": "reddit",
}


def compute_connections(
    rendercv_model: RenderCVModel, file_type: Literal["typst", "markdown"]
) -> list[str]:
    """Route to format-specific connection generator.

    Args:
        rendercv_model: CV model with contact information.
        file_type: Target format for connections.

    Returns:
        List of formatted connection strings.
    """
    return {
        "typst": compute_connections_for_typst,
        "markdown": compute_connections_for_markdown,
    }[file_type](rendercv_model)


@dataclass
class Connection:
    fontawesome_icon: str
    url: str | None
    body: str


def parse_connections(rendercv_model: RenderCVModel) -> list[Connection]:
    """Extract contact information from CV model into normalized connection format.

    Why:
        CV header displays various contact methods in user-defined order. This
        extracts emails, phones, websites, location, and social networks from
        the model, preserving the order specified in the input file.

    Args:
        rendercv_model: CV model with contact information.

    Returns:
        List of connections with icon specifiers, URLs, and display text.
    """
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
                        Connection(
                            fontawesome_icon=fontawesome_icons[key], url=url, body=body
                        )
                    )

            case "phone":
                phones = rendercv_model.cv.phone
                if phones is None:
                    raise RenderCVInternalError("phone key present but value is None")
                if not isinstance(phones, list):
                    phones = [phones]

                for phone in phones:
                    url = str(phone)
                    body = phonenumbers.format_number(
                        phonenumbers.parse(phone, None),
                        getattr(
                            phonenumbers.PhoneNumberFormat,
                            rendercv_model.design.header.connections.phone_number_format.upper(),
                        ),
                    )
                    connections.append(
                        Connection(
                            fontawesome_icon=fontawesome_icons[key], url=url, body=body
                        )
                    )

            case "website":
                websites = rendercv_model.cv.website
                if not websites:
                    raise RenderCVInternalError("website key present but value is None")
                if not isinstance(websites, list):
                    websites = [websites]

                for website in websites:
                    url = str(website)
                    body = clean_url(url)
                    connections.append(
                        Connection(
                            fontawesome_icon=fontawesome_icons[key], url=url, body=body
                        )
                    )

            case "location":
                url = None
                body = str(rendercv_model.cv.location)
                connections.append(
                    Connection(
                        fontawesome_icon=fontawesome_icons[key], url=None, body=body
                    )
                )

            case "social_networks":
                if rendercv_model.cv.social_networks is None:
                    raise RenderCVInternalError(
                        "social_networks key present but value is None"
                    )
                for social_network in rendercv_model.cv.social_networks:
                    url = social_network.url
                    if rendercv_model.design.header.connections.display_urls_instead_of_usernames:
                        body = clean_url(url)
                    else:
                        match social_network.network:
                            case "Google Scholar":
                                body = "Google Scholar"
                            case _:
                                body = social_network.username
                    connections.append(
                        Connection(
                            fontawesome_icon=fontawesome_icons[social_network.network],
                            url=url,
                            body=body,
                        )
                    )

            case "custom_connections":
                if rendercv_model.cv.custom_connections is None:
                    raise RenderCVInternalError(
                        "custom_connections key present but value is None"
                    )
                for custom_connection in rendercv_model.cv.custom_connections:
                    url = (
                        str(custom_connection.url)
                        if custom_connection.url is not None
                        else None
                    )
                    body = custom_connection.placeholder
                    connections.append(
                        Connection(
                            fontawesome_icon=custom_connection.fontawesome_icon,
                            url=url,
                            body=body,
                        )
                    )

    return connections


def compute_connections_for_typst(rendercv_model: RenderCVModel) -> list[str]:
    """Format connections with Typst markup, Font Awesome icons, and conditional hyperlinks.

    Why:
        Typst templates need connection strings with icon syntax and link markup.
        Icon visibility and hyperlink behavior are user-configurable through
        design settings, requiring conditional formatting at render time.

    Args:
        rendercv_model: CV model with contact information and design settings.

    Returns:
        List of Typst-formatted connection strings ready for template insertion.
    """
    connections = parse_connections(rendercv_model)

    show_icon = rendercv_model.design.header.connections.show_icons
    hyperlink = rendercv_model.design.header.connections.hyperlink

    placeholders = [
        (
            f'#connection-with-icon("{connection.fontawesome_icon}")'
            f"[{markdown_to_typst(connection.body)}]"
            if show_icon
            else markdown_to_typst(connection.body)
        )
        for connection in connections
    ]

    return [
        (
            f'#link("{connection.url}", icon: false, if-underline: false, if-color:'
            f" false)[{placeholder}]"
            if connection.url and hyperlink
            else placeholder
        )
        for connection, placeholder in zip(connections, placeholders, strict=True)
    ]


def compute_connections_for_markdown(rendercv_model: RenderCVModel) -> list[str]:
    """Format connections as Markdown links without icons.

    Args:
        rendercv_model: CV model with contact information.

    Returns:
        List of Markdown-formatted connection strings.
    """
    connections = parse_connections(rendercv_model)

    return [
        (
            f"[{connection.body}]({connection.url})"
            if connection.url
            else connection.body
        )
        for connection in connections
    ]
