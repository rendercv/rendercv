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
    base_model = request.getfixturevalue(f"{cv_variant}_rendercv_model")

    model = RenderCVModel(
        cv=base_model.cv,
        design={"theme": theme},
        locale=base_model.locale,
        settings=base_model.settings,
    )

    def generate_file(output_path):
        model.settings.render_command.typst_path = output_path
        generate_typst(model)

    reference_filename = f"{theme}_{cv_variant}.typ"
    assert compare_file_with_reference(generate_file, reference_filename)


def test_generate_typst_with_dont_generate_typst_returns_temp_path(
    minimal_rendercv_model: RenderCVModel,
):
    """Test that generate_typst returns a temp path when dont_generate_typst is True.

    This ensures PDF/PNG generation can still work even when user doesn't want to
    save the typst file (fixes issue #550).
    """
    model = RenderCVModel(
        cv=minimal_rendercv_model.cv,
        design={"theme": "classic"},
        locale=minimal_rendercv_model.locale,
        settings=minimal_rendercv_model.settings,
    )
    model.settings.render_command.dont_generate_typst = True

    typst_path = generate_typst(model)

    # Should return a valid path, not None
    assert typst_path is not None
    assert typst_path.exists()
    assert typst_path.suffix == ".typ"
    # Verify it contains valid typst content
    content = typst_path.read_text()
    assert "#import" in content or "John Doe" in content
