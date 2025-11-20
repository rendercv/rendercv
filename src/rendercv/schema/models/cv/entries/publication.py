import functools
from typing import Self

import pydantic

from .basis.entry import BaseEntry
from .basis.entry_with_date import BaseEntryWithDate

url_validator = pydantic.TypeAdapter(pydantic.HttpUrl)


class BasePublicationEntry(BaseEntry):
    title: str = pydantic.Field(
        examples=[
            "Deep Learning for Computer Vision",
            "Advances in Quantum Computing",
        ],
    )
    authors: list[str] = pydantic.Field(
        description=(
            "List of authors. A name can be bolded by wrapping it with **double"
            " asterisks**."
        ),
        examples=[["John Doe", "**Jane Smith**", "Bob Johnson"]],
    )
    doi: str | None = pydantic.Field(
        default=None,
        description=(
            "The DOI (Digital Object Identifier) of the publication. If provided, it"
            " will be used as the link instead of the URL."
        ),
        examples=["10.48550/arXiv.2310.03138"],
        pattern=r"\b10\..*",
    )
    url: pydantic.HttpUrl | None = pydantic.Field(
        default=None,
        description=(
            "A URL link to the publication. Note: If DOI is provided, this URL will be"
            " ignored."
        ),
    )
    journal: str | None = pydantic.Field(
        default=None,
        description=(
            "The name of the journal, conference, or venue where it was published."
        ),
        examples=["Nature", "IEEE Conference on Computer Vision", "arXiv preprint"],
    )

    @pydantic.model_validator(mode="after")
    def ignore_url_if_doi_is_given(self) -> Self:
        doi_is_provided = self.doi is not None

        if doi_is_provided:
            self.url = None

        return self

    @pydantic.model_validator(mode="after")
    def validate_doi_url(self) -> Self:
        if self.doi_url:
            url_validator.validate_strings(self.doi_url)

        return self

    @functools.cached_property
    def doi_url(self) -> str | None:
        doi_is_provided = self.doi is not None

        if doi_is_provided:
            return f"https://doi.org/{self.doi}"

        return None


# This approach ensures PublicationEntryBase keys appear first in the key order:
class PublicationEntry(BasePublicationEntry, BaseEntryWithDate):
    pass
