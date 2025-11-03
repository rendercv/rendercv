import pytest

from rendercv.schema.models.cv.entries.publication import PublicationEntry


@pytest.mark.parametrize(
    ("doi", "expected_doi_url"),
    [
        ("10.1109/TASC.2023.3340648", "https://doi.org/10.1109/TASC.2023.3340648"),
        (None, None),
    ],
)
def test_doi_url(publication_entry, doi, expected_doi_url):
    publication_entry["doi"] = doi
    publication_entry = PublicationEntry(**publication_entry)
    assert publication_entry.doi_url == expected_doi_url
