import pydantic
import pytest

from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.validation_context import ValidationContext


@pytest.mark.parametrize("name", [None, "", "  \n  "])
def test_pdf_ua_requires_a_name_during_validation(name):
    with pytest.raises(pydantic.ValidationError, match="main heading") as error:
        RenderCVModel(cv={"name": name})
    assert error.value.errors()[0]["loc"] == ("cv", "name")


@pytest.mark.parametrize(
    "settings",
    [{"pdf_profile": "standard"}, {"render_command": {"dont_generate_pdf": True}}],
)
def test_unnamed_documents_can_disable_pdf_ua(settings):
    assert RenderCVModel(settings=settings).cv.name is None


@pytest.mark.parametrize(
    "source", ["<<cv.name>>", "((* if cv.name *))", "{% if cv.name %}"]
)
def test_rejects_invalid_templates_during_validation(tmp_path, source):
    templates = tmp_path / "classic"
    templates.mkdir()
    (templates / "Header.j2.typ").write_text(source, encoding="utf-8")
    with pytest.raises(pydantic.ValidationError, match=r"Header\.j2\.typ"):
        RenderCVModel.model_validate(
            {"cv": {"name": "Jane Doe"}},
            context={
                "context": ValidationContext(input_file_path=tmp_path / "cv.yaml")
            },
        )


def test_disabled_markdown_skips_unused_markdown_and_html_templates(tmp_path):
    for folder, filename in [("markdown", "Header.j2.md"), ("html", "Full.html")]:
        (tmp_path / folder).mkdir()
        (tmp_path / folder / filename).write_text("{% broken %}", encoding="utf-8")
    model = RenderCVModel.model_validate(
        {
            "cv": {"name": "Jane Doe"},
            "settings": {"render_command": {"dont_generate_markdown": True}},
        },
        context={"context": ValidationContext(input_file_path=tmp_path / "cv.yaml")},
    )
    assert model.settings.render_command.dont_generate_markdown


def test_ignores_html_files_that_are_not_templates(tmp_path):
    # An `html` folder next to the CV can hold unrelated pages; only `Full.html`
    # is a template:
    (tmp_path / "html").mkdir()
    (tmp_path / "html" / "page.html").write_text("{% broken %}", encoding="utf-8")
    model = RenderCVModel.model_validate(
        {"cv": {"name": "Jane Doe"}},
        context={"context": ValidationContext(input_file_path=tmp_path / "cv.yaml")},
    )
    assert model.cv.name == "Jane Doe"


def test_rejects_an_invalid_html_template(tmp_path):
    (tmp_path / "html").mkdir()
    (tmp_path / "html" / "Full.html").write_text("{% broken %}", encoding="utf-8")
    with pytest.raises(pydantic.ValidationError, match=r"Full\.html"):
        RenderCVModel.model_validate(
            {"cv": {"name": "Jane Doe"}},
            context={
                "context": ValidationContext(input_file_path=tmp_path / "cv.yaml")
            },
        )
