"""Tests for the pdf_png module."""

import pathlib
import shutil

import pytest

from rendercv.renderer.pdf_png import generate_pdf, generate_png
from rendercv.renderer.typst import generate_typst
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.rendercv_model import RenderCVModel


@pytest.mark.parametrize("theme", available_themes)
@pytest.mark.parametrize("cv_variant", ["minimal", "full"])
def test_generate_pdf(
    compare_file_with_reference,
    theme: str,
    cv_variant: str,
    request: pytest.FixtureRequest,
):
    """Test generate_pdf with all themes and CV variants."""
    base_model = request.getfixturevalue(f"{cv_variant}_rendercv_model")

    model = RenderCVModel(
        cv=base_model.cv,
        design={"theme": theme},
        locale=base_model.locale,
        settings=base_model.settings,
    )

    def generate_file(output_path):
        # Generate typst first
        model.settings.render_command.typst_path = output_path.with_suffix(".typ")
        typst_path = generate_typst(model)

        # Copy lib.typ to output directory (required for compilation)
        lib_source = pathlib.Path("lib.typ")
        if lib_source.exists():
            shutil.copy(lib_source, output_path.parent / "lib.typ")

        # Generate PDF
        model.settings.render_command.pdf_path = output_path
        generate_pdf(model, typst_path)

    reference_filename = f"{theme}_{cv_variant}.pdf"

    assert compare_file_with_reference(generate_file, reference_filename)


@pytest.mark.parametrize("theme", available_themes)
@pytest.mark.parametrize("cv_variant", ["minimal", "full"])
def test_generate_png(
    compare_file_with_reference,
    theme: str,
    cv_variant: str,
    request: pytest.FixtureRequest,
):
    """Test generate_pdf with all themes and CV variants."""
    base_model = request.getfixturevalue(f"{cv_variant}_rendercv_model")

    model = RenderCVModel(
        cv=base_model.cv,
        design={"theme": theme},
        locale=base_model.locale,
        settings=base_model.settings,
    )

    def generate_file(output_path):
        # Generate typst first
        model.settings.render_command.typst_path = output_path.with_suffix(".typ")
        typst_path = generate_typst(model)

        # Copy lib.typ to output directory (required for compilation)
        lib_source = pathlib.Path("lib.typ")
        if lib_source.exists():
            shutil.copy(lib_source, output_path.parent / "lib.typ")

        # Generate PDF
        model.settings.render_command.png_path = output_path
        generate_png(model, typst_path)

    reference_filename = f"{theme}_{cv_variant}.png"

    assert compare_file_with_reference(generate_file, reference_filename)
