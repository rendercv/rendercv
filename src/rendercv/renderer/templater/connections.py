from dataclasses import dataclass
from typing import Literal

import phonenumbers

from rendercv.schema.models.rendercv_model import RenderCVModel

from .markdown_parser import markdown_to_typst
from .string_processor import clean_url


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
    icon_specifier: str
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
                        Connection(icon_specifier=key, url=url, body=body)
                    )

            case "phone":
                phones = rendercv_model.cv.phone
                assert phones is not None
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
            if rendercv_model.design.header.connections.display_urls_instead_of_usernames:
                body = clean_url(url)
            else:
                match social_network.network:
                    case "Google Scholar":
                        body = "Google Scholar"
                    case _:
                        body = social_network.username
            connections.append(
                Connection(icon_specifier=social_network.network, url=url, body=body)
            )

    return connections


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
            f'#connection-with-icon("{typst_fa_icons[connection.icon_specifier]}")'
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
