from datetime import date as Date

import pydantic
import pytest

from rendercv.renderer.templater.entry_templates_from_input import (
    compute_entry_values,
    process_highlights,
    render_entry_templates,
)
from rendercv.renderer.templater.markup import Format, Link, Text, emit, plain_text
from rendercv.renderer.templater.rendered import RenderedEntry
from rendercv.schema.models.cv.entries.education import EducationEntry
from rendercv.schema.models.cv.entries.experience import ExperienceEntry
from rendercv.schema.models.cv.entries.normal import NormalEntry
from rendercv.schema.models.cv.entries.publication import PublicationEntry
from rendercv.schema.models.cv.section import Entry
from rendercv.schema.models.design.classic_theme import (
    EducationEntryTemplate,
    NormalEntryTemplate,
    PublicationEntryTemplate,
    Templates,
)
from rendercv.schema.models.locale.english_locale import EnglishLocale
from rendercv.schema.models.locale.locale import Locale, locale_adapter


def render(
    entry: Entry,
    *,
    templates: Templates | None = None,
    locale: Locale | None = None,
    show_time_span: bool = False,
    keywords: tuple[str, ...] = (),
    output_format: Format = "markdown",
) -> RenderedEntry | str:
    return render_entry_templates(
        entry,
        templates=templates or Templates(),
        locale=locale or EnglishLocale(),
        show_time_span=show_time_span,
        current_date=Date(2024, 1, 1),
        keywords=keywords,
        output_format=output_format,
    )


@pytest.mark.parametrize(
    ("highlights", "expected"),
    [
        (["Single item"], "- Single item"),
        (["Item 1", "Item 2"], "- Item 1\n- Item 2"),
        (["Parent - Child 1 - Child 2"], "- Parent\n  - Child 1\n  - Child 2"),
        (["**a - b**"], "- #strong[a - b]"),
        (["`a - b`"], "- `a - b`"),
        (["multi\nline"], "- multi\n  line"),
        (["- already a list item"], "- \\- already a list item"),
    ],
)
def test_process_highlights(highlights, expected):
    assert emit(process_highlights(highlights), "typst") == expected


class TestComputeEntryValues:
    def compute(self, entry, *, show_time_span: bool = False):
        return compute_entry_values(
            entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=show_time_span,
            current_date=Date(2024, 1, 1),
            output_format="typst",
        )

    def test_makes_every_scalar_field_a_placeholder(self):
        entry = NormalEntry.model_validate(
            {"name": "Project", "advisor": "Dr. Who", "count": 3}
        )

        values = self.compute(entry)

        assert values["NAME"] == (Text("Project"),)
        assert values["ADVISOR"] == (Text("Dr. Who"),)
        assert values["COUNT"] == (Text("3"),)

    def test_computes_dates_of_a_range(self):
        entry = ExperienceEntry(
            company="Acme",
            position="Engineer",
            start_date="2020-01",
            end_date="2021-02",
        )

        values = self.compute(entry, show_time_span=True)

        assert plain_text(values["DATE"]) == "Jan 2020 – Feb 2021\n\n1 year 2 months"
        assert plain_text(values["START_DATE"]) == "Jan 2020"
        assert plain_text(values["END_DATE"]) == "Feb 2021"

    def test_links_a_publication_doi(self):
        entry = PublicationEntry(
            title="Paper",
            authors=["A", "B"],
            doi="10.1/abc",
            url=pydantic.HttpUrl("https://example.com"),
        )

        values = self.compute(entry)

        expected = (Link("https://doi.org/10.1/abc", (Text("10.1/abc"),)),)
        assert values["DOI"] == values["URL"] == expected
        assert values["AUTHORS"] == (Text("A, B"),)

    def test_links_a_url_with_its_cleaned_text(self):
        entry = NormalEntry.model_validate(
            {"name": "Linked", "url": "https://example.com/path/"}
        )

        values = self.compute(entry)

        assert values["URL"] == (
            Link("https://example.com/path/", (Text("example.com/path"),)),
        )


