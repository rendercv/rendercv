import contextlib
import functools
import pathlib
from typing import Literal

import jinja2

from rendercv.schema.models.rendercv_model import RenderCVModel

from .markup import clean_url, markdown_to_html, typst_string
from .model_processor import process_model
from .rendered import RenderContext, RenderedSection

templates_directory = pathlib.Path(__file__).parent / "templates"
file_extensions: dict[str, str] = {"typst": "typ", "markdown": "md"}


@functools.lru_cache(maxsize=1)
def get_jinja2_environment(
    input_file_path: pathlib.Path | None = None,
) -> jinja2.Environment:
    """Create cached Jinja2 environment with custom filters and template loaders.

    Why:
        Template rendering is called multiple times per render. Caching environment
        prevents repeated filesystem scans. Loader hierarchy enables user template
        overrides by checking input file directory before built-in templates.

    Args:
        input_file_path: Path to input file for user template override resolution.

    Returns:
        Configured Jinja2 environment with filters and loaders.
    """
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            [
                (  # To allow users to override the templates:
                    input_file_path.parent if input_file_path else pathlib.Path.cwd()
                ),
                templates_directory,
            ]
        ),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=jinja2.select_autoescape(["html"], default_for_string=False),
    )
    env.filters["clean_url"] = clean_url
    env.filters["strip"] = lambda string: string.strip()
    env.filters["typst_string"] = typst_string
    env.filters["markdown_heading"] = render_markdown_heading
    return env


def render_markdown_heading(title: str, level: int) -> str:
    """Write a heading, preserving depths beyond Markdown's six heading levels.

    Args:
        title: Heading content in Markdown.
        level: Heading level in the CV's outline.

    Returns:
        A Markdown heading, or an HTML heading with an explicit accessible level.
    """
    if level <= 6:
        return f"{'#' * level} {title}"
    return f'<h6 aria-level="{level}">{markdown_to_html(title, inline=True)}</h6>'


def render_full_template(
    rendercv_model: RenderCVModel, file_type: Literal["typst", "markdown"]
) -> str:
    """Render complete CV document by assembling preamble, header, and sections.

    Why:
        CV generation requires consistent structure across formats. This orchestrates
        model processing, template rendering for each component, and assembly into
        final document following proper order.

    Example:
        ```py
        typst_document = render_full_template(rendercv_model, "typst")
        # Returns complete .typ file with preamble, header, and all sections

        markdown_document = render_full_template(rendercv_model, "markdown")
        # Returns complete .md file with header and all sections
        ```

    Args:
        rendercv_model: CV model to render.
        file_type: Output format for template selection and processing.

    Returns:
        Complete rendered document as string.
    """
    extension = file_extensions[file_type]

    context = process_model(rendercv_model, file_type)

    header = render_single_template(
        file_type,
        f"Header.j2.{extension}",
        context,
    )
    if file_type == "typst":
        preamble = render_single_template(
            file_type,
            f"Preamble.j2.{extension}",
            context,
        )
        code = f"{preamble}\n\n{header}\n"
    else:
        code = f"{header}\n"

    for rendercv_section in context.cv.rendercv_sections:
        code += f"\n{render_section(context, file_type, rendercv_section)}"

    return code


