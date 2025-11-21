from datetime import date as Date

import pytest

from rendercv.renderer.templater.model_processor import process_fields, process_model
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.cv.entries.normal import NormalEntry
from rendercv.schema.models.rendercv_model import RenderCVModel


@pytest.fixture
def uppercase_then_bang():
    return [
        lambda s: s.upper(),
        lambda s: f"{s}!",
    ]


@pytest.fixture
def recorder():
    seen = []

    def fn(v: str) -> str:
        seen.append(v)
        return f"processed-{v}"

    return fn, seen


class TestProcessFields:
    def test_applies_processors_in_order(self, uppercase_then_bang):
        result = process_fields("content", uppercase_then_bang)
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

    @pytest.mark.parametrize(
        "bad_value",
        [
            {"unexpected": "dict"},
            123,
            3.14,
            object(),
        ],
    )
    def test_raises_for_unhandled_field_types(self, bad_value):
        entry = NormalEntry.model_validate(
            {
                "name": "Test",
                "weird": bad_value,
            }
        )

        with pytest.raises(ValueError, match="Unhandled field type"):
            process_fields(entry, [lambda s: s])


@pytest.fixture(params=[["Python", "Remote"], []])
def model(request: pytest.FixtureRequest) -> RenderCVModel:
    cv_data = {
        # Order matters for connections
        "name": "Jane Doe",
        "email": "jane@example.com",
        "website": "https://janedoe.dev",
        "sections": {
            "Experience": [
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

    rendercv_model = RenderCVModel(cv=cv)
    rendercv_model.settings.current_date = Date(2024, 2, 1)
    rendercv_model.settings.bold_keywords = request.param

    return rendercv_model


class TestProcessModel:
    def test_process_model_for_markdown_populates_fields(self, model):
        result = process_model(model, "markdown")

        # Connections and last updated date are added to cv
        assert result.cv.connections == [  # pyright: ignore[reportAttributeAccessIssue]
            "[jane@example.com](mailto:jane@example.com)",
            "[janedoe.dev](https://janedoe.dev/)",
        ]
        assert result.cv.last_updated_date == "Last updated in Feb 2024"  # pyright: ignore[reportAttributeAccessIssue]

        entry = result.cv.rendercv_sections[0].entries[0]
        assert entry.main_column_template.startswith("**Backend Work**")
        if model.settings.bold_keywords:
            assert (
                "Built **Python** services with *markdown* emphasis."
                in entry.main_column_template
            )
            assert "- Improved **Python** performance" in entry.main_column_template
            # DATE placeholder removed because it's not provided; location remains
            assert entry.date_and_location_column_template.strip() == "**Remote**"
        else:
            assert (
                "Built Python services with *markdown* emphasis."
                in entry.main_column_template
            )
            assert "- Improved Python performance" in entry.main_column_template
            assert entry.date_and_location_column_template.strip() == "Remote"

    def test_process_model_for_typst_converts_markdown_and_bolds_keywords(self, model):
        result = process_model(model, "typst")

        entry = result.cv.rendercv_sections[0].entries[0]
        assert entry.main_column_template.startswith("#strong[Backend Work]")
        if model.settings.bold_keywords:
            assert (
                "- Improved #strong[Python] performance" in entry.main_column_template
            )
            assert entry.date_and_location_column_template.strip() == "#strong[Remote]"
            # Connections rendered as Typst links with icons by default
            assert result.cv.connections[0].startswith("#link(")  # pyright: ignore[reportAttributeAccessIssue]
            assert "#connection-with-icon" in result.cv.connections[0]  # pyright: ignore[reportAttributeAccessIssue]
        else:
            assert "- Improved Python performance" in entry.main_column_template
            assert entry.date_and_location_column_template.strip() == "Remote"
            assert result.cv.connections[0].startswith("#link(")  # pyright: ignore[reportAttributeAccessIssue]
            assert "jane@example.com" in result.cv.connections[0]  # pyright: ignore[reportAttributeAccessIssue]
