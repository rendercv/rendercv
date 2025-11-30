import filecmp
import itertools
import pathlib
import shutil
import types
import typing
from datetime import date as Date

import pydantic
import pydantic_extra_types.phone_numbers as pydantic_phone_numbers
import pytest

from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.cv.entries.bullet import BulletEntry
from rendercv.schema.models.cv.entries.education import EducationEntry
from rendercv.schema.models.cv.entries.experience import ExperienceEntry
from rendercv.schema.models.cv.entries.normal import NormalEntry
from rendercv.schema.models.cv.entries.numbered import NumberedEntry
from rendercv.schema.models.cv.entries.one_line import OneLineEntry
from rendercv.schema.models.cv.entries.publication import PublicationEntry
from rendercv.schema.models.cv.entries.reversed_numbered import ReversedNumberedEntry
from rendercv.schema.models.cv.social_network import SocialNetwork
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.settings.settings import Settings


@pytest.fixture
def compare_file_with_reference(
    tmp_path: pathlib.Path, testdata_dir: pathlib.Path, update_testdata: bool
):
    """Generic fixture for comparing generated files with reference files.

    This fixture works with any file type (typst, markdown, PDF, etc.) and supports
    the --update-testdata flag to regenerate reference files.

    Usage:
        def test_something(compare_file_with_reference):
            def generate_file(output_path):
                # Generate your file at output_path
                pass

            assert compare_file_with_reference(
                generate_file,
                "reference.typ"
            )

    Args:
        tmp_path: Pytest fixture providing temporary directory.
        testdata_dir: Fixture providing path to testdata directory.
        update_testdata: Fixture indicating whether to update reference files.

    Returns:
        A callable that takes (callable_func, reference_filename)
        and returns True if files match, False otherwise.
    """

    def compare(callable_func, reference_filename: str) -> bool:
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        output_path_input = output_dir / reference_filename
        callable_func(output_path_input)

        reference_paths = list(
            testdata_dir.glob(f"{output_path_input.stem}*{output_path_input.suffix}")
        )
        generated_paths = list(
            output_dir.glob(f"{output_path_input.stem}*{output_path_input.suffix}")
        )

        if len(generated_paths) == 0:
            msg = f"Output file not found: {output_path_input}"
            raise FileNotFoundError(msg)

        if update_testdata:
            testdata_dir.mkdir(parents=True, exist_ok=True)
            for generated_path in generated_paths:
                shutil.copy(generated_path, testdata_dir / generated_path.name)
            return True

        if not any(reference_paths):
            msg = (
                f"Reference file not found: {reference_filename}. Run with"
                " --update-testdata to generate it."
            )
            raise FileNotFoundError(msg)

        if len(reference_paths) != len(generated_paths):
            msg = (
                f"Number of generated files ({len(generated_paths)}) does not match"
                f" number of reference files ({len(reference_paths)}). Run with"
                " `--update-testdata` to generate the missing files."
            )
            raise FileNotFoundError(msg)

        return any(
            filecmp.cmp(generated_path, reference_path, shallow=False)
            for generated_path, reference_path in zip(
                generated_paths, reference_paths, strict=True
            )
        )

    return compare


@pytest.fixture
def minimal_rendercv_model() -> RenderCVModel:
    """Create a minimal RenderCVModel for testing.

    Returns:
        A RenderCVModel with minimal CV data (name + one section).
    """
    cv = Cv(
        name="John Doe",
        sections={
            "Experience": [
                "Software Engineer at Company X, 2020-2023",
            ]
        },
    )
    return RenderCVModel(cv=cv, settings=Settings(current_date=Date(2025, 11, 30)))


