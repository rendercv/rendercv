import functools
import re
from collections.abc import Callable
from typing import Literal, overload

from rendercv.schema.models.cv.section import Entry
from rendercv.schema.models.rendercv_model import RenderCVModel

from .connections import compute_connections
from .date import compute_last_updated_date
from .entry_templates import compute_entry_templates
from .markdown_parser import markdown_to_typst
from .string_processor import make_keywords_bold

entry_type_to_snake_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def process_model(
    rendercv_model: RenderCVModel, file_type: Literal["typst", "markdown"]
) -> RenderCVModel:
    string_processors: list[Callable[[str], str]] = [
        lambda string: make_keywords_bold(string, rendercv_model.settings.bold_keywords)
    ]
    if file_type == "typst":
        string_processors.extend([markdown_to_typst])

    rendercv_model.cv.name = apply_string_processors(
        rendercv_model.cv.name, string_processors
    )
    rendercv_model.cv.headline = apply_string_processors(
        rendercv_model.cv.headline, string_processors
    )
    rendercv_model.cv.connections = compute_connections(rendercv_model, file_type)  # pyright: ignore[reportAttributeAccessIssue]
    rendercv_model.cv.last_updated_date_template = compute_last_updated_date(  # pyright: ignore[reportAttributeAccessIssue]
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
        section.title = apply_string_processors(section.title, string_processors)
        for entry in section.entries:
            # Convert PascalCase to snake_case (e.g., "EducationEntry" -> "education_entry")
            entry_type_snake_case = entry_type_to_snake_case_pattern.sub(
                "_", section.entry_type
            ).lower()

            entry_options = getattr(
                rendercv_model.design.entry_types,
                entry_type_snake_case,
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


def process_fields(
    entry: Entry, string_processors: list[Callable[[str], str]]
) -> Entry:
    skipped = {"start_date", "end_date", "date", "doi", "url"}

    if isinstance(entry, str):
        return apply_string_processors(entry, string_processors)

    data = entry.model_dump(exclude_none=True)
    for field, value in data.items():
        if field in skipped or field.startswith("_"):
            continue

        if isinstance(value, str):
            setattr(entry, field, apply_string_processors(value, string_processors))
        elif isinstance(value, list):
            setattr(
                entry,
                field,
                [apply_string_processors(v, string_processors) for v in value],
            )
        else:
            message = f"Unhandled field type: {type(value)}"
            raise ValueError(message)

    return entry


@overload
def apply_string_processors(
    string: None, string_processors: list[Callable[[str], str]]
) -> None: ...
@overload
def apply_string_processors(
    string: str, string_processors: list[Callable[[str], str]]
) -> str: ...
def apply_string_processors(
    string: str | None, string_processors: list[Callable[[str], str]]
) -> str | None:
    if string is None:
        return string
    return functools.reduce(lambda v, f: f(v), string_processors, string)
