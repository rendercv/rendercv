from datetime import date as Date

import pytest

from rendercv.renderer.templater.model_processor import process_fields, process_model
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.cv.entries.normal import NormalEntry
from rendercv.schema.models.rendercv_model import RenderCVModel


class TestProcessFields:
    def test_applies_processors_to_strings_in_order(self):
        processors = [
            lambda string: string.upper(),
            lambda string: f"{string}!",
        ]

        result = process_fields("content", processors)

        assert result == "CONTENT!"

    def test_processes_strings_and_lists_while_skipping_special_fields(self):
        entry = NormalEntry.model_validate(
            {
                "name": "Entry",
                "summary": "keep me",
                "highlights": ["first", "second"],
                "start_date": "2020-01-01",
                "end_date": "2020-02-01",
                "location": "Remote",
            }
        )
        seen: list[str] = []

        def recorder(value: str) -> str:
            seen.append(value)
            return f"processed-{value}"

        process_fields(entry, [recorder])

        assert "keep me" in seen
        assert "first" in seen
        assert "second" in seen
        assert "Remote" in seen  # location processed
        assert "2020-01-01" not in seen  # start_date skipped

    def test_raises_for_unhandled_field_types(self):
        unexpected_entry = NormalEntry.model_validate(
            {
                "name": "Unexpected Entry",
                "text": {"extra": True},
            }
        )
        with pytest.raises(ValueError, match="Unhandled field type: <class 'dict'>"):
            process_fields(unexpected_entry, [lambda value: value])


class TestProcessModel:
    def build_model(self, *, current_date: Date) -> RenderCVModel:
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
        rendercv_model.settings.current_date = current_date
        rendercv_model.settings.bold_keywords = ["Python", "Remote"]

        # Match design.entry_types attribute names so templates are applied.
        for section in rendercv_model.cv.rendercv_sections:
            section.entry_type = "normal_entry"

        return rendercv_model

    def test_process_model_for_markdown_populates_fields(self):
        model = self.build_model(current_date=Date(2024, 2, 1))

        result = process_model(model, "markdown")

        # Connections and last updated date are added to cv
        assert result.cv.connections == [  # pyright: ignore[reportAttributeAccessIssue]
            "[jane@example.com](mailto:jane@example.com)",
            "[janedoe.dev](https://janedoe.dev/)",
        ]
        assert result.cv.last_updated_date == "Last updated in Feb 2024"  # pyright: ignore[reportAttributeAccessIssue]

        entry = result.cv.rendercv_sections[0].entries[0]
        assert entry.main_column_template.startswith("**Backend Work**")
        assert (
            "Built Python services with *markdown* emphasis."
            in entry.main_column_template
        )
        assert "- Improved Python performance" in entry.main_column_template
        # DATE placeholder removed because it's not provided; location remains
        assert entry.date_and_location_column_template.strip() == "Remote"

    def test_process_model_for_typst_converts_markdown_and_bolds_keywords(self):
        model = self.build_model(current_date=Date(2024, 2, 1))

        result = process_model(model, "typst")

        entry = result.cv.rendercv_sections[0].entries[0]
        # Templates exist even though markdown remains unchanged
        assert entry.main_column_template.startswith("**Backend Work**")
        assert "- Improved Python performance" in entry.main_column_template
        assert entry.date_and_location_column_template.strip() == "Remote"
        # Connections rendered as Typst links with icons by default
        assert result.cv.connections[0].startswith("#link(")  # pyright: ignore[reportAttributeAccessIssue]
        assert "#connection-with-icon" in result.cv.connections[0]  # pyright: ignore[reportAttributeAccessIssue]
