"""Tests for the typst module."""

import pytest

from rendercv.renderer.typst import generate_typst
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.rendercv_model import RenderCVModel


@pytest.mark.parametrize("theme", available_themes)
@pytest.mark.parametrize("cv_variant", ["minimal", "full"])
def test_generate_typst(
    compare_file_with_reference,
    theme: str,
    cv_variant: str,
    request: pytest.FixtureRequest,
):
    """Test generate_typst with all themes and CV variants.

    This test compares generated typst files with reference files in testdata.
    Reference files are named: {theme}_{cv_variant}.typ

    Args:
        compare_file_with_reference: Fixture for comparing generated with reference.
        theme: Theme name to test (parametrized over all available themes).
        cv_variant: CV variant to test (minimal or full).
        request: Pytest fixture request for accessing other fixtures dynamically.
    """
    # Get the appropriate CV model fixture
    base_model = request.getfixturevalue(f"{cv_variant}_rendercv_model")

    # Create a new model with the specified theme (using Pydantic validation)
    model = RenderCVModel(
        cv=base_model.cv,
        design={"theme": theme},
        locale=base_model.locale,
        settings=base_model.settings,
    )

    # Define the callable that generates the file
    def generate_file(output_path):
        # Set path so the file is generated at output_path
        model.settings.render_command.typst_path = output_path
        # Generate the typst file
        generate_typst(model)

    # Compare with reference
    reference_filename = f"{theme}_{cv_variant}.typ"

    assert compare_file_with_reference(generate_file, reference_filename)
