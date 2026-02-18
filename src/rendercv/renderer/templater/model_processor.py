from collections.abc import Callable
from typing import Literal

from rendercv.schema.models.cv.section import Entry
from rendercv.schema.models.rendercv_model import RenderCVModel

from .connections import compute_connections
from .date import build_date_placeholders, date_object_to_string
from .entry_templates_from_input import render_entry_templates
from .footer_and_top_note import render_footer_template, render_top_note_template
from .markdown_parser import markdown_to_typst
from .string_processor import (
    apply_string_processors,
    make_keywords_bold,
    substitute_placeholders,
)


def process_model(
    rendercv_model: RenderCVModel, file_type: Literal["typst", "markdown"]
) -> RenderCVModel:
    """Pre-process CV model for template rendering with format-specific transformations.

    Why:
        Templates need processed data, not raw model. This applies markdown
        parsing, keyword bolding, connection formatting, date rendering, and
        entry template expansion before templates execute.

    Args:
        rendercv_model: Validated CV model.
        file_type: Target format for format-specific processors.

    Returns:
        Processed model ready for templates.
    """
    rendercv_model = rendercv_model.model_copy(deep=True)

    string_processors: list[Callable[[str], str]] = [
        lambda string: make_keywords_bold(string, rendercv_model.settings.bold_keywords)
    ]
    if file_type == "typst":
        string_processors.extend([markdown_to_typst])

    rendercv_model.cv._plain_name = rendercv_model.cv.name
    rendercv_model.cv.name = apply_string_processors(
        rendercv_model.cv.name, string_processors
    )
    rendercv_model.cv.headline = apply_string_processors(
        rendercv_model.cv.headline, string_processors
    )
    rendercv_model.cv._connections = compute_connections(rendercv_model, file_type)
    rendercv_model.cv._top_note = render_top_note_template(
        rendercv_model.design.templates.top_note,
        locale=rendercv_model.locale,
        current_date=rendercv_model.settings._resolved_current_date,
        name=rendercv_model.cv.name,
        single_date_template=rendercv_model.design.templates.single_date,
        string_processors=string_processors,
    )

    rendercv_model.cv._footer = render_footer_template(
        rendercv_model.design.templates.footer,
        locale=rendercv_model.locale,
        current_date=rendercv_model.settings._resolved_current_date,
        name=rendercv_model.cv.name,
        single_date_template=rendercv_model.design.templates.single_date,
        string_processors=string_processors,
    )

    pdf_title_placeholders: dict[str, str] = {
        "CURRENT_DATE": date_object_to_string(
            rendercv_model.settings._resolved_current_date,
            locale=rendercv_model.locale,
            single_date_template=rendercv_model.design.templates.single_date,
        ),
        "NAME": rendercv_model.cv._plain_name or "",
        **build_date_placeholders(
            rendercv_model.settings._resolved_current_date, locale=rendercv_model.locale
        ),
    }
    rendercv_model.settings.pdf_title = substitute_placeholders(
        rendercv_model.settings.pdf_title, pdf_title_placeholders
    )

    if rendercv_model.cv.sections is None:
        return rendercv_model

    for section in rendercv_model.cv.rendercv_sections:
        section.title = apply_string_processors(section.title, string_processors)
        show_time_span = (
            section.snake_case_title
            in rendercv_model.design.sections.show_time_spans_in
        )
        for i, entry in enumerate(section.entries):
            entry = render_entry_templates(  # NOQA: PLW2901
                entry,
                templates=rendercv_model.design.templates,
                locale=rendercv_model.locale,
                show_time_span=show_time_span,
                current_date=rendercv_model.settings._resolved_current_date,
            )
            section.entries[i] = process_fields(entry, string_processors)

    return rendercv_model


def process_fields(
    entry: Entry, string_processors: list[Callable[[str], str]]
) -> Entry:
    """Apply string processors to all entry fields except skipped technical fields.

    Why:
        Entry fields need markdown parsing and formatting, but dates, DOIs, and
        URLs must remain unprocessed for correct linking and formatting. Field-
        level processing enables selective transformation.

    Args:
        entry: Entry to process (model or string).
        string_processors: Transformation functions to apply.

    Returns:
        Entry with processed fields.
    """
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
            setattr(
                entry, field, apply_string_processors(str(value), string_processors)
            )

    return entry
