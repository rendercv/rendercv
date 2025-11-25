"""Fixtures for renderer tests."""

import filecmp
import pathlib
import shutil

import pytest

from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.sample_generator import create_sample_rendercv_pydantic_model


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
        output_path_input = output_dir / reference_filename
        callable_func(output_path_input)

        # Get reference path
        reference_paths = list(
            testdata_dir.glob(f"{output_path_input.stem}*{output_path_input.suffix}")
        )
        generated_paths = list(
            output_dir.glob(f"{output_path_input.stem}*{output_path_input.suffix}")
        )

        if len(generated_paths) == 0:
            # Maybe multiple files were generated (png)
            msg = f"Output file not found: {output_path_input}"
            raise FileNotFoundError(msg)

        if update_testdata:
            # Update reference file
            testdata_dir.mkdir(parents=True, exist_ok=True)
            for generated_path in generated_paths:
                shutil.copy(generated_path, testdata_dir / generated_path.name)
            return True

        # Compare files
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
