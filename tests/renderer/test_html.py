import pytest

from rendercv.renderer.html import generate_html
from rendercv.renderer.markdown import generate_markdown
from rendercv.schema.models.rendercv_model import RenderCVModel


@pytest.mark.parametrize("cv_variant", ["minimal", "full"])
def test_generate_html(
    compare_file_with_reference,
    cv_variant: str,
    request: pytest.FixtureRequest,
):
    base_model = request.getfixturevalue(f"{cv_variant}_rendercv_model")

    model = RenderCVModel(
        cv=base_model.cv,
        locale=base_model.locale,
        settings=base_model.settings,
    )

    def generate_file(output_path):
        model.settings.render_command.markdown_path = output_path.with_suffix(".md")
        markdown_path = generate_markdown(model)

        model.settings.render_command.html_path = output_path
        generate_html(model, markdown_path)

    reference_filename = f"{cv_variant}.html"
    assert compare_file_with_reference(generate_file, reference_filename)
