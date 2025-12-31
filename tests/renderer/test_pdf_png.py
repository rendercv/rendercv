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
    base_model = request.getfixturevalue(f"{cv_variant}_rendercv_model")

    model = RenderCVModel(
        cv=base_model.cv,
        design={"theme": theme},
        locale=base_model.locale,
        settings=base_model.settings,
    )

    def generate_file(output_path):
        model.settings.render_command.typst_path = output_path.with_suffix(".typ")
        typst_path, is_temporary = generate_typst(model)
        assert not is_temporary

        model.settings.render_command.pdf_path = output_path
        generate_pdf(model, typst_path)

    reference_filename = f"{theme}_{cv_variant}.pdf"

    assert compare_file_with_reference(generate_file, reference_filename)


@pytest.mark.parametrize("theme", available_themes)
def test_generate_png(
    compare_file_with_reference,
    theme: str,
    minimal_rendercv_model: RenderCVModel,
):
    model = RenderCVModel(
        cv=minimal_rendercv_model.cv,
        design={"theme": theme},
        locale=minimal_rendercv_model.locale,
        settings=minimal_rendercv_model.settings,
    )

    def generate_file(output_path):
        model.settings.render_command.typst_path = output_path.with_suffix(".typ")
        typst_path, is_temporary = generate_typst(model)
        assert not is_temporary

        model.settings.render_command.png_path = output_path
        generate_png(model, typst_path)

    reference_filename = f"{theme}_minimal.png"

    assert compare_file_with_reference(generate_file, reference_filename)


def test_generate_pdf_with_dont_generate_typst(
    tmp_path,
    minimal_rendercv_model: RenderCVModel,
):
    """Test that PDF can still be generated when dont_generate_typst is True.

    This is a regression test for issue #550 where disabling typst generation
    would also disable PDF/PNG generation.
    """
    model = RenderCVModel(
        cv=minimal_rendercv_model.cv,
        design={"theme": "classic"},
        locale=minimal_rendercv_model.locale,
        settings=minimal_rendercv_model.settings,
    )
    model.settings.render_command.dont_generate_typst = True
    model.settings.render_command.pdf_path = tmp_path / "output.pdf"

    # Generate typst (should return temp path with is_temporary=True)
    typst_path, is_temporary = generate_typst(model)
    assert typst_path is not None
    assert is_temporary is True

    try:
        # Generate PDF using the temp typst path
        pdf_path = generate_pdf(model, typst_path)

        assert pdf_path is not None
        assert pdf_path.exists()
        assert pdf_path.suffix == ".pdf"
    finally:
        # Clean up temp directory (as done in run_rendercv.py)
        if is_temporary and typst_path.parent.exists():
            shutil.rmtree(typst_path.parent, ignore_errors=True)


def test_generate_png_with_dont_generate_typst(
    tmp_path,
    minimal_rendercv_model: RenderCVModel,
):
    """Test that PNG can still be generated when dont_generate_typst is True.

    This is a regression test for issue #550 where disabling typst generation
    would also disable PDF/PNG generation.
    """
    model = RenderCVModel(
        cv=minimal_rendercv_model.cv,
        design={"theme": "classic"},
        locale=minimal_rendercv_model.locale,
        settings=minimal_rendercv_model.settings,
    )
    model.settings.render_command.dont_generate_typst = True
    model.settings.render_command.png_path = tmp_path / "output.png"

    # Generate typst (should return temp path with is_temporary=True)
    typst_path, is_temporary = generate_typst(model)
    assert typst_path is not None
    assert is_temporary is True

    try:
        # Generate PNG using the temp typst path
        png_paths = generate_png(model, typst_path)

        assert png_paths is not None
        assert len(png_paths) > 0
        assert all(p.exists() for p in png_paths)
        assert all(p.suffix == ".png" for p in png_paths)
    finally:
        # Clean up temp directory (as done in run_rendercv.py)
        if is_temporary and typst_path.parent.exists():
            shutil.rmtree(typst_path.parent, ignore_errors=True)