def render_section(
    rendercv_model: RenderContext,
    file_type: Literal["typst", "markdown"],
    section: RenderedSection,
    level: int = 2,
) -> str:
    """Render a section, or a subsection, with its entries.

    Why:
        A subsection is a section one level down, so it is rendered with the
        same templates. Each template gets the heading level of what it renders
        (the name is level 1, sections are 2, subsections are 3, and entries are
        one level below their section), so that headings nest in every format.

    Args:
        rendercv_model: Processed CV model.
        file_type: Output format for template selection.
        section: Section to render.
        level: Heading level of the section.

    Returns:
        Rendered section.
    """
    extension = file_extensions[file_type]
    section_beginning = render_single_template(
        file_type,
        f"SectionBeginning.j2.{extension}",
        rendercv_model,
        section_title=section.title,
        snake_case_section_title=section.snake_case_title,
        entry_type=section.entry_type,
        level=level,
    )
    section_ending = render_single_template(
        file_type,
        f"SectionEnding.j2.{extension}",
        rendercv_model,
        entry_type=section.entry_type,
        level=level,
    )
    if section.entry_type == "SubsectionEntry":
        entry_codes = []
        for subsection in section.entries:
            assert isinstance(subsection, RenderedSection)
            entry_codes.append(
                render_section(rendercv_model, file_type, subsection, level + 1)
            )
    else:
        entry_codes = [
            render_single_template(
                file_type,
                f"entries/{section.entry_type}.j2.{extension}",
                rendercv_model,
                entry=entry,
                level=level + 1,
            )
            for entry in section.entries
        ]
    entries_code = "\n\n".join(entry_codes)
    return f"{section_beginning}\n{entries_code}\n{section_ending}"


def render_html(rendercv_model: RenderCVModel, markdown: str) -> str:
    """Convert Markdown to HTML and wrap with full HTML template.

    Why:
        HTML output requires both content conversion (Markdown to HTML body) and
        document structure (head, CSS, metadata). The HTML document is the Markdown
        document in HTML, so its template sees the model processed for Markdown
        (with the title resolved, for example).

    Example:
        ```py
        markdown_content = render_full_template(rendercv_model, "markdown")
        html_document = render_html(rendercv_model, markdown_content)
        # Returns complete HTML with <head>, CSS, and converted Markdown body
        ```

    Args:
        rendercv_model: CV model for template context.
        markdown: Markdown content to convert.

    Returns:
        Complete HTML document.
    """
    html_body = markdown_to_html(markdown)
    return render_single_template(
        "html",
        "Full.html",
        process_model(rendercv_model, "markdown"),
        html_body=html_body,
    )


def render_single_template(
    file_type: Literal["markdown", "typst", "html"],
    relative_template_path: str,
    rendercv_model: RenderContext,
    **kwargs,
) -> str:
    """Render single Jinja2 template with user override support. Arbitrary keyword
    arguments may be passed to the template as additional template variables.

    Why:
        Users can override built-in templates by placing custom templates in
        theme folder alongside input file. Typst templates check theme-specific
        location first, falling back to built-in templates if not found.

    Example:
        ```py
        header = render_single_template("typst", "Header.j2.typ", rendercv_model)
        # First checks for classic/Header.j2.typ in input file directory
        # Falls back to built-in typst/Header.j2.typ if not found

        section = render_single_template(
            "typst",
            "SectionBeginning.j2.typ",
            rendercv_model,
            section_title="Experience",
        )
        ```

    Args:
        file_type: Format for template directory selection.
        relative_template_path: Template file path relative to format directory.
        rendercv_model: CV model providing template context.

    Returns:
        Rendered template as string.
    """
    jinja2_environment = get_jinja2_environment(rendercv_model._input_file_path)
    template = None
    if file_type == "typst":
        # Try user's own Typst templates first:
        with contextlib.suppress(jinja2.TemplateNotFound):
            template = jinja2_environment.get_template(
                f"{rendercv_model.design.theme}/{relative_template_path}"
            )

    if template is None:
        template = jinja2_environment.get_template(
            f"{file_type}/{relative_template_path}"
        )

    return template.render(
        cv=rendercv_model.cv,
        design=rendercv_model.design,
        locale=rendercv_model.locale,
        settings=rendercv_model.settings,
        entry_layout=jinja2_environment.select_template(
            [
                f"{rendercv_model.design.theme}/EntryLayout.j2.typ",
                "typst/EntryLayout.j2.typ",
            ]
        )
        if file_type == "typst"
        else None,
        **kwargs,
    )
