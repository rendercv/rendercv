import functools
import re
from typing import Literal

import pydantic


class SocialNetwork(RenderCVBaseModelWithoutExtraKeys):
    """This class is the data model of a social network."""

    model_config = pydantic.ConfigDict(
        title="Social Network",
    )
    network: Literal[
        "LinkedIn",
        "GitHub",
        "GitLab",
        "IMDB",
        "Instagram",
        "ORCID",
        "Mastodon",
        "StackOverflow",
        "ResearchGate",
        "YouTube",
        "Google Scholar",
        "Telegram",
        "Leetcode",
        "X",
    ] = pydantic.Field(
        title="Social Network",
    )
    username: str = pydantic.Field(
        title="Username",
        description=(
            "The username used in the social network. The link will be generated"
            " automatically."
        ),
    )

    @pydantic.field_validator("username")
    @classmethod
    def check_username(cls, username: str, info: pydantic.ValidationInfo) -> str:
        """Check if the username is provided correctly."""
        if "network" not in info.data:
            # the network is either not provided or not one of the available social
            # networks. In this case, don't check the username, since Pydantic will
            # raise an error for the network.
            return username

        network = info.data["network"]

        if network == "Mastodon":
            mastodon_username_pattern = r"@[^@]+@[^@]+"
            if not re.fullmatch(mastodon_username_pattern, username):
                message = (
                    'Mastodon username should be in the format "@username@domain"!'
                )
                raise ValueError(message)
        elif network == "StackOverflow":
            stackoverflow_username_pattern = r"\d+\/[^\/]+"
            if not re.fullmatch(stackoverflow_username_pattern, username):
                message = (
                    'StackOverflow username should be in the format "user_id/username"!'
                )
                raise ValueError(message)
        elif network == "YouTube":
            if username.startswith("@"):
                message = (
                    'YouTube username should not start with "@"! Remove "@" from the'
                    " beginning of the username."
                )
                raise ValueError(message)
        elif network == "ORCID":
            orcid_username_pattern = r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]"
            if not re.fullmatch(orcid_username_pattern, username):
                message = "ORCID username should be in the format 'XXXX-XXXX-XXXX-XXX'!"
                raise ValueError(message)
        elif network == "IMDB":
            imdb_username_pattern = r"nm\d{7}"
            if not re.fullmatch(imdb_username_pattern, username):
                message = "IMDB name should be in the format 'nmXXXXXXX'!"
                raise ValueError(message)

        return username

    @pydantic.model_validator(mode="after")  # type: ignore
    def check_url(self) -> "SocialNetwork":
        """Validate the URL of the social network."""
        if self.network == "Mastodon":
            # All the other social networks have valid URLs. Mastodon URLs contain both
            # the username and the domain. So, we need to validate if the url is valid.
            validate_url(self.url)

        return self

    @functools.cached_property
    def url(self) -> str:
        """Return the URL of the social network and cache `url` as an attribute of the
        instance.
        """
        if self.network == "Mastodon":
            # Split domain and username
            _, username, domain = self.username.split("@")
            url = f"https://{domain}/@{username}"
        else:
            url_dictionary = {
                "LinkedIn": "https://linkedin.com/in/",
                "GitHub": "https://github.com/",
                "GitLab": "https://gitlab.com/",
                "IMDB": "https://imdb.com/name/",
                "Instagram": "https://instagram.com/",
                "ORCID": "https://orcid.org/",
                "StackOverflow": "https://stackoverflow.com/users/",
                "ResearchGate": "https://researchgate.net/profile/",
                "YouTube": "https://youtube.com/@",
                "Google Scholar": "https://scholar.google.com/citations?user=",
                "Telegram": "https://t.me/",
                "Leetcode": "https://leetcode.com/u/",
                "X": "https://x.com/",
            }
            url = url_dictionary[self.network] + self.username

        return url
