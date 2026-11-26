"""Wraps the rendercv core pipeline for the web API.

Why:
    The API must reuse the core's validation and rendering logic exactly as
    the CLI does (`rendercv.cli.render_command.run_rendercv`), rather than
    reimplementing YAML parsing, pydantic validation, or Typst/PDF
    generation. See docs/plans/completed/cv-editor-web-app.md, Phase 0.
"""

import pathlib
import tempfile
from dataclasses import dataclass

from rendercv.exception import RenderCVUserError
from rendercv.renderer.pdf_png import generate_pdf, generate_png
from rendercv.renderer.typst import generate_typst
from rendercv.schema.rendercv_model_builder import build_rendercv_dictionary_and_model


@dataclass(slots=True)
class CvDocuments:
    """The four YAML documents that make up one CV editor session.

    Why:
        Mirrors the four-tab editor model (CV, Design, Locale, Settings)
        from the web app plan, and is the single shape threaded through
        validation, rendering, and caching.
    """

    cv_yaml: str
    design_yaml: str
    locale_yaml: str
    settings_yaml: str


def blank_to_none(yaml_text: str) -> str | None:
    """Treat a whitespace-only overlay document as "not provided".

    Why:
        The core's overlay merging (`build_rendercv_dictionary`) expects
        `None` for an absent overlay; a blank editor tab would otherwise be
        parsed as YAML and fail with a confusing error.

    Args:
        yaml_text: Raw overlay document text.

    Returns:
        None if the document is blank, otherwise the original text.
    """
    return yaml_text if yaml_text.strip() else None


def validate_documents(documents: CvDocuments) -> None:
    """Validate the four YAML documents via the core pipeline.

    Why:
        Reuses `build_rendercv_dictionary_and_model` so validation errors
        (including YAML syntax errors) carry the same structured
        location/message data the CLI displays.

    Args:
        documents: The four YAML documents to validate.

    Raises:
        RenderCVUserValidationError: If any document fails validation.
    """
    build_rendercv_dictionary_and_model(
        documents.cv_yaml,
        design_yaml_file=blank_to_none(documents.design_yaml),
        locale_yaml_file=blank_to_none(documents.locale_yaml),
        settings_yaml_file=blank_to_none(documents.settings_yaml),
    )


def render_documents_to_pngs(documents: CvDocuments) -> list[bytes]:
    """Render the four YAML documents to one PNG per page.

    Why a list rather than a single image: a CV is as long as it is, and
    handing back only the first page would silently lose the rest of
    somebody's work. The caller decides how to package them.

    Args:
        documents: The four YAML documents to render.

    Returns:
        The pages, in order, as PNG file contents.

    Raises:
        RenderCVUserValidationError: If the documents fail validation.
        RenderCVUserError: If rendering fails for a user-facing reason, e.g.
            the settings document disables Typst or PNG generation.
    """
    with tempfile.TemporaryDirectory(prefix="rendercv-web-png-") as temp_dir:
        input_file_path = pathlib.Path(temp_dir) / "cv.yaml"
        _, model = build_rendercv_dictionary_and_model(
            documents.cv_yaml,
            design_yaml_file=blank_to_none(documents.design_yaml),
            locale_yaml_file=blank_to_none(documents.locale_yaml),
            settings_yaml_file=blank_to_none(documents.settings_yaml),
            input_file_path=input_file_path,
            dont_generate_markdown=True,
            dont_generate_html=True,
            # The one difference from the PDF path, and the reason this
            # function exists: the core defaults to skipping PNGs because the
            # preview never needed them.
            dont_generate_png=False,
        )
        typst_path = generate_typst(model)
        png_paths = generate_png(model, typst_path)
        if not png_paths:
            message = (
                "Cannot render images: the settings document disables Typst or"
                " PNG generation (dont_generate_typst / dont_generate_png)."
            )
            raise RenderCVUserError(message=message)
        return [path.read_bytes() for path in png_paths]


def render_documents_to_pdf(documents: CvDocuments) -> bytes:
    """Render the four YAML documents to PDF bytes via the core pipeline.

    Why:
        Mirrors the minimal pipeline in `run_rendercv.py` (build model,
        generate Typst, compile PDF) but renders into a scratch temporary
        directory and returns bytes instead of writing to a user-chosen
        path, since the web API has no filesystem of its own to offer.

    Args:
        documents: The four YAML documents to render.

    Returns:
        Compiled PDF file contents.

    Raises:
        RenderCVUserValidationError: If the documents fail validation.
        RenderCVUserError: If rendering fails for a user-facing reason, e.g.
            the settings document disables PDF or Typst generation.
    """
    with tempfile.TemporaryDirectory(prefix="rendercv-web-") as temp_dir:
        input_file_path = pathlib.Path(temp_dir) / "cv.yaml"
        _, model = build_rendercv_dictionary_and_model(
            documents.cv_yaml,
            design_yaml_file=blank_to_none(documents.design_yaml),
            locale_yaml_file=blank_to_none(documents.locale_yaml),
            settings_yaml_file=blank_to_none(documents.settings_yaml),
            input_file_path=input_file_path,
            dont_generate_markdown=True,
            dont_generate_html=True,
            dont_generate_png=True,
        )
        typst_path = generate_typst(model)
        pdf_path = generate_pdf(model, typst_path)
        if pdf_path is None:
            message = (
                "Cannot render a PDF: the settings document disables Typst or"
                " PDF generation (dont_generate_typst / dont_generate_pdf)."
            )
            raise RenderCVUserError(message=message)
        return pdf_path.read_bytes()
