<<<<<<< HEAD
"""This module contains fixtures and other helpful functions for the tests."""

import copy
import filecmp
import itertools
import json
import os
=======
>>>>>>> f16aca9 (Rename old tests)
import pathlib

import pytest
<<<<<<< HEAD
import ruamel.yaml

from rendercv import old_data as data
from rendercv.renderer import templater

# RenderCV is being tested by comparing the output to reference files. Therefore,
# reference files should be updated when RenderCV is updated in a way that changes
# the output. Setting update_testdata to True will update the reference files with
# the latest RenderCV. This should be done with caution, as it will overwrite the
# reference files with the latest output.
update_testdata = os.getenv("UPDATE_TESTDATA", "false").lower() == "true"

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
=======
>>>>>>> f16aca9 (Rename old tests)


@pytest.fixture
def testdata_dir(request):
    module_path = pathlib.Path(request.node.module.__file__)
    module_name = module_path.stem
    base_dir = module_path.parent

    return base_dir / "testdata" / module_name
