import functools
import re
from typing import Literal

import pydantic
import pydantic_core

from ...utils.custom_pydantic_error_types import CustomPydanticErrorTypes
from ..base import BaseModelWithoutExtraKeys

url_validator = pydantic.TypeAdapter(pydantic.HttpUrl)


class SocialNetwork(BaseModelWithoutExtraKeys):
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
        description="The name of the social network or platform.",
    )
    username: str = pydantic.Field(
        description="Your username on the platform.",
        examples=["john_doe", "@johndoe@mastodon.social", "12345/john-doe"],
    )

    @pydantic.field_validator("username")
    @classmethod
    def check_username(cls, username: str, info: pydantic.ValidationInfo) -> str:
        if "network" not in info.data:
            # the network is either not provided or not one of the available social
            # networks. In this case, don't check the username, since Pydantic will
            # raise an error for the network.
            return username

        network = info.data["network"]

        match network:
            case "Mastodon":
                mastodon_username_pattern = r"@[^@]+@[^@]+"
                if not re.fullmatch(mastodon_username_pattern, username):
                    raise pydantic_core.PydanticCustomError(
                        CustomPydanticErrorTypes.other.value,
                        'Mastodon username should be in the format "@username@domain".',
                    )
            case "StackOverflow":
                stackoverflow_username_pattern = r"\d+\/[^\/]+"
                if not re.fullmatch(stackoverflow_username_pattern, username):
                    raise pydantic_core.PydanticCustomError(
                        CustomPydanticErrorTypes.other.value,
                        "StackOverflow username should be in the format"
                        ' "user_id/username".',
                    )
            case "YouTube":
                if username.startswith("@"):
                    raise pydantic_core.PydanticCustomError(
                        CustomPydanticErrorTypes.other.value,
                        'YouTube username should not start with "@". Remove "@" from'
                        ' the beginning of the username."',
                    )
            case "ORCID":
                orcid_username_pattern = r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]"
                if not re.fullmatch(orcid_username_pattern, username):
                    raise pydantic_core.PydanticCustomError(
                        CustomPydanticErrorTypes.other.value,
                        "ORCID username should be in the format 'XXXX-XXXX-XXXX-XXX'.",
                    )
            case "IMDB":
                imdb_username_pattern = r"nm\d{7}"
                if not re.fullmatch(imdb_username_pattern, username):
                    raise pydantic_core.PydanticCustomError(
                        CustomPydanticErrorTypes.other.value,
                        "IMDB name should be in the format 'nmXXXXXXX'.",
                    )

        return username

    @pydantic.model_validator(mode="after")
    def validate_generated_url(self) -> "SocialNetwork":
        url_validator.validate_strings(self.url)
        return self

    @functools.cached_property
    def url(self) -> str:
        if self.network == "Mastodon":
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