@pytest.fixture
def full_rendercv_model(testdata_dir: pathlib.Path) -> RenderCVModel:
    """Create a comprehensive RenderCVModel with all entry combinations.

    Generates all possible combinations of entry types with different
    optional fields set/unset for comprehensive rendering tests.

    Returns:
        A RenderCVModel with ~400 entry instances across all entry types.
    """
    # Build CV with all sections
    cv = Cv(
        name="John Doe",
        headline="AI Researcher and Entrepreneur",
        location="Istanbul, Turkey",
        email="john_doe@example.com",
        photo=testdata_dir.parent / "profile_picture.jpg",
        phone=pydantic_phone_numbers.PhoneNumber("+905419999999"),
        website=pydantic.HttpUrl("https://example.com"),
        social_networks=[
            SocialNetwork(network="LinkedIn", username="johndoe"),
            SocialNetwork(network="GitHub", username="johndoe"),
            SocialNetwork(network="IMDB", username="nm0000001"),
            SocialNetwork(network="Instagram", username="johndoe"),
            SocialNetwork(network="ORCID", username="0000-0000-0000-0000"),
            SocialNetwork(network="Google Scholar", username="F8IyYrQAAAAJ"),
            SocialNetwork(network="Mastodon", username="@johndoe@example.com"),
            SocialNetwork(network="StackOverflow", username="12323/johndoe"),
            SocialNetwork(network="GitLab", username="johndoe"),
            SocialNetwork(network="ResearchGate", username="johndoe"),
            SocialNetwork(network="YouTube", username="johndoe"),
            SocialNetwork(network="Telegram", username="johndoe"),
            SocialNetwork(network="X", username="johndoe"),
        ],
        sections={
            "Text Entries": [
                (
                    "This is a *TextEntry*. It is only a text and can be useful for"
                    " sections like **Summary**. To showcase the TextEntry completely,"
                    " this sentence is added, but it doesn't contain any information."
                ),
                (
                    "Another text entry with *markdown* and **bold** text. This is the"
                    " second text entry."
                ),
                "Third text with [link](https://example.com) and more content.",
            ],
            "Publication Entries": create_combinations_of_entry_type(PublicationEntry),
            "Experience Entries": create_combinations_of_entry_type(ExperienceEntry),
            "Education Entries": create_combinations_of_entry_type(EducationEntry),
            "Normal Entries": create_combinations_of_entry_type(NormalEntry),
            "One Line Entries": [
                OneLineEntry(
                    label="Programming", details="Python, C++, JavaScript, MATLAB"
                ),
                OneLineEntry(
                    label="Programming", details="Python, C++, JavaScript, MATLAB"
                ),
            ],
            "Bullet Entries": [
                BulletEntry(bullet="This is a bullet entry."),
                BulletEntry(bullet="This is a bullet entry."),
            ],
            "Numbered Entries": [
                NumberedEntry(number="This is a numbered entry."),
                NumberedEntry(number="This is a numbered entry."),
            ],
            "Reversed Numbered Entries": [
                ReversedNumberedEntry(
                    reversed_number="This is a reversed numbered entry."
                ),
                ReversedNumberedEntry(
                    reversed_number="This is a reversed numbered entry."
                ),
                ReversedNumberedEntry(
                    reversed_number="This is a reversed numbered entry."
                ),
            ],
            "A Section & with % Special Characters": [
                NormalEntry(name="A Section & with % Special Characters")
            ],
        },
    )

    return RenderCVModel(cv=cv, settings=Settings(current_date=Date(2025, 11, 30)))


