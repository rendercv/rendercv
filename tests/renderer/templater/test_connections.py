from typing import Literal

import pytest

from rendercv.renderer.templater.connections import (
    compute_connections,
    compute_connections_for_markdown,
    compute_connections_for_typst,
    parse_connections,
)
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.cv.social_network import SocialNetwork
from rendercv.schema.models.design.classic_theme import ClassicTheme, Header
from rendercv.schema.models.locale.locale import EnglishLocale
from rendercv.schema.models.rendercv_model import RenderCVModel


def create_cv(
    *,
    key_order: list[str],
    email: list[str] | str | None = None,
    phone: list[str] | str | None = None,
    website: list[str] | str | None = None,
    location: str | None = None,
    social_networks: list[SocialNetwork] | None = None,
):
    cv_data = {}
    for key in key_order:
        if key == "email" and email is not None:
            cv_data["email"] = email
        elif key == "phone" and phone is not None:
            cv_data["phone"] = phone
        elif key == "website" and website is not None:
            cv_data["website"] = website
        elif key == "location" and location is not None:
            cv_data["location"] = location

    cv_data["name"] = "John Doe"
    if social_networks is not None:
        cv_data["social_networks"] = social_networks

    return Cv.model_validate(cv_data)


def create_rendercv_model(
    cv,
    use_icons_for_connections: bool = True,
    make_connections_links: bool = True,
    phone_number_format: Literal["national", "international", "E164"] = "international",
):
    design = ClassicTheme(
        header=Header(
            use_icons_for_connections=use_icons_for_connections,
            make_connections_links=make_connections_links,
        )
    )

    locale = EnglishLocale(phone_number_format=phone_number_format)

    return RenderCVModel(cv=cv, design=design, locale=locale)


