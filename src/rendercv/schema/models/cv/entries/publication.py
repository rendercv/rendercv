from typing import Self

import pydantic

from .basis.entry import BaseEntry
from .basis.entry_with_date import BaseEntryWithDate


class BasePublicationEntry(BaseEntry):
    title: str
    authors: list[str]
    doi: str | None = pydantic.Field(
        default=None,
        examples=["10.48550/arXiv.2310.03138"],
        pattern=r"\b10\..*",
    )
    url: pydantic.HttpUrl | None = pydantic.Field(
        default=None,
        description="If DOI is provided, URL will be ignored.",
    )
    journal: str | None = None

    @pydantic.model_validator(mode="after")
    def ignore_url_if_doi_is_given(self) -> Self:
        doi_is_provided = self.doi is not None

        if doi_is_provided:
            self.url = None

        return self


# This approach ensures PublicationEntryBase keys appear first in the key order:
class PublicationEntry(BasePublicationEntry, BaseEntryWithDate):
    pass