def return_value_for_field(field_name: str, field_type: typing.Any) -> typing.Any:
    """Generate test values for Pydantic model fields based on name and type.

    Returns appropriate test data for a field by checking field name first,
    then handling complex types (Union, Literal, list), and finally falling
    back to type-based defaults.
    """
    field_dictionary = {
        "institution": "Boğaziçi University",
        "location": "Istanbul, Turkey",
        "degree": "BS",
        "area": "Mechanical Engineering",
        "start_date": "2015-09",
        "end_date": "2020-06",
        "date": "2021-09",
        "summary": (
            "Did *this* and this is a **bold** [link](https://example.com). But I must"
            " explain to you how all this mistaken idea of denouncing pleasure and"
            " praising pain was born and I will give you a complete account of the"
            " system, and expound the actual teachings of the great explorer of the"
            " truth, the master-builder of human happiness."
        ),
        "highlights": [
            (
                "Did *this* and this is a **bold** [link](https://example.com). But I"
                " must explain to you how all this mistaken idea of denouncing pleasure"
                " and praising pain was born and I will give you a complete account of"
                " the system, and expound the actual teachings of the great explorer of"
                " the truth, the master-builder of human happiness."
            ),
            (
                "Did that. Nor again is there anyone who loves or pursues or desires to"
                " obtain pain of itself, because it is pain, but because occasionally"
                " circumstances occur in which toil and pain can procure him some great"
                " pleasure. - Nor again is there anyone who loves or pursues or desires"
                " to obtain pain of itself, because it is pain, but because"
                " occasionally circumstances occur in which toil and pain can procure"
                " him some great pleasure. - Nor again is there anyone who loves or"
                " pursues or desires to obtain pain of itself, because it is pain, but"
                " because occasionally circumstances occur in which toil and pain can"
                " procure him some great pleasure."
            ),
            (
                "Did that. Nor again is there anyone who loves or pursues or desires to"
                " obtain pain of itself, because it is pain, but because occasionally"
                " circumstances occur in which toil and pain can procure him some great"
                " pleasure."
            ),
        ],
        "company": "Some Company",
        "position": "Software Engineer",
        "name": "My Project",
        "label": "Pro**gram**ming",
        "details": "Python, C++, JavaScript, MATLAB",
        "authors": [
            "J. Doe",
            "***H. Tom***",
            "S. Doe",
            "A. Andsurname",
            "S. Doe",
            "A. Andsurname",
        ],
        "title": (
            "Magneto-Thermal Thin Shell Approximation for 3D Finite Element Analysis of"
            " No-Insulation Coils"
        ),
        "journal": "IEEE Transactions on Applied Superconductivity",
        "doi": "10.1007/978-3-319-69626-3_101-1",
        "url": "https://example.com",
        "bullet": "This is a bullet entry.",
        "number": "This is a numbered entry.",
        "reversed_number": "This is a reversed numbered entry.",
    }

    field_type_dictionary = {
        pydantic.HttpUrl: "https://example.com",
        pydantic_phone_numbers.PhoneNumber: "+905419999999",
        str: "A test string",
        int: 1,
        float: 1.0,
        bool: True,
    }

    # 1. Check field name first
    if field_name in field_dictionary:
        return field_dictionary[field_name]

    # 2. Get type info
    origin = typing.get_origin(field_type)
    args = typing.get_args(field_type)

    # 3. Handle Union types (including Optional = str | None)
    # Check for both typing.Union and the new union syntax (str | None)
    is_union = origin is typing.Union
    # Python 3.10+ has types.UnionType for the new syntax
    if not is_union and hasattr(typing, "UnionType"):
        is_union = isinstance(field_type, types.UnionType)

    if is_union:
        # Filter out None and recursively handle first non-None type
        non_none_args = [arg for arg in args if arg is not type(None)]
        if non_none_args:
            return return_value_for_field(field_name, non_none_args[0])

    # 4. Handle Literal types (e.g., Literal['present'])
    if origin is typing.Literal:
        return args[0]  # Return first literal value

    # 5. Handle list types
    if origin is list:
        element_type = args[0] if args else str
        if element_type is str:
            return ["Item 1", "Item 2"]
        # For other types, create list with one element
        return [return_value_for_field(field_name, element_type)]

    # 6. Check against type dictionary
    for field_type, value in field_type_dictionary.items():
        if field_type is field_type or field_type == field_type:
            return value
        # Also check if type is in Union args
        if args and field_type in args:
            return value

    message = f"No value found for field {field_name} of type {field_type}"
    raise ValueError(message)


def create_combinations_of_entry_type(
    model: type[pydantic.BaseModel],
    ignore_fields: set[str] | None = None,
) -> list[pydantic.BaseModel]:
    """Generate all combinations of a Pydantic model with different optional fields.

    Creates instances with: only required fields, then all combinations of optional
    fields being set/unset. Used to test rendering with various field combinations.
    """
    ignore_fields = ignore_fields or set()

    required_fields = {}
    optional_fields = {}

    # 1. Categorize fields as required or optional
    for field_name, field_info in model.model_fields.items():
        if field_name in ignore_fields:
            continue

        value = return_value_for_field(field_name, field_info.annotation)

        if field_info.is_required():
            required_fields[field_name] = value
        else:
            optional_fields[field_name] = value

    # 2. Create base instance with only required fields
    model_with_only_required_fields = model(**required_fields)
    all_combinations = [model_with_only_required_fields]

    # 3. Generate all combinations of optional fields
    for i in range(1, len(optional_fields) + 1):
        for combination in itertools.combinations(optional_fields, i):
            # Build kwargs with required + selected optional fields
            kwargs = required_fields.copy()
            kwargs.update({k: optional_fields[k] for k in combination})

            # Create fresh instance (don't mutate existing ones)
            model_instance = model(**kwargs)
            all_combinations.append(model_instance)

    return all_combinations
