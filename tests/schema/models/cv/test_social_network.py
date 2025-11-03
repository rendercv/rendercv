import pydantic
import pytest

from rendercv.schema.models.cv.social_network import SocialNetwork


@pytest.mark.parametrize(
    ("network", "username"),
    [
        ("Mastodon", "invalidmastodon"),
        ("Mastodon", "@inva@l@id"),
        ("Mastodon", "@invalid@ne<>twork.com"),
        ("StackOverflow", "invalidusername"),
        ("StackOverflow", "invalidusername//"),
        ("StackOverflow", "invalidusername/invalid"),
        ("YouTube", "@invalidusername"),
        ("NONAME", "@invalidusername"),
    ],
)
def test_invalid_social_networks(network, username):
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
            "4567/myusername",
            "https://stackoverflow.com/users/4567/myusername",
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
            "X",
            "myusername",
            "https://x.com/myusername",
        ),
    ],
)
def test_social_network_url(network, username, expected_url):
    social_network = SocialNetwork(network=network, username=username)
    assert str(social_network.url) == expected_url
