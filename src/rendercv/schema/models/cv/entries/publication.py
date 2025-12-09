import functools
from typing import Self

import pydantic

from .bases.entry import BaseEntry
from .bases.entry_with_date import BaseEntryWithDate

url_validator = pydantic.TypeAdapter(pydantic.HttpUrl)


class BasePublicationEntry(BaseEntry):
    title: str = pydantic.Field(
        examples=[
            "Deep Learning for Computer Vision",
            "Advances in Quantum Computing",
        ],
    )
    authors: list[str] = pydantic.Field(
        description="You can bold your name with **double asterisks**.",
        examples=[["John Doe", "**Jane Smith**", "Bob Johnson"]],
    )
    summary: str | None = pydantic.Field(
        default=None,
        examples=["This paper presents a new method for computer vision."],
    )
    doi: str | None = pydantic.Field(
        default=None,
        description=(
            "The DOI (Digital Object Identifier). If provided, it will be used as the"
            " link instead of the URL."
        ),
        examples=["10.48550/arXiv.2310.03138"],
        pattern=r"\b10\..*",
    )
    url: pydantic.HttpUrl | None = pydantic.Field(
        default=None,
        description="A URL link to the publication. Ignored if DOI is provided.",
    )
    journal: str | None = pydantic.Field(
        default=None,
        description="The journal, conference, or venue where it was published.",
        examples=["Nature", "IEEE Conference on Computer Vision", "arXiv preprint"],
    )

    @pydantic.model_validator(mode="after")
    def ignore_url_if_doi_is_given(self) -> Self:
        """Prioritize DOI over custom URL when both provided.

        Why:
            DOI is canonical, stable identifier for publications. When provided,
            ignore user's URL to ensure templates use official DOI link.

        Returns:
            Publication instance with url cleared if DOI exists.
        """
        doi_is_provided = self.doi is not None

        if doi_is_provided:
            self.url = None

        return self

    @pydantic.model_validator(mode="after")
    def validate_doi_url(self) -> Self:
        """Validate generated DOI URL is well-formed.

        Why:
            DOI URL generation from DOI string might produce invalid URLs.
            Post-validation ensures generated URLs are valid.

        Returns:
            Validated publication instance.
        """
        if self.doi_url:
            url_validator.validate_strings(self.doi_url)

        return self

    @functools.cached_property
    def doi_url(self) -> str | None:
        """Generate DOI URL from DOI identifier.

        Why:
            DOI identifiers need https://doi.org/ prefix for linking.
            Property generates complete URL from DOI string.

        Returns:
            Complete DOI URL, or None if no DOI provided.
        """
        doi_is_provided = self.doi is not None

        if doi_is_provided:
            return f"https://doi.org/{self.doi}"

        return None


# This approach ensures PublicationEntryBase keys appear first in the key order:
class PublicationEntry(BaseEntryWithDate, BasePublicationEntry):
    pass
