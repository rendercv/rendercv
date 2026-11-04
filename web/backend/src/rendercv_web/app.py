"""FastAPI application exposing the rendercv core as a web service.

Why:
    Phase 0 of the web editor plan: the backend wraps validation and
    rendering from `rendercv` without reimplementing any of it (see
    docs/plans/completed/cv-editor-web-app.md, Approach > Phase 0).
"""

import concurrent.futures
import io
import logging
import os
import zipfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from rendercv.schema.rendercv_model_builder import read_yaml_with_validation_errors

from .cache import cache_key_for, image_cache_key_for, render_cache
from .core import (
    CvDocuments,
    render_documents_to_pdf,
    render_documents_to_pngs,
    validate_documents,
)
from .cvs import router as cvs_router
from .db.migrate import upgrade_to_head
from .documents import apply_patch_ops, to_json_safe
from .errors import register_exception_handlers
from .frontend import mount_frontend
from .limits import enforce_documents_size_cap, enforce_yaml_size_cap
from .models import (
    CvDocumentsRequest,
    ParseRequest,
    ParseResponse,
    PatchRequest,
    PatchResponse,
    ThemeInfo,
    ValidResponse,
)
from .oauth import router as auth_router
from .preferences import router as preferences_router
from .schema import load_schema
from .themes import list_theme_defaults

logger = logging.getLogger("rendercv_web")

RENDER_TIMEOUT_SECONDS = 30.0

ALLOWED_ORIGINS_ENV_VAR = "RENDERCV_WEB_ALLOWED_ORIGINS"
DEFAULT_ALLOWED_ORIGINS = ["http://localhost:5173"]


