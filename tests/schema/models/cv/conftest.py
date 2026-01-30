import copy
from typing import Any

import pytest

education_entry_dictionary = {
    "institution": "Boğaziçi University",
    "location": "Istanbul, Turkey",
    "degree": "BS",
    "area": "Mechanical Engineering",
    "start_date": "2015-09",
    "end_date": "2020-06",
    "highlights": [
        "GPA: 3.24/4.00 ([Transcript](https://example.com))",
        "Awards: Dean's Honor List, Sportsperson of the Year",
    ],
}

experience_entry_dictionary = {
    "company": "Some Company",
    "location": "TX, USA",
    "position": "Software Engineer",
    "start_date": "2020-07",
    "end_date": "2021-08-12",
    "highlights": [
        (
            "Developed an [IOS application](https://example.com) that has received more"
            " than **100,000 downloads**."
        ),
        "Managed a team of **5** engineers.",
    ],
}

normal_entry_dictionary = {
    "name": "Some Project",
    "location": "Remote",
    "date": "2021-09",
    "highlights": [
        "Developed a web application with **React** and **Django**.",
        "Implemented a **RESTful API**",
    ],
}

publication_entry_dictionary = {
    "title": (
        "Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of"
        " No-Insulation Coils"
    ),
    "authors": ["J. Doe", "***H. Tom***", "S. Doe", "A. Andsurname"],
    "date": "2021-12-08",
    "journal": "IEEE Transactions on Applied Superconductivity",
    "doi": "10.1109/TASC.2023.3340648",
}

one_line_entry_dictionary = {
    "label": "Programming",
    "details": "Python, C++, JavaScript, MATLAB",
}

bullet_entry_dictionary = {
    "bullet": "This is a bullet entry.",
}

numbered_entry_dictionary = {
    "number": "This is a numbered entry.",
}

reversed_numbered_entry_dictionary = {
    "reversed_number": "This is a reversed numbered entry.",
}

text_entry_dictionary = {
    "content": "This is a TextEntry with tags support.",
}


@pytest.fixture
def publication_entry() -> dict[str, Any]:
    """Return a sample publication entry."""
    return copy.deepcopy(publication_entry_dictionary)


@pytest.fixture
def experience_entry() -> dict[str, Any]:
    """Return a sample experience entry."""
    return copy.deepcopy(experience_entry_dictionary)


@pytest.fixture
def education_entry() -> dict[str, Any]:
    """Return a sample education entry."""
    return copy.deepcopy(education_entry_dictionary)


@pytest.fixture
def normal_entry() -> dict[str, Any]:
    """Return a sample normal entry."""
    return copy.deepcopy(normal_entry_dictionary)


@pytest.fixture
def one_line_entry() -> dict[str, Any]:
    """Return a sample one line entry."""
    return copy.deepcopy(one_line_entry_dictionary)


@pytest.fixture
def bullet_entry() -> dict[str, Any]:
    """Return a sample bullet entry."""
    return copy.deepcopy(bullet_entry_dictionary)


@pytest.fixture
def numbered_entry() -> dict[str, Any]:
    """Return a sample numbered entry."""
    return copy.deepcopy(numbered_entry_dictionary)


@pytest.fixture
def reversed_numbered_entry() -> dict[str, Any]:
    """Return a sample reversed numbered entry."""
    return copy.deepcopy(reversed_numbered_entry_dictionary)


@pytest.fixture
def text_entry() -> dict[str, Any]:
    """Return a sample text entry as a dict for TextEntry model."""
    return copy.deepcopy(text_entry_dictionary)


@pytest.fixture
def text_entry_string() -> str:
    """Return a sample text entry as a plain string (backward compatible)."""
    return (
        "This is a *TextEntry*. It is only a text and can be useful for sections like"
        " **Summary**. To showcase the TextEntry completely, this sentence is added,"
        " but it doesn't contain any information."
    )
