import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rendercv.schema.models.cv.entries.publication import PublicationEntry


class TestPublicationEntry:
    @pytest.mark.parametrize(
        ("doi", "expected_doi_url"),
        [
            ("10.1109/TASC.2023.3340648", "https://doi.org/10.1109/TASC.2023.3340648"),
            (None, None),
        ],
    )
    def test_doi_url(self, publication_entry, doi, expected_doi_url):
        publication_entry["doi"] = doi
        publication_entry = PublicationEntry(**publication_entry)
        assert publication_entry.doi_url == expected_doi_url

    @settings(deadline=None)
    @given(doi=st.from_regex(r"10\.\d{4,9}/[a-zA-Z0-9._-]+", fullmatch=True))
    def test_doi_url_always_produces_valid_url(self, doi: str) -> None:
        entry = PublicationEntry(title="Paper", authors=["Author"], doi=doi)
        assert entry.doi_url == f"https://doi.org/{doi}"