def resolve_allowed_origins() -> list[str]:
    """Read the browser origins allowed to call this API.

    Why this is configurable rather than a constant: the session cookie is
    sent with `allow_credentials=True`, and a browser refuses to send or
    accept credentialed cross-origin requests unless the origin is listed
    exactly. A deployment whose frontend is served from anywhere other than
    the dev server would therefore silently fail to log in or save
    anything -- with a CORS error in the console as the only clue.

    A deployment serving the frontend and this API from the same origin (a
    reverse proxy putting `/api` on the app's own host) needs no CORS at
    all, and can leave this unset.

    Returns:
        The configured origins, or the dev server's origin when unset.
    """
    configured = os.environ.get(ALLOWED_ORIGINS_ENV_VAR, "")
    origins = [origin.strip() for origin in configured.split(",") if origin.strip()]
    return origins or DEFAULT_ALLOWED_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Bring the target database up to the latest schema before serving.

    Why:
        The dev-DB creation path approved in the plan
        (docs/plans/completed/cv-editor-web-app.md, Phase 4): `uvicorn` must
        start cleanly against a brand-new or behind-head database with no
        manual `alembic upgrade head` step. `upgrade_to_head` is idempotent
        (see `db/migrate.py`), so this runs the same way on every startup
        regardless of whether `RENDERCV_WEB_DATABASE_URL` is set.

    Args:
        app: The FastAPI application (required by the lifespan protocol,
            unused here).
    """
    del app
    upgrade_to_head()
    yield


app = FastAPI(title="RenderCV Web Editor API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=resolve_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(cvs_router)
app.include_router(preferences_router)

# Renders run in a bounded thread pool so a slow Typst compile can be given
# a hard timeout (guardrails: "timeouts on all external calls") instead of
# blocking a request indefinitely.
render_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=4, thread_name_prefix="rendercv-render"
)


def to_documents(request: CvDocumentsRequest) -> CvDocuments:
    """Convert the validated request model into the core wrapper's document shape.

    Args:
        request: The validated request body.

    Returns:
        Equivalent `CvDocuments` for the core wrapper.
    """
    return CvDocuments(
        cv_yaml=request.cv_yaml,
        design_yaml=request.design_yaml,
        locale_yaml=request.locale_yaml,
        settings_yaml=request.settings_yaml,
    )


@app.post("/api/validate", response_model=ValidResponse)
def validate(request: CvDocumentsRequest) -> ValidResponse:
    """Validate the four CV YAML documents via the core pipeline.

    Args:
        request: The four YAML documents to validate.

    Returns:
        `{valid: true}` if validation succeeds.

    Raises:
        HTTPException: 413 if a document exceeds the size cap.
    """
    enforce_documents_size_cap(request.model_dump())
    validate_documents(to_documents(request))
    return ValidResponse()


@app.post("/api/render")
def render(request: CvDocumentsRequest) -> Response:
    """Render the four CV YAML documents to a PDF via the core pipeline.

    Why:
        Renders are cached by sha256 of the four documents (guardrails:
        "cache renders by (yaml-hash, theme)") so repeated identical
        requests skip Typst compilation entirely.

    Args:
        request: The four YAML documents to render.

    Returns:
        `application/pdf` response body with the compiled PDF bytes.

    Raises:
        HTTPException: 413 if a document exceeds the size cap, 504 if the
            render exceeds the timeout.
    """
    enforce_documents_size_cap(request.model_dump())
    documents = to_documents(request)
    key = cache_key_for(documents)

    cached_pdf = render_cache.get(key)
    if cached_pdf is not None:
        return Response(content=cached_pdf, media_type="application/pdf")

    future = render_executor.submit(render_documents_to_pdf, documents)
    try:
        pdf_bytes = future.result(timeout=RENDER_TIMEOUT_SECONDS)
    except concurrent.futures.TimeoutError as e:
        raise HTTPException(status_code=504, detail="Render timed out.") from e

    render_cache.put(key, pdf_bytes)
    return Response(content=pdf_bytes, media_type="application/pdf")


@app.post("/api/render/images")
def render_images(request: CvDocumentsRequest) -> Response:
    """Render the four CV YAML documents to one PNG per page.

    Why the response type varies:
        Most CVs are one page, and handing that back as a zip to be
        unpacked would be worse for the common case. More than one page
        cannot be a bare PNG without losing pages, so those arrive zipped.
        `Content-Type` says which, and the caller needs nothing else.

    Why the pages are not thinned to the first:
        A CV is as long as it is. Returning page one only would look like
        success and quietly drop the rest.

    Args:
        request: The four YAML documents to render.

    Returns:
        `image/png` for a single-page CV, `application/zip` containing
        `page-1.png`, `page-2.png` ... for a longer one.

    Raises:
        HTTPException: 413 if a document exceeds the size cap, 504 if the
            render exceeds the timeout.
    """
    enforce_documents_size_cap(request.model_dump())
    documents = to_documents(request)
    key = image_cache_key_for(documents)

    cached = render_cache.get(key)
    if cached is not None:
        return images_response(cached)

    future = render_executor.submit(render_documents_to_pngs, documents)
    try:
        pages = future.result(timeout=RENDER_TIMEOUT_SECONDS)
    except concurrent.futures.TimeoutError as e:
        raise HTTPException(status_code=504, detail="Render timed out.") from e

    body = pack_pages(pages)
    render_cache.put(key, body)
    return images_response(body)


def pack_pages(pages: list[bytes]) -> bytes:
    """Package rendered pages into the bytes the endpoint returns.

    Args:
        pages: PNG file contents, in page order.

    Returns:
        The single page unchanged, or a zip archive of all of them.
    """
    if len(pages) == 1:
        return pages[0]
    buffer = io.BytesIO()
    # Stored, not deflated: PNG is already compressed, so deflating again
    # buys almost nothing and costs CPU this deployment has little of.
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED) as archive:
        for number, page in enumerate(pages, start=1):
            archive.writestr(f"page-{number}.png", page)
    return buffer.getvalue()


def images_response(body: bytes) -> Response:
    """Label packed pages so the caller knows what it received.

    Args:
        body: The bytes from `pack_pages`.

    Returns:
        A response typed `image/png` or `application/zip`.

    Why the shape is read back off the bytes rather than remembered: the
    cache stores only the body, so a cache hit has to reach the same answer
    as a fresh render from the same information.
    """
    is_zip = body[:2] == b"PK"
    media_type = "application/zip" if is_zip else "image/png"
    return Response(content=body, media_type=media_type)


@app.get("/api/schema")
def schema() -> dict[str, Any]:
    """Serve the repository's root JSON Schema for the form generator.

    Returns:
        Parsed JSON Schema document.
    """
    return load_schema()


@app.get("/api/themes", response_model=list[ThemeInfo])
def themes() -> list[ThemeInfo]:
    """List built-in themes with their default design options.

    Returns:
        One entry per built-in theme (name + default design options).
    """
    return list_theme_defaults()


@app.post("/api/documents/parse", response_model=ParseResponse)
def parse_document(request: ParseRequest) -> ParseResponse:
    """Parse one YAML document into JSON via the core's YAML reader.

    Why:
        Reuses `read_yaml_with_validation_errors` so a YAML syntax error
        here produces exactly the same structured `{errors: [...]}` shape
        `/api/validate` does, with `yaml_source` fixed to
        `"main_yaml_file"` since there's only one document.

    Args:
        request: The YAML document to parse.

    Returns:
        The parsed document as JSON-safe data, top-level key included.

    Raises:
        HTTPException: 413 if the document exceeds the size cap.
    """
    enforce_yaml_size_cap(request.yaml)
    document = read_yaml_with_validation_errors(request.yaml, "main_yaml_file")
    return ParseResponse(data=to_json_safe(document))


@app.post("/api/documents/patch", response_model=PatchResponse)
def patch_document(request: PatchRequest) -> PatchResponse:
    """Apply an ordered list of structural edits to a YAML document.

    Why:
        Backs the form editor's writes into the raw YAML view: comments,
        key order, and quoting style must survive edits made through the
        form, so ops are applied via ruamel's round-trip representation
        instead of re-serializing the document from scratch.

    Args:
        request: The YAML document and the ops to apply to it.

    Returns:
        The updated YAML document.

    Raises:
        HTTPException: 413 if the document exceeds the size cap.
        DocumentPatchError: 400 (via the exception boundary) if any op
            fails; no partial result is returned.
    """
    enforce_yaml_size_cap(request.yaml)
    updated_yaml = apply_patch_ops(request.yaml, request.ops)
    return PatchResponse(yaml=updated_yaml)


# Registered last, and it must stay last: `mount_frontend` adds a catch-all
# route that matches every path, so any endpoint declared after it would be
# unreachable. It is a no-op in development, where Vite serves the frontend
# and proxies `/api` here instead.
mount_frontend(app)
