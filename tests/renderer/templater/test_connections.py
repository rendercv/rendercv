from typing import Literal, get_args

import pytest

from rendercv.renderer.templater.connections import (
    compute_connections,
    compute_connections_for_markdown,
    compute_connections_for_typst,
    parse_connections,
    typst_fa_icons,
)
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.cv.social_network import SocialNetwork, SocialNetworkName
from rendercv.schema.models.design.classic_theme import (
    ClassicTheme,
    Connections,
    Header,
)
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
) -> Cv:
    """Create a test CV with specified connection fields in a specific order.

    The key_order parameter determines the order connections appear in the CV,
    which is preserved in the final output.
    """
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
    cv: Cv,
    *,
    use_icons: bool = True,
    make_links: bool = True,
    phone_format: Literal["national", "international", "E164"] = "international",
) -> RenderCVModel:
    """Create a test RenderCVModel with specified connection formatting options.

    Used to test different connection rendering configurations (icons, links, phone format).
    """
    return RenderCVModel(
        cv=cv,
        design=ClassicTheme(
            header=Header(
                connections=Connections(
                    show_icons=use_icons,
                    hyperlink=make_links,
                    phone_number_format=phone_format,
                )
            )
        ),
        locale=EnglishLocale(),
    )


class TestParseConnections:
    @pytest.mark.parametrize(
        ("field", "value", "expected_count", "expected_icon"),
        [
            ("email", "john@example.com", 1, "email"),
            ("email", ["john@example.com", "jane@example.com"], 2, "email"),
            ("phone", "+14155552671", 1, "phone"),
            ("phone", ["+14155552671", "+442071234567"], 2, "phone"),
            ("website", "https://example.com", 1, "website"),
            (
                "website",
                ["https://example.com", "https://blog.example.com"],
                2,
                "website",
            ),
            ("location", "New York, NY", 1, "location"),
        ],
    )
    def test_parse_single_field_type(self, field, value, expected_count, expected_icon):
        cv = create_cv(key_order=[field], **{field: value})
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == expected_count
        assert all(c.icon_specifier == expected_icon for c in connections)

    def test_email_connection_structure(self):
        cv = create_cv(key_order=["email"], email="john@example.com")
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert connections[0].url == "mailto:john@example.com"
        assert connections[0].body == "john@example.com"

    @pytest.mark.parametrize(
        ("phone", "phone_format", "expected_body"),
        [
            ("+14155552671", "international", "+1 415-555-2671"),
            ("+14155552671", "national", "(415) 555-2671"),
            ("+14155552671", "E164", "+14155552671"),
        ],
    )
    def test_phone_formatting(self, phone, phone_format, expected_body):
        cv = create_cv(key_order=["phone"], phone=phone)
        model = create_rendercv_model(cv, phone_format=phone_format)

        connections = parse_connections(model)

        assert connections[0].body == expected_body

    def test_website_connection_structure(self):
        cv = create_cv(key_order=["website"], website="https://example.com")
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        # Pydantic's HttpUrl adds trailing slash
        assert connections[0].url == "https://example.com/"
        assert connections[0].body == "example.com"

    def test_location_has_no_url(self):
        cv = create_cv(key_order=["location"], location="New York, NY")
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert connections[0].url is None
        assert connections[0].body == "New York, NY"

    def test_social_network_connection(self):
        social = SocialNetwork(network="LinkedIn", username="johndoe")
        cv = create_cv(key_order=[], social_networks=[social])
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == 1
        assert connections[0].icon_specifier == "LinkedIn"
        assert connections[0].url == "https://linkedin.com/in/johndoe"
        assert connections[0].body == "johndoe"

    def test_key_order_is_preserved(self):
        cv = create_cv(
            key_order=["location", "email", "phone", "website"],
            location="NYC",
            email="john@example.com",
            phone="+14155552671",
            website="https://example.com",
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        icons = [c.icon_specifier for c in connections]  # type: ignore
        assert icons == ["location", "email", "phone", "website"]

    def test_social_networks_appended_after_key_order(self):
        cv = create_cv(
            key_order=["email"],
            email="john@example.com",
            social_networks=[
                SocialNetwork(network="LinkedIn", username="johndoe"),
                SocialNetwork(network="GitHub", username="johndoe"),
            ],
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        icons = [c.icon_specifier for c in connections]  # type: ignore
        assert icons == ["email", "LinkedIn", "GitHub"]

    def test_empty_key_order_returns_empty_list(self):
        cv = create_cv(key_order=[])
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert connections == []

    def test_unknown_keys_are_ignored(self):
        cv = create_cv(
            key_order=["unknown_field", "email", "another_unknown"],
            email="john@example.com",
        )
        model = create_rendercv_model(cv)

        connections = parse_connections(model)

        assert len(connections) == 1
        assert connections[0].icon_specifier == "email"


class TestComputeConnectionsForTypst:
    @pytest.mark.parametrize(
        ("use_icons", "make_links", "expected_patterns"),
        [
            (True, True, ["#connection-with-icon", "#link("]),
            (True, False, ["#connection-with-icon"]),
            (False, True, ["#link("]),
            (False, False, []),
        ],
    )
    def test_icon_and_link_combinations(self, use_icons, make_links, expected_patterns):
        cv = create_cv(key_order=["email"], email="john@example.com")
        model = create_rendercv_model(cv, use_icons=use_icons, make_links=make_links)

        result = compute_connections_for_typst(model)

        assert len(result) == 1
        for pattern in expected_patterns:
            assert pattern in result[0]

        # Check that unwanted patterns are NOT present
        if not use_icons:
            assert "#connection-with-icon" not in result[0]
        if not make_links:
            assert "#link(" not in result[0]

    def test_connection_without_url_has_no_link(self):
        cv = create_cv(key_order=["location"], location="New York, NY")
        model = create_rendercv_model(cv, use_icons=True, make_links=True)

        result = compute_connections_for_typst(model)

        assert "#connection-with-icon" in result[0]
        assert "#link(" not in result[0]

    def test_plain_text_output_when_no_formatting(self):
        cv = create_cv(key_order=["email"], email="john@example.com")
        model = create_rendercv_model(cv, use_icons=False, make_links=False)

        result = compute_connections_for_typst(model)

        assert "john\\@example.com" in result[0]


class TestComputeConnectionsForMarkdown:
    def test_connection_with_url_formatted_as_markdown_link(self):
        cv = create_cv(key_order=["email"], email="john@example.com")
        model = create_rendercv_model(cv)

        result = compute_connections_for_markdown(model)

        assert result[0] == "[john@example.com](mailto:john@example.com)"

    def test_connection_without_url_is_plain_text(self):
        cv = create_cv(key_order=["location"], location="New York, NY")
        model = create_rendercv_model(cv)

        result = compute_connections_for_markdown(model)

        assert result[0] == "New York, NY"
        assert "[" not in result[0]


class TestComputeConnections:
    @pytest.mark.parametrize("file_type", ["typst", "markdown"])
    def test_dispatches_to_correct_formatter(self, file_type):
        cv = create_cv(key_order=["email"], email="john@example.com")
        model = create_rendercv_model(cv, use_icons=True, make_links=True)

        result = compute_connections(model, file_type)

        assert len(result) == 1
        assert isinstance(result[0], str)

        if file_type == "typst":
            assert "#connection-with-icon" in result[0]
        else:  # markdown
            assert result[0].startswith("[")


class TestIconMapping:
    @pytest.mark.parametrize("network", get_args(SocialNetworkName.__value__))
    def test_all_social_networks_have_icons(self, network):
        assert network in typst_fa_icons, f"Missing icon for social network: {network}"

    @pytest.mark.parametrize("conn_type", ["email", "phone", "website", "location"])
    def test_all_connection_types_have_icons(self, conn_type):
        assert conn_type in typst_fa_icons, (
            f"Missing icon for connection type: {conn_type}"
        )
