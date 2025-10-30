from typing import Self

import pydantic

from .basis.entry import Entry
from .basis.entry_with_date import EntryWithDate


class PublicationEntryBase(Entry):
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


# The following class is to ensure PublicationEntryBase keys come first,
# then the keys of the EntryWithDate class. The only way to achieve this in Pydantic is
# to do this. The same thing is done for the other classes as well.
class PublicationEntry(PublicationEntryBase, EntryWithDate):
    pass