class TestRenderEntryTemplates:
    def test_renders_a_text_entry(self):
        assert (
            render("Plain text with Python", keywords=("Python",))
            == "Plain text with **Python**"
        )

    def test_renders_default_templates(self):
        entry = NormalEntry(
            name="Project",
            date="2023-05",
            highlights=["Alpha", "Beta"],
            location="Remote",
        )

        entry = render(entry)

        assert entry.main_column == "**Project**\n- Alpha\n- Beta"  # ty: ignore[unresolved-attribute]
        assert entry.date_and_location_column == "Remote\nMay 2023"  # ty: ignore[unresolved-attribute]

    def test_shows_the_time_span_on_its_own_line(self):
        entry = ExperienceEntry(
            company="Acme",
            position="Engineer",
            start_date="2020-01",
            end_date="2021-02",
        )

        entry = render(entry, show_time_span=True)
        assert isinstance(entry, RenderedEntry)

        assert (
            entry.date_and_location_column == "Jan 2020 – Feb 2021\n\n1 year 2 months"
        )

    def test_formats_dates_in_custom_templates(self):
        entry = NormalEntry(
            name="Timeline", start_date="2020-01-01", end_date="2021-03-01"
        )
        templates = Templates(
            normal_entry=NormalEntryTemplate(
                main_column="START_DATE / END_DATE / LOCATION / DATE"
            )
        )

        entry = render(entry, templates=templates)

        assert entry.main_column == "Jan 2020 / Mar 2021 / Jan 2020 – Mar 2021"  # ty: ignore[unresolved-attribute]

    def test_handles_authors_doi_and_unknown_placeholders(self):
        entry = PublicationEntry(
            title="My Paper",
            authors=["Alice", "Bob"],
            doi="10.1000/xyz123",
            date="2024-02-01",
        )
        templates = Templates(
            publication_entry=PublicationEntryTemplate(
                main_column="AUTHORS | DOI | DATE | OPTIONAL"
            )
        )

        entry = render(entry, templates=templates)

        assert entry.main_column == (  # ty: ignore[unresolved-attribute]
            "Alice, Bob | [10.1000/xyz123](https://doi.org/10.1000/xyz123) | Feb 2024"
        )

    @pytest.mark.parametrize(
        ("language", "degree", "area", "expected"),
        [
            ("english", "BS", "Computer Science", "**MIT**, BS in Computer Science"),
            ("french", "Licence", "Informatique", "**MIT**, Licence en Informatique"),
            ("japanese", "BS", "Computer Science", "**MIT**, Computer Science BS"),
            ("english", None, "Computer Science", "**MIT**, Computer Science"),
        ],
    )
    def test_fills_locale_phrases(self, language, degree, area, expected):
        entry = EducationEntry(
            institution="MIT", area=area, degree=degree, date="2024-05"
        )
        templates = Templates(
            education_entry=EducationEntryTemplate(
                main_column="**INSTITUTION**, DEGREE_WITH_AREA", degree_column=None
            )
        )

        entry = render(
            entry,
            templates=templates,
            locale=locale_adapter.validate_python({"language": language}),
        )

        assert entry.main_column == expected  # ty: ignore[unresolved-attribute]

    @pytest.mark.parametrize(
        ("institution", "area", "expected_main_column"),
        [
            ("", "Computer Science", "Computer Science"),
            ("MIT", "", "**MIT**"),
            ("", "", ""),
        ],
    )
    def test_removes_formatting_around_empty_fields(
        self, institution, area, expected_main_column
    ):
        entry = EducationEntry(
            institution=institution, area=area, start_date="2020-01", end_date="2021-01"
        )

        assert render(entry).main_column == expected_main_column  # ty: ignore[unresolved-attribute]

    def test_lays_out_a_summary_as_a_summary_block(self):
        entry = NormalEntry(name="Project", summary="Project description")

        entry = render(entry, output_format="typst")

        assert entry.main_column == "#strong[Project]\n#summary[Project description]"  # ty: ignore[unresolved-attribute]

    def test_keeps_an_inline_summary_inline(self):
        templates = Templates(
            experience_entry=Templates().experience_entry.model_copy(
                update={"main_column": "**COMPANY**, SUMMARY"}
            )
        )
        entry = ExperienceEntry(
            company="Google",
            position="Engineer",
            summary="Built search",
            start_date="2020-01",
            end_date="2021-01",
        )

        entry = render(entry, templates=templates, output_format="typst")

        assert entry.main_column == "#strong[Google], Built search"  # ty: ignore[unresolved-attribute]

    def test_ignores_fields_that_are_not_text(self):
        entry = NormalEntry.model_validate({"name": "RenderCV", "scores": [1, 2]})

        entry = render(entry, output_format="typst")

        assert entry.main_column == "#strong[RenderCV]"  # ty: ignore[unresolved-attribute]
        assert entry.scores == [1, 2]  # ty: ignore[unresolved-attribute]

    def test_renders_fields_for_custom_jinja_templates(self):
        entry = NormalEntry.model_validate(
            {
                "name": "Python project",
                "advisor": "Dr. *Who*",
                "highlights": ["Used Python"],
            }
        )

        entry = render(entry, keywords=("Python",), output_format="typst")

        assert entry.name == "#strong[Python] project"  # ty: ignore[unresolved-attribute]
        assert entry.advisor == "Dr. #emph[Who]"  # ty: ignore[unresolved-attribute]
        assert entry.highlights == ["Used #strong[Python]"]  # ty: ignore[unresolved-attribute]
        assert entry.main_column == "#strong[Python project]\n- Used #strong[Python]"  # ty: ignore[unresolved-attribute]


def test_rendering_an_entry_preserves_validated_input():
    entry = NormalEntry(name="**Research**", date="2020-01", highlights=["C++"])
    before = entry.model_dump()
    for output_format in ("typst", "markdown", "typst"):
        render_entry_templates(
            entry,
            templates=Templates(),
            locale=EnglishLocale(),
            show_time_span=False,
            current_date=Date(2025, 1, 1),
            keywords=["C++"],
            output_format=output_format,
        )
        assert entry.model_dump() == before
