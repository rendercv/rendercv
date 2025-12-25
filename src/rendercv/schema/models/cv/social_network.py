import functools
import re
from typing import Literal, TypeAlias, get_args

import pydantic
import pydantic_core
import pydantic_extra_types.phone_numbers as pydantic_phone_numbers

from ...pydantic_error_handling import CustomPydanticErrorTypes
from ..base import BaseModelWithoutExtraKeys

url_validator = pydantic.TypeAdapter(pydantic.HttpUrl)
SocialNetworkName: TypeAlias = Literal[
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
    "WhatsApp",
    "Leetcode",
    "X",
    "Bluesky",
]
available_social_networks = get_args(SocialNetworkName)
url_dictionary: dict[SocialNetworkName, str] = {
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
    "WhatsApp": "https://wa.me/",
    "Leetcode": "https://leetcode.com/u/",
    "X": "https://x.com/",
    "Bluesky": "https://bsky.app/profile/",
}


class SocialNetwork(BaseModelWithoutExtraKeys):
    network: SocialNetworkName = pydantic.Field()
    username: str = pydantic.Field(
        examples=["john_doe", "@johndoe@mastodon.social", "12345/john-doe"],
    )

    @pydantic.field_validator("username")
    @classmethod
    def check_username(cls, username: str, info: pydantic.ValidationInfo) -> str:
        """Validate username format per network's requirements.

        Why:
            Different platforms have specific username formats (e.g., Mastodon needs
            @user@domain, StackOverflow needs id/name). Early validation prevents
            broken URL generation.

        Args:
            username: Username to validate.
            info: Validation context containing network field.

        Returns:
            Validated username.
        """
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
            case "Bluesky":
                bluesky_username_pattern = r"^([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
                if not re.fullmatch(bluesky_username_pattern, username):
                    raise pydantic_core.PydanticCustomError(
                        CustomPydanticErrorTypes.other.value,
                        "Bluesky username should be a valid handle with no '@' (e.g.,"
                        " 'username.bsky.social' or 'domain.com').",
                    )
            case "WhatsApp":
                phone_validator = pydantic.TypeAdapter(
                    pydantic_phone_numbers.PhoneNumber
                )
                try:
                    phone_validator.validate_python(username)
                except pydantic.ValidationError as e:
                    raise pydantic_core.PydanticCustomError(
                        CustomPydanticErrorTypes.other.value,
                        "WhatsApp username should be your phone number with country"
                        " code in international format (e.g., +1 for USA, +44 for UK).",
                    ) from e

        return username

    @pydantic.model_validator(mode="after")
    def validate_generated_url(self) -> "SocialNetwork":
        """Validate generated URL is well-formed.

        Why:
            URL generation from username might produce invalid URLs if username
            format is wrong. Post-validation check catches edge cases.

        Returns:
            Validated social network instance.
        """
        url_validator.validate_strings(self.url)
        return self

    @functools.cached_property
    def url(self) -> str:
        """Generate profile URL from network and username.

        Why:
            Users provide network+username for brevity. Property generates full
            URLs with platform-specific logic (e.g., Mastodon domain extraction).

        Returns:
            Complete profile URL.
        """
        if self.network == "Mastodon":
            _, username, domain = self.username.split("@")
            url = f"https://{domain}/@{username}"
        else:
            url = url_dictionary[self.network] + self.username

        return url
