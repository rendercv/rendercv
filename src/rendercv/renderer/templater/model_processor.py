from collections.abc import Callable
from typing import Literal

from rendercv.schema.models.cv.section import Entry
from rendercv.schema.models.rendercv_model import RenderCVModel

from .connections import compute_connections
from .date import compute_last_updated_date
from .entry_templates import compute_entry_templates
from .string_processor import make_keywords_bold, markdown_to_typst


def process_fields(
    entry: Entry, string_processors: list[Callable[[str], str]]
) -> Entry:
    skipped_fields = ["start_date", "end_date", "date", "doi", "url"]
    for processor in string_processors:
        if isinstance(entry, str):
            entry = processor(entry)
        else:
            for field_name, field_value in vars(entry).items():
                if field_name in skipped_fields or field_name.startswith("_"):
                    continue

                if isinstance(field_value, str):
                    new_field_value = processor(field_value)
                elif isinstance(field_value, list):
                    new_field_value = [processor(item) for item in field_value]
                else:
                    message = f"Unhandled field type: {type(field_value)}"
                    raise ValueError(message)

                field_value = new_field_value  # NOQA: PLW2901

    return entry


def process_model(
    rendercv_model: RenderCVModel, file_type: Literal["typst", "markdown"]
) -> RenderCVModel:
    string_processors: list[Callable[[str], str]] = [
        lambda string: make_keywords_bold(string, rendercv_model.settings.bold_keywords)
    ]
    if file_type == "typst":
        string_processors.extend([markdown_to_typst])
    elif file_type == "markdown":
        string_processors.extend([])

    rendercv_model.cv.connections = compute_connections(rendercv_model, file_type)  # pyright: ignore[reportAttributeAccessIssue]
    rendercv_model.cv.last_updated_date = compute_last_updated_date(  # pyright: ignore[reportAttributeAccessIssue]
        rendercv_model.locale,
        rendercv_model.settings.current_date,
        rendercv_model.cv.name,
    )
    if rendercv_model.cv.sections is None:
        return rendercv_model

    sections_to_show_time_spans = [
        section.title.lower().replace(" ", "_")
        for section in rendercv_model.cv.rendercv_sections
    ]

    for section in rendercv_model.cv.rendercv_sections:
        for entry in section.entries:
            entry_options = getattr(
                rendercv_model.design.entry_types,
                section.entry_type,
                None,
            )
            if entry_options:
                show_time_spans = (
                    section.title.lower().replace(" ", "_")
                    in sections_to_show_time_spans
                )
                entry_templates = compute_entry_templates(
                    entry,
                    entry_options,
                    rendercv_model.locale,
                    show_time_spans,
                    rendercv_model.settings.current_date,
                )
                for template_name, template in entry_templates.items():
                    setattr(entry, template_name, template)

            entry = process_fields(  # NOQA: PLW2901
                entry,
                string_processors,
            )

    return rendercv_model
