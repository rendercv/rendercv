"""Fixtures for renderer tests."""

import filecmp
import pathlib
import shutil

import pytest

from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.sample_generator import create_sample_rendercv_pydantic_model


def compare_files(file1: pathlib.Path, file2: pathlib.Path) -> bool:
    """Compare two files to check if they are the same.

    For PDFs, compares text content page by page.
    For other files, uses binary comparison.

    Args:
        file1: The first file to compare.
        file2: The second file to compare.

    Returns:
        True if the files are the same, False otherwise.
    """
    if file1.suffix != file2.suffix:
        return False

    # if file1.suffix == ".pdf":
    #     pages1 = pypdf.PdfReader(file1).pages
    #     pages2 = pypdf.PdfReader(file2).pages

    #     if len(pages1) != len(pages2):
    #         return False

    #     for i in range(len(pages1)):
    #         if pages1[i].extract_text() != pages2[i].extract_text():
    #             return False

    #     return True

    return filecmp.cmp(file1, file2, shallow=False)


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

    def _compare(
        callable_func,
        reference_filename: str,
    ) -> bool:
        """Compare generated file with reference.

        Args:
            callable_func: Function that takes output_path and generates a file.
            reference_filename: Name of the reference file in testdata_dir.
                Also used as the output filename.

        Returns:
            True if files match (or if reference was updated), False otherwise.
        """
        # Create temp output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Call the function to generate the file
        generated_path = output_dir / reference_filename
        callable_func(generated_path)

        # Get reference path
        reference_path = testdata_dir / reference_filename

        if not generated_path.exists():
            msg = f"Generated file not found: {generated_path}"
            raise FileNotFoundError(msg)

        if update_testdata:
            # Update reference file
            reference_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(generated_path, reference_path)
            return True

        # Compare files
        if not reference_path.exists():
            msg = (
                f"Reference file not found: {reference_path}. Run with"
                " --update-testdata to generate it."
            )
            raise FileNotFoundError(msg)

        return compare_files(generated_path, reference_path)

    return _compare


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
    return RenderCVModel(cv=cv)


@pytest.fixture
def full_rendercv_model() -> RenderCVModel:
    """Create a full sample RenderCVModel for testing.

    Returns:
        A RenderCVModel with all fields populated using sample data.
    """
    return create_sample_rendercv_pydantic_model(
        name="John Doe",
        theme="classic",
        locale="english",
    )
