from datetime import date as Date

import pydantic
import pytest

from rendercv.renderer.templater.model_processor import process_fields, process_model
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.cv.entries.normal import NormalEntry
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.settings.settings import Settings


@pytest.fixture
def recorder():
    """Return a processor function and a list tracking all values it has processed.

    Used to verify which fields get processed and in what order.
    """
    seen = []

    def fn(v: str) -> str:
        seen.append(v)
        return f"processed-{v}"

    return fn, seen


class TestProcessFields:
    def test_applies_processors_in_order(self):
        processors = [lambda s: s.upper(), lambda s: f"{s}!"]
        result = process_fields("content", processors)
        assert result == "CONTENT!"

    def test_processes_fields_and_mutates_entry(self, recorder):
        fn, seen = recorder

        entry = NormalEntry.model_validate(
            {
                "name": "Entry",
                "summary": "hello",
                "highlights": ["a", "b"],
                "start_date": "2020-01-01",
                "end_date": "2020-02-01",
                "location": "Remote",
            }
        )

        process_fields(entry, [fn])

        assert "hello" in seen
        assert "a" in seen
        assert "b" in seen
        assert "Remote" in seen

        assert "2020-01-01" not in seen
        assert "2020-02-01" not in seen
        assert entry.summary == "processed-hello"
        assert entry.highlights == ["processed-a", "processed-b"]
        assert entry.location == "processed-Remote"

        assert entry.start_date == "2020-01-01"
        assert entry.end_date == "2020-02-01"

    def test_converts_non_string_non_list_fields_to_string(self, recorder):
        class EntryWithInt(pydantic.BaseModel):
            name: str
            count: int

        fn, seen = recorder
        entry = EntryWithInt(name="Test", count=42)

        process_fields(entry, [fn])  # ty: ignore[invalid-argument-type]

        assert "Test" in seen
        assert "42" in seen
        assert entry.name == "processed-Test"
        assert entry.count == "processed-42"


@pytest.fixture(params=[["Python", "Remote"], []])
def model(request: pytest.FixtureRequest) -> RenderCVModel:
    """Return a test RenderCVModel with keywords either set or empty.

    Parametrized to test both with and without bold keywords.
    """
    cv_data = {
        # Order matters for connections
        "name": "Jane Doe @",
        "headline": "Software Engineer @",
        "email": "jane@example.com",
        "website": "https://janedoe.dev",
        "sections": {
            "Professional Experience": [
                {
                    "name": "Backend Work",
                    "summary": "Built Python services with *markdown* emphasis.",
                    "highlights": ["Improved Python performance"],
                    "start_date": "2022-01-01",
                    "end_date": "2023-02-01",
                    "location": "Remote",
                }
            ]
        },
    }
    cv = Cv.model_validate(cv_data)

    rendercv_model = RenderCVModel(
        cv=cv, settings=Settings(current_date=Date(2024, 2, 1))
    )
    rendercv_model.settings.bold_keywords = request.param

    return rendercv_model


class TestProcessModel:
    def test_markdown_output_has_correct_structure(self, model):
        result = process_model(model, "markdown")

        assert result.cv.name == "Jane Doe @"
        assert result.cv.headline == "Software Engineer @"

        # Connections and last updated date are added to cv
        assert result.cv._connections == [
            "[jane@example.com](mailto:jane@example.com)",
            "[janedoe.dev](https://janedoe.dev/)",
        ]
        assert result.cv._top_note == "*Last updated in Feb 2024*"

        entry = result.cv.rendercv_sections[0].entries[0]
        assert entry.main_column.startswith("**Backend Work**")
        if model.settings.bold_keywords:
            assert (
                "Built **Python** services with *markdown* emphasis."
                in entry.main_column
            )
            assert "- Improved **Python** performance" in entry.main_column
            # DATE placeholder removed because it's not provided; location remains
            assert entry.date_and_location_column == "**Remote**\nJan 2022 – Feb 2023"
        else:
            assert (
                "Built Python services with *markdown* emphasis." in entry.main_column
            )
            assert "- Improved Python performance" in entry.main_column
            assert entry.date_and_location_column == "Remote\nJan 2022 – Feb 2023"

    def test_typst_output_escapes_special_characters(self, model):
        result = process_model(model, "typst")

        assert result.cv.name == "Jane Doe \\@"
        assert result.cv.headline == "Software Engineer \\@"

        entry = result.cv.rendercv_sections[0].entries[0]
        assert entry.main_column.startswith("#strong[Backend Work]")
        if model.settings.bold_keywords:
            assert "- Improved #strong[Python] performance" in entry.main_column
            assert (
                entry.date_and_location_column == "#strong[Remote]\nJan 2022 – Feb 2023"
            )
            # Connections rendered as Typst links with icons by default
            assert result.cv._connections[0].startswith("#link(")
            assert "#connection-with-icon" in result.cv._connections[0]
        else:
            assert "- Improved Python performance" in entry.main_column
            assert entry.date_and_location_column == "Remote\nJan 2022 – Feb 2023"
            assert result.cv._connections[0].startswith("#link(")
            assert "jane@example.com" in result.cv._connections[0]

    def test_handles_cv_with_no_sections(self):
        cv_data = {
            "name": "Jane Doe",
            "headline": "Software Engineer",
        }
        cv = Cv.model_validate(cv_data)
        rendercv_model = RenderCVModel(cv=cv)

        result = process_model(rendercv_model, "markdown")

        assert result.cv.name == "Jane Doe"
        assert result.cv.headline == "Software Engineer"

    def test_pdf_title_default_placeholder_resolution(self, model):
        result = process_model(model, "typst")

        assert result.settings.pdf_title == "Jane Doe @ - CV"

    def test_pdf_title_custom_placeholder_resolution(self):
        cv = Cv.model_validate({"name": "John Doe"})
        rendercv_model = RenderCVModel(
            cv=cv, settings=Settings(current_date=Date(2024, 3, 15))
        )
        rendercv_model.settings.pdf_title = "NAME - Resume YEAR"

        result = process_model(rendercv_model, "typst")

        assert result.settings.pdf_title == "John Doe - Resume 2024"