class TestParseConnections:
    def test_single_email(self):
        cv = create_cv(
            email="john@example.com",
            key_order=["email"],
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == 1
        assert connections[0]["icon_specifier"] == "email"
        assert connections[0]["url"] == "mailto:john@example.com"
        assert connections[0]["body"] == "john@example.com"

    def test_multiple_emails(self):
        cv = create_cv(
            email=["john@example.com", "jane@example.com"],
            key_order=["email"],
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == 2
        assert connections[0]["body"] == "john@example.com"
        assert connections[1]["body"] == "jane@example.com"
        assert all(c["url"] and c["url"].startswith("mailto:") for c in connections)

    @pytest.mark.parametrize(
        ("phone_input", "phone_format", "expected_body"),
        [
            ("+14155552671", "international", "+1 415-555-2671"),
            ("+14155552671", "national", "(415) 555-2671"),
            ("+14155552671", "E164", "+14155552671"),
        ],
    )
    def test_single_phone_formatting(self, phone_input, phone_format, expected_body):
        cv = create_cv(
            phone=phone_input,
            key_order=["phone"],
        )
        model = create_rendercv_model(cv, phone_number_format=phone_format)

        connections = parse_connections(model)

        assert len(connections) == 1
        assert connections[0]["icon_specifier"] == "phone"
        assert connections[0]["body"] == expected_body

    def test_multiple_phones(self):
        cv = create_cv(
            phone=["+14155552671", "+442071234567"],
            key_order=["phone"],
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == 2
        assert connections[0]["icon_specifier"] == "phone"
        assert connections[1]["icon_specifier"] == "phone"
        assert connections[0]["body"] == "+1 415-555-2671"
        assert connections[1]["body"] == "+44 20 7123 4567"

    def test_single_website(self):
        cv = create_cv(
            website="https://example.com",
            key_order=["website"],
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == 1
        assert connections[0]["icon_specifier"] == "website"
        # Pydantic's HttpUrl normalizes URLs by adding trailing slash
        assert connections[0]["url"] == "https://example.com/"
        # Note: clean_url removes https:// prefix
        assert "example.com" in connections[0]["body"]

    def test_multiple_websites(self):
        cv = create_cv(
            website=["https://example.com", "https://blog.example.com"],
            key_order=["website"],
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == 2
        assert all(c["icon_specifier"] == "website" for c in connections)

    def test_location(self):
        cv = create_cv(
            location="New York, NY",
            key_order=["location"],
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == 1
        assert connections[0]["icon_specifier"] == "location"
        assert connections[0]["url"] is None
        assert connections[0]["body"] == "New York, NY"

    def test_social_networks(self):
        social_network = SocialNetwork(network="LinkedIn", username="johndoe")

        cv = create_cv(
            social_networks=[social_network],
            key_order=[],
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == 1
        assert connections[0]["icon_specifier"] == "LinkedIn"
        assert connections[0]["url"] == "https://linkedin.com/in/johndoe"
        assert connections[0]["body"] == "johndoe"

    def test_multiple_social_networks(self):
        linkedin = SocialNetwork(network="LinkedIn", username="johndoe")
        github = SocialNetwork(network="GitHub", username="johndoe")

        cv = create_cv(
            social_networks=[linkedin, github],
            key_order=[],
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == 2
        assert connections[0]["icon_specifier"] == "LinkedIn"
        assert connections[1]["icon_specifier"] == "GitHub"

    def test_key_order_preservation(self):
        cv = create_cv(
            email="john@example.com",
            phone="+14155552671",
            website="https://example.com",
            location="New York, NY",
            key_order=["location", "email", "phone", "website"],
            social_networks=[
                SocialNetwork(network="LinkedIn", username="johndoe"),
                SocialNetwork(network="GitHub", username="johndoe"),
            ],
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert connections[0]["icon_specifier"] == "location"
        assert connections[1]["icon_specifier"] == "email"
        assert connections[2]["icon_specifier"] == "phone"
        assert connections[3]["icon_specifier"] == "website"
        assert connections[4]["icon_specifier"] == "LinkedIn"
        assert connections[5]["icon_specifier"] == "GitHub"

    def test_empty_connections(self):
        cv = create_cv(key_order=[])
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert connections == []

    def test_unknown_key_in_order(self):
        cv = create_cv(
            email="john@example.com",
            key_order=["unknown_field", "email", "another_unknown"],
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == 1
        assert connections[0]["icon_specifier"] == "email"


class TestComputeConnectionsForTypst:
    def test_with_icons_and_links(self):
        cv = create_cv(
            email="john@example.com",
            phone="+14155552671",
            key_order=["email", "phone", "location"],
        )
        model = create_rendercv_model(
            cv, use_icons_for_connections=True, make_connections_links=True
        )

        result = compute_connections_for_typst(model)

        assert len(result) == 2
        # Should have both icon and link
        assert "#connection-with-icon" in result[0]
        assert "#link(" in result[0]
        assert "mailto:john@example.com" in result[0]
        assert "#connection-with-icon" in result[1]
        assert "#link(" in result[1]
        assert "tel:+1-415-555-2671" in result[1]

    def test_with_icons_without_links(self):
        cv = create_cv(
            email="john@example.com",
            key_order=["email"],
        )
        model = create_rendercv_model(
            cv, use_icons_for_connections=True, make_connections_links=False
        )

        result = compute_connections_for_typst(model)

        assert len(result) == 1
        # Should have icon but no link
        assert "#connection-with-icon" in result[0]
        assert "#link(" not in result[0]

    def test_without_icons_with_links(self):
        cv = create_cv(
            email="john@example.com",
            key_order=["email"],
        )
        model = create_rendercv_model(
            cv, use_icons_for_connections=False, make_connections_links=True
        )

        result = compute_connections_for_typst(model)

        assert len(result) == 1
        # Should have link but no icon wrapper
        assert "#connection-with-icon" not in result[0]
        assert "#link(" in result[0]

    def test_without_icons_without_links(self):
        cv = create_cv(
            email="john@example.com",
            key_order=["email"],
        )
        model = create_rendercv_model(
            cv, use_icons_for_connections=False, make_connections_links=False
        )

        result = compute_connections_for_typst(model)

        assert len(result) == 1
        assert "#connection-with-icon" not in result[0]
        assert "#link(" not in result[0]
        assert "john@example.com" in result[0]

    def test_location_without_url(self):
        cv = create_cv(
            location="New York, NY",
            key_order=["location"],
        )
        model = create_rendercv_model(
            cv, use_icons_for_connections=True, make_connections_links=True
        )

        result = compute_connections_for_typst(model)

        assert len(result) == 1
        assert "#connection-with-icon" in result[0]
        assert "#link(" not in result[0]

    def test_multiple_connections(self):
        cv = create_cv(
            email="john@example.com",
            phone="+14155552671",
            location="New York, NY",
            key_order=["email", "phone", "location"],
        )
        model = create_rendercv_model(
            cv, use_icons_for_connections=True, make_connections_links=True
        )

        result = compute_connections_for_typst(model)

        assert len(result) == 3
        assert "#link(" in result[0]
        assert "#link(" in result[1]
        assert "#link(" not in result[2]


class TestComputeConnectionsForMarkdown:
    def test_email_with_link(self):
        cv = create_cv(
            email="john@example.com",
            key_order=["email"],
        )
        model = create_rendercv_model(cv)

        result = compute_connections_for_markdown(model)

        assert len(result) == 1
        assert result[0] == "[john@example.com](mailto:john@example.com)"

    def test_phone_with_link(self):
        cv = create_cv(
            phone="+14155552671",
            key_order=["phone"],
        )
        model = create_rendercv_model(cv)

        result = compute_connections_for_markdown(model)

        assert len(result) == 1
        assert result[0].startswith("[+1 415-555-2671]")
        assert "415-555-2671" in result[0]

    def test_website_with_link(self):
        cv = create_cv(
            website="https://example.com",
            key_order=["website"],
        )
        model = create_rendercv_model(cv)

        result = compute_connections_for_markdown(model)

        assert len(result) == 1
        assert result[0].startswith("[")
        # Pydantic's HttpUrl normalizes URLs by adding trailing slash
        assert "](https://example.com/)" in result[0]

    def test_location_without_link(self):
        """Test markdown location without link."""
        cv = create_cv(
            location="New York, NY",
            key_order=["location"],
        )
        model = create_rendercv_model(cv)

        result = compute_connections_for_markdown(model)

        assert len(result) == 1
        # Location has no URL, so it's plain text
        assert result[0] == "New York, NY"
        assert "[" not in result[0]
        assert "]" not in result[0]

    def test_social_network_with_link(self):
        """Test markdown social network connection."""
        github = SocialNetwork(network="GitHub", username="johndoe")

        cv = create_cv(
            social_networks=[github],
            key_order=[],
        )
        model = create_rendercv_model(cv)

        result = compute_connections_for_markdown(model)

        assert len(result) == 1
        assert result[0] == "[johndoe](https://github.com/johndoe)"

    def test_multiple_connections(self):
        """Test formatting multiple connections for markdown."""
        cv = create_cv(
            email="john@example.com",
            location="New York, NY",
            key_order=["email", "location"],
        )
        model = create_rendercv_model(cv)

        result = compute_connections_for_markdown(model)

        assert len(result) == 2
        assert "[john@example.com]" in result[0]
        assert result[1] == "New York, NY"


class TestComputeConnections:
    def test_dispatches_to_typst(self):
        """Test that compute_connections dispatches to Typst function."""
        cv = create_cv(
            email="john@example.com",
            key_order=["email"],
        )
        model = create_rendercv_model(
            cv, use_icons_for_connections=True, make_connections_links=True
        )

        result = compute_connections(model, "typst")

        # Should return Typst-formatted output
        assert len(result) == 1
        assert "#connection-with-icon" in result[0]

    def test_dispatches_to_markdown(self):
        """Test that compute_connections dispatches to markdown function."""
        cv = create_cv(
            email="john@example.com",
            key_order=["email"],
        )
        model = create_rendercv_model(cv)

        result = compute_connections(model, "markdown")

        # Should return markdown-formatted output
        assert len(result) == 1
        assert result[0] == "[john@example.com](mailto:john@example.com)"

    @pytest.mark.parametrize(
        "file_type",
        ["typst", "markdown"],
    )
    def test_both_file_types(self, file_type):
        """Test dispatcher works for both file types."""
        cv = create_cv(
            email="john@example.com",
            key_order=["email"],
        )
        model = create_rendercv_model(cv)

        result = compute_connections(model, file_type)

        # Should return a list with one connection
        assert len(result) == 1
        assert isinstance(result[0], str)
