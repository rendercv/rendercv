import functools
from collections.abc import Callable
from typing import Literal, overload

from rendercv.exception import RenderCVInternalError
from rendercv.schema.models.cv.section import Entry
from rendercv.schema.models.rendercv_model import RenderCVModel

from .connections import compute_connections
from .entry_templates_from_yaml import render_entry_templates
from .footer_and_top_note import render_footer_template, render_top_note_template
from .markdown_parser import markdown_to_typst
from .string_processor import make_keywords_bold


def process_model(
    rendercv_model: RenderCVModel, file_type: Literal["typst", "markdown"]
) -> RenderCVModel:
    string_processors: list[Callable[[str], str]] = [
        lambda string: make_keywords_bold(string, rendercv_model.settings.bold_keywords)
    ]
    if file_type == "typst":
        string_processors.extend([markdown_to_typst])

    rendercv_model.cv.plain_name = rendercv_model.cv.name  # pyright: ignore[reportAttributeAccessIssue]
    rendercv_model.cv.name = apply_string_processors(
        rendercv_model.cv.name, string_processors
    )
    rendercv_model.cv.headline = apply_string_processors(
        rendercv_model.cv.headline, string_processors
    )
    rendercv_model.cv.connections = compute_connections(rendercv_model, file_type)  # pyright: ignore[reportAttributeAccessIssue]
    rendercv_model.cv.top_note = render_top_note_template(  # pyright: ignore[reportAttributeAccessIssue]
        rendercv_model.design.templates.top_note,
        locale=rendercv_model.locale,
        current_date=rendercv_model.settings.current_date,
        name=rendercv_model.cv.name,
        single_date_template=rendercv_model.design.templates.single_date,
    )
    rendercv_model.cv.footer = render_footer_template(  # pyright: ignore[reportAttributeAccessIssue]
        rendercv_model.design.templates.footer,
        locale=rendercv_model.locale,
        current_date=rendercv_model.settings.current_date,
        name=rendercv_model.cv.name,
        single_date_template=rendercv_model.design.templates.single_date,
    )
    if rendercv_model.cv.sections is None:
        return rendercv_model

    sections_to_show_time_spans = [
        section_title.lower().replace(" ", "_")
        for section_title in rendercv_model.design.sections.show_time_spans_in
    ]

    for section in rendercv_model.cv.rendercv_sections:
        section.title = apply_string_processors(section.title, string_processors)
        show_time_span = (
            section.title.lower().replace(" ", "_") in sections_to_show_time_spans
        )
        for i, entry in enumerate(section.entries):
            entry = render_entry_templates(  # NOQA: PLW2901
                entry,
                templates=rendercv_model.design.templates,
                locale=rendercv_model.locale,
                show_time_span=show_time_span,
                current_date=rendercv_model.settings.current_date,
            )
            section.entries[i] = process_fields(entry, string_processors)

    return rendercv_model


def process_fields(
    entry: Entry, string_processors: list[Callable[[str], str]]
) -> Entry:
    skipped = {"start_date", "end_date", "doi", "url"}

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
            raise RenderCVInternalError(message)

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
