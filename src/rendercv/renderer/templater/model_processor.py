from rendercv.document import build_document_placeholders
from rendercv.schema.models.cv.section import BaseRenderCVSection
from rendercv.schema.models.rendercv_model import RenderCVModel

from .connections import compute_connections
from .date import sort_entries
from .entry_templates_from_input import render_entry_templates
from .footer_and_top_note import (
    fill_document_template,
    render_footer_template,
    render_top_note_template,
)
from .markup import Format, Node, bold_keywords, emit, parse_content, plain_text
from .rendered import RenderContext, RenderedCv, RenderedSection


def process_model(
    rendercv_model: RenderCVModel, output_format: Format
) -> RenderContext:
    """Render the content of a CV model in the output format, for its templates.

    Why:
        Jinja templates lay out content that is already rendered: names,
        headlines, connections, section titles, and entries are converted from
        Markdown to the output format, with keywords bolded, exactly once.

    Args:
        rendercv_model: Validated CV model. It is not modified.
        output_format: `"typst"` or `"markdown"`.

    Returns:
        A separate representation whose content is rendered in the output format.
    """
    cv = rendercv_model.cv
    design = rendercv_model.design
    locale = rendercv_model.locale
    settings = rendercv_model.settings
    keywords = settings.bold_keywords
    current_date = settings._resolved_current_date
    placeholders = build_document_placeholders(rendercv_model)

    def render(content: tuple[Node, ...]) -> str:
        return emit(bold_keywords(content, keywords), output_format)

    top_note = render(
        render_top_note_template(
            design.templates.top_note,
            placeholders=placeholders,
            last_updated=locale.last_updated,
        )
    )
    footer = render(
        render_footer_template(design.templates.footer, placeholders=placeholders)
    )
    # Page numbers are known only in the context of each page:
    footer = f"context {{ [{footer}] }}" if output_format == "typst" else footer

    def process_section(
        section: BaseRenderCVSection, *, show_time_span: bool
    ) -> RenderedSection:
        if section.entry_type == "SubsectionEntry":
            entries = tuple(
                process_section(subsection, show_time_span=show_time_span)
                for subsection in section.entries
            )
        else:
            source_entries = section.entries
            if settings.sort_entries != "none":
                source_entries = sort_entries(
                    source_entries,
                    order=settings.sort_entries,
                    current_date=current_date,
                )
            entries = tuple(
                render_entry_templates(
                    entry,
                    templates=design.templates,
                    locale=locale,
                    show_time_span=show_time_span,
                    current_date=current_date,
                    keywords=keywords,
                    output_format=output_format,
                )
                for entry in source_entries
            )
        return RenderedSection(
            title=render(parse_content(section.title)),
            key=section.key,
            entry_type=section.entry_type,
            entries=entries,
        )

    return RenderContext(
        cv=RenderedCv(
            source=cv,
            name=render(parse_content(cv.name)) if cv.name is not None else None,
            headline=render(parse_content(cv.headline))
            if cv.headline is not None
            else None,
            photo=rendercv_model._output_plan.photo,
            rendercv_sections=tuple(
                process_section(
                    section,
                    show_time_span=section.snake_case_title
                    in design.sections.show_time_spans_in,
                )
                for section in cv.rendercv_sections
            ),
            _plain_name=plain_text(parse_content(cv.name)) if cv.name else None,
            _connections=tuple(compute_connections(rendercv_model, output_format)),
            _top_note=top_note,
            _footer=footer,
        ),
        design=design,
        locale=locale,
        # Templates see the title with its placeholders filled, as plain text for the
        # PDF's metadata and the HTML's title:
        settings=settings.model_copy(
            update={
                "pdf_title": plain_text(
                    fill_document_template(settings.pdf_title, placeholders)
                )
            }
        ),
        _input_file_path=rendercv_model._input_file_path,
    )
