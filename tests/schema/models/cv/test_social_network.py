from typing import get_args

import pydantic
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rendercv.schema.models.cv.social_network import (
    SocialNetwork,
    SocialNetworkName,
    url_dictionary,
)


class TestSocialNetwork:
    def test_all_urls_are_present(self):
        assert set(url_dictionary.keys()) == (
            set(get_args(SocialNetworkName.__value__)) - {"Mastodon"}
        )

    @pytest.mark.parametrize(
        ("network", "username"),
        [
            ("Mastodon", "invalidmastodon"),
            ("Mastodon", "@inva@l@id"),
            ("Mastodon", "@invalid@ne<>twork.com"),
            ("StackOverflow", "invalidusername//"),
            ("StackOverflow", "invalidusername/invalid"),
            ("StackOverflow", "4567/"),
            ("StackOverflow", "user name"),
            ("YouTube", "@invalidusername"),
            ("NONAME", "@invalidusername"),
            ("WhatsApp", "invalidphone"),
            ("Bluesky", "invalidusername"),
            ("Reddit", "invalid~username"),
        ],
    )
    def test_rejects_invalid_networks_and_usernames(self, network, username):
        with pytest.raises(pydantic.ValidationError):
            SocialNetwork(network=network, username=username)

    @pytest.mark.parametrize(
        ("network", "username", "expected_url"),
        [
            ("LinkedIn", "myusername", "https://linkedin.com/in/myusername"),
            ("GitHub", "myusername", "https://github.com/myusername"),
            ("IMDB", "nm0000001", "https://imdb.com/name/nm0000001"),
            ("Instagram", "myusername", "https://instagram.com/myusername"),
            ("ORCID", "0000-0000-0000-0000", "https://orcid.org/0000-0000-0000-0000"),
            ("Mastodon", "@myusername@test.org", "https://test.org/@myusername"),
            (
                "StackOverflow",
                "myusername",
                "https://stackoverflow.com/users/myusername",
            ),
            (
                "GitLab",
                "myusername",
                "https://gitlab.com/myusername",
            ),
            (
                "ResearchGate",
                "myusername",
                "https://researchgate.net/profile/myusername",
            ),
            (
                "YouTube",
                "myusername",
                "https://youtube.com/@myusername",
            ),
            (
                "Google Scholar",
                "myusername",
                "https://scholar.google.com/citations?user=myusername",
            ),
            (
                "Telegram",
                "myusername",
                "https://t.me/myusername",
            ),
            (
                "WhatsApp",
                "+14155552671",
                "https://wa.me/+14155552671",
            ),
            (
                "X",
                "myusername",
                "https://x.com/myusername",
            ),
            (
                "Bluesky",
                "myusername.bsky.social",
                "https://bsky.app/profile/myusername.bsky.social",
            ),
            ("Reddit", "myusername", "https://reddit.com/user/myusername"),
        ],
    )
    def test_url(self, network, username, expected_url):
        social_network = SocialNetwork(network=network, username=username)
        assert str(social_network.url) == expected_url

    @settings(deadline=None)
    @given(
        username=st.from_regex(
            r"@[a-zA-Z0-9_]{1,15}@[a-z]{2,10}\.[a-z]{2,4}", fullmatch=True
        )
    )
    def test_mastodon_valid_format_accepted(self, username: str) -> None:
        sn = SocialNetwork(network="Mastodon", username=username)
        assert sn.username == username

    @settings(deadline=None)
    @given(
        user=st.from_regex(r"[a-zA-Z0-9_]{1,15}", fullmatch=True),
        domain=st.from_regex(r"[a-z]{2,10}\.[a-z]{2,4}", fullmatch=True),
    )
    def test_mastodon_url_contains_username_and_domain(
        self, user: str, domain: str
    ) -> None:
        username = f"@{user}@{domain}"
        sn = SocialNetwork(network="Mastodon", username=username)
        assert domain in sn.url
        assert f"/@{user}" in sn.url
        assert sn.url.startswith("https://")

    @settings(deadline=None)
    @given(username=st.from_regex(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", fullmatch=True))
    def test_orcid_valid_format_accepted(self, username: str) -> None:
        sn = SocialNetwork(network="ORCID", username=username)
        assert sn.username == username

    @settings(deadline=None)
    @given(username=st.from_regex(r"[a-zA-Z0-9._-]{1,30}", fullmatch=True))
    def test_stackoverflow_valid_format_accepted(self, username: str) -> None:
        sn = SocialNetwork(network="StackOverflow", username=username)
        assert sn.username == username
        assert sn.url == f"https://stackoverflow.com/users/{username}"

    @pytest.mark.parametrize(
        ("username", "expected_username"),
        [
            ("johndoe", "johndoe"),
            ("12323/johndoe", "johndoe"),
            ("4567/myusername", "myusername"),
        ],
    )
    def test_stackoverflow_legacy_id_is_stripped(
        self, username: str, expected_username: str
    ) -> None:
        """The numeric id is dropped so only the username is rendered/linked."""
        sn = SocialNetwork(network="StackOverflow", username=username)
        assert sn.username == expected_username
        assert sn.url == f"https://stackoverflow.com/users/{expected_username}"

    @settings(deadline=None)
    @given(username=st.from_regex(r"[a-zA-Z0-9_-]{3,23}", fullmatch=True))
    def test_reddit_valid_format_accepted(self, username: str) -> None:
        sn = SocialNetwork(network="Reddit", username=username)
        assert sn.username == username

    @settings(deadline=None)
    @given(
        network=st.sampled_from(["LinkedIn", "GitHub", "GitLab", "X"]),
        username=st.from_regex(r"[a-zA-Z0-9_-]{1,20}", fullmatch=True),
    )
    def test_valid_network_url_is_valid_http_url(
        self, network: SocialNetworkName, username: str
    ) -> None:
        sn = SocialNetwork(network=network, username=username)
        pydantic.TypeAdapter(pydantic.HttpUrl).validate_strings(sn.url)
