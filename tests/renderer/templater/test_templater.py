import pathlib

import pytest

from rendercv.renderer.templater.model_processor import process_model
from rendercv.renderer.templater.rendered import RenderedEntry, RenderedSection
from rendercv.renderer.templater.templater import (
    get_jinja2_environment,
    render_full_template,
    render_html,
    render_markdown_heading,
    render_section,
)
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.rendercv_model import RenderCVModel


def model_with_input_in(
    directory: pathlib.Path, name: str = "John Doe"
) -> RenderCVModel:
    model = RenderCVModel(cv=Cv.model_validate({"name": name}))
    model._input_file_path = directory / "cv.yaml"
    return model


def test_render_full_template_uses_jinja_overrides(tmp_path):
    (tmp_path / "markdown").mkdir()
    (tmp_path / "markdown" / "Header.j2.md").write_text(
        "# {{ cv.name }} << custom >>", encoding="utf-8"
    )
    result = render_full_template(model_with_input_in(tmp_path), "markdown")
    assert result.startswith("# John Doe << custom >>")


class TestRenderHtml:
    def test_escapes_the_title_and_keeps_the_body(self, tmp_path):
        model = model_with_input_in(tmp_path, name="A <b>B</b>")

        html = render_html(model, "**bold**")

        assert "<title>A &lt;b&gt;B&lt;/b&gt; - CV</title>" in html
        assert "<p><strong>bold</strong></p>" in html


def test_get_jinja2_environment_quotes_typst_strings():
    environment = get_jinja2_environment(None)
    template = environment.from_string("{{ value|typst_string }}")

    assert template.render(value='a "b"') == '"a \\"b\\""'


def test_deep_heading_preserves_formatting_and_its_level():
    heading = render_markdown_heading("**First Author**", 8)
    assert 'aria-level="8"' in heading
    assert "<strong>First Author</strong>" in heading


class TestRenderSection:
    section = RenderedSection(
        key="",
        title="Publications",
        entry_type="SubsectionEntry",
        entries=(
            RenderedSection(
                key="",
                title="Preprints",
                entry_type="ReversedNumberedEntry",
                entries=(RenderedEntry({"reversed_number": "A preprint."}),),
            ),
            RenderedSection(
                key="", title="Talks", entry_type="TextEntry", entries=("A talk.",)
            ),
        ),
    )

    def test_renders_subsections_as_headings_one_level_down(self, tmp_path):
        markdown = render_section(
            process_model(model_with_input_in(tmp_path), "markdown"),
            "markdown",
            self.section,
        )

        assert markdown.splitlines()[0] == "## Publications"
        assert "### Preprints" in markdown
        assert "### Talks" in markdown

    def test_renders_the_entries_of_each_subsection_with_its_entry_type(self, tmp_path):
        typst = render_section(
            process_model(model_with_input_in(tmp_path), "typst"), "typst", self.section
        )

        assert typst.startswith("== Publications\n")
        preprints = typst.index("=== Preprints")
        talks = typst.index("=== Talks")
        # Only the reversed numbered entries are wrapped:
        assert preprints < typst.index("#reversed-numbered-entries(") < talks
        assert typst.count("#reversed-numbered-entries(") == 1


@pytest.mark.parametrize("output_format", ["typst", "markdown"])
def test_sb2nov_uses_the_localized_degree_phrase(output_format):
    model = RenderCVModel.model_validate(
        {
            "cv": {
                "name": "Jane Doe",
                "sections": {
                    "education": [
                        {
                            "institution": "Universidad",
                            "degree": "Licenciatura",
                            "area": "Física",
                        }
                    ]
                },
            },
            "design": {"theme": "sb2nov"},
            "locale": {"language": "spanish"},
        }
    )
    source = render_full_template(model, output_format)
    assert "Licenciatura en Física" in source
    assert " in " not in source


@pytest.mark.parametrize("theme", available_themes)
@pytest.mark.parametrize("output_format", ["typst", "markdown"])
def test_education_degree_appears_once_in_every_theme(theme, output_format):
    model = RenderCVModel.model_validate(
        {
            "cv": {
                "name": "Jane Doe",
                "sections": {
                    "education": [
                        {
                            "institution": "Example University",
                            "degree": "BSc",
                            "area": "Physics",
                        }
                    ]
                },
            },
            "design": {"theme": theme},
        }
    )
    source = render_full_template(model, output_format)
    assert source.count("BSc") == 1
