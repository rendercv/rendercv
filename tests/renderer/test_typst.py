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


@pytest.mark.parametrize("theme", available_themes)
def test_generate_typst_subsections(
    compare_file_with_reference,
    theme: str,
    subsections_rendercv_model: RenderCVModel,
):
    model = RenderCVModel(
        cv=subsections_rendercv_model.cv,
        design={"theme": theme},
        locale=subsections_rendercv_model.locale,
        settings=subsections_rendercv_model.settings,
    )

    def generate_file(output_path):
        model.settings.render_command.typst_path = output_path
        generate_typst(model)

    assert compare_file_with_reference(generate_file, f"{theme}_subsections.typ")


def test_subsection_spacing_is_rendered(
    tmp_path, subsections_rendercv_model: RenderCVModel
):
    model = RenderCVModel(
        cv=subsections_rendercv_model.cv,
        design={
            "theme": "classic",
            "subsection_titles": {
                "space_above": "0.2cm",
                "space_below": "0.1cm",
            },
        },
        locale=subsections_rendercv_model.locale,
        settings=subsections_rendercv_model.settings,
    )

    model.settings.render_command.typst_path = tmp_path / "subsections.typ"
    typst_path = generate_typst(model)

    assert typst_path is not None
    typst_contents = typst_path.read_text(encoding="utf-8")
    assert "#v(0.2cm)" in typst_contents
    assert "#v(0.1cm)" in typst_contents
