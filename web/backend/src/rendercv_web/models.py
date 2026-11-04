"""Request and response models for the RenderCV Web Editor API.

Why:
    Guardrails ("trust no one"): every request body is validated by a
    pydantic model before it reaches the `rendercv` core pipeline.
"""

from datetime import datetime
from typing import Annotated, Any, Literal

import pydantic

MAX_DOCUMENT_BYTES = 512 * 1024
# Mirrors the `cvs.name` / `preferences.key` column widths in `db/models.py`:
# SQLite ignores VARCHAR lengths but PostgreSQL (the deploy target) raises
# `DataError` on overflow, which the error boundary can only turn into an
# opaque 500 -- so the cap is enforced here, as a 422, before the write.
MAX_CV_NAME_LENGTH = 255
MAX_PREFERENCE_KEY_LENGTH = 128
# `preferences.value` is an unbounded TEXT column, but every value the editor
# stores is small UI state (zoom, theme, split ratio); cap it so a request
# body cannot grow the table without limit.
MAX_PREFERENCE_VALUE_LENGTH = 4096


class CvDocumentsRequest(pydantic.BaseModel):
    """The four YAML documents submitted by the editor's four tabs.

    Why:
        The web editor mirrors the CV, Design, Locale, and Settings tabs
        1:1 with the four YAML documents the core's overlay mechanism
        expects (`build_rendercv_dictionary_and_model`).
    """

    model_config = pydantic.ConfigDict(extra="forbid")

    cv_yaml: str = pydantic.Field(description="The `cv:` YAML document.")
    design_yaml: str = pydantic.Field(
        default="", description="The `design:` YAML document, or empty."
    )
    locale_yaml: str = pydantic.Field(
        default="", description="The `locale:` YAML document, or empty."
    )
    settings_yaml: str = pydantic.Field(
        default="", description="The `settings:` YAML document, or empty."
    )


class ValidationErrorItem(pydantic.BaseModel):
    """One structured validation error with a YAML source location.

    Why:
        Mirrors `rendercv.exception.RenderCVValidationError` so the frontend
        can jump to the exact tab and line that caused the error.
    """

    location: str | None = pydantic.Field(
        description="Dotted schema path (e.g. `cv.sections.education.0.degree`)."
    )
    message: str = pydantic.Field(description="Human-readable error message.")
    yaml_source: str = pydantic.Field(
        description="Which document the error came from (cv/design/locale/settings)."
    )
    yaml_line: int | None = pydantic.Field(
        description="1-indexed line number in the source YAML document, if known."
    )


class ValidationErrorResponse(pydantic.BaseModel):
    """Response body for a failed validation or render request."""

    errors: list[ValidationErrorItem]


class ValidResponse(pydantic.BaseModel):
    """Response body for a successful validation request."""

    valid: bool = True


class InternalErrorResponse(pydantic.BaseModel):
    """Opaque response body for unexpected server errors.

    Why:
        Guardrails ("never leak stack traces"): only an opaque id is
        returned to the client; full details go to the server log.
    """

    error_id: str = pydantic.Field(
        description="Opaque id to correlate with server logs."
    )
    message: str = "An unexpected error occurred. Please try again."


class ThemeInfo(pydantic.BaseModel):
    """One built-in theme's name and default design options."""

    name: str
    design_defaults: dict[str, Any]


class ParseRequest(pydantic.BaseModel):
    """Request body for `POST /api/documents/parse`."""

    model_config = pydantic.ConfigDict(extra="forbid")

    yaml: str = pydantic.Field(description="A single YAML document string.")


class ParseResponse(pydantic.BaseModel):
    """Response body for a successful `POST /api/documents/parse`.

    Why:
        `data` is the whole parsed mapping, top-level key included (e.g.
        `{"cv": {...}}`), so the frontend can address it with the same
        dotted paths the schema and validation errors use.
    """

    data: Any = pydantic.Field(description="The parsed document as JSON-safe data.")


class SetOp(pydantic.BaseModel):
    """Set or replace the value at `path`.

    Why:
        The final path element is created if it names a missing mapping
        key; every element before it must already exist, so a client can't
        silently create deep structure by accident.
    """

    model_config = pydantic.ConfigDict(extra="forbid")

    op: Literal["set"]
    path: list[str | int]
    value: Any


class InsertOp(pydantic.BaseModel):
    """Insert `value` into the sequence at `path`, at `index`.

    Why:
        `index == len(sequence)` appends. `path` may also name a missing
        mapping key, in which case a new sequence is created for it, but
        only when `index` is 0 -- inserting into a sequence that doesn't
        exist yet only makes sense at its very start.
    """

    model_config = pydantic.ConfigDict(extra="forbid")

    op: Literal["insert"]
    path: list[str | int]
    index: int
    value: Any


class DeleteOp(pydantic.BaseModel):
    """Delete the mapping key or sequence element at `path`."""

    model_config = pydantic.ConfigDict(extra="forbid")

    op: Literal["delete"]
    path: list[str | int]


class MoveOp(pydantic.BaseModel):
    """Reorder the sequence at `path` by moving `from_index` to `to_index`."""

    model_config = pydantic.ConfigDict(extra="forbid")

    op: Literal["move"]
    path: list[str | int]
    from_index: int
    to_index: int


type PatchOp = Annotated[
    SetOp | InsertOp | DeleteOp | MoveOp, pydantic.Field(discriminator="op")
]


class PatchRequest(pydantic.BaseModel):
    """Request body for `POST /api/documents/patch`."""

    model_config = pydantic.ConfigDict(extra="forbid")

    yaml: str = pydantic.Field(description="The YAML document to patch.")
    ops: list[PatchOp] = pydantic.Field(
        description="Ordered edits, applied atomically."
    )


class PatchResponse(pydantic.BaseModel):
    """Response body for a successful `POST /api/documents/patch`."""

    yaml: str = pydantic.Field(description="The updated YAML document.")


class PatchOpErrorDetail(pydantic.BaseModel):
    """Detail of which operation failed and why."""

    op_index: int = pydantic.Field(description="Index of the failing op in `ops`.")
    message: str = pydantic.Field(description="Human-readable failure reason.")


class PatchOpErrorResponse(pydantic.BaseModel):
    """Response body for a failed `POST /api/documents/patch` (400)."""

    error: PatchOpErrorDetail


class CvDocumentsPayload(pydantic.BaseModel):
    """The four YAML documents belonging to one persisted CV.

    Why:
        Same four fields as `CvDocumentsRequest`, but named for the
        persistence endpoints (`cvs.py`) which nest this under a
        `documents` key rather than accepting it as the whole request body.
    """

    model_config = pydantic.ConfigDict(extra="forbid")

    cv_yaml: str = pydantic.Field(description="The `cv:` YAML document.")
    design_yaml: str = pydantic.Field(
        default="", description="The `design:` YAML document, or empty."
    )
    locale_yaml: str = pydantic.Field(
        default="", description="The `locale:` YAML document, or empty."
    )
    settings_yaml: str = pydantic.Field(
        default="", description="The `settings:` YAML document, or empty."
    )


class CvSummary(pydantic.BaseModel):
    """One row of `GET /api/cvs`: enough to render the CV list sidebar."""

    id: int
    name: str
    updated_at: datetime


class CvDetail(CvSummary):
    """A full CV: `CvSummary` plus its four YAML documents."""

    documents: CvDocumentsPayload


class CvCreateRequest(pydantic.BaseModel):
    """Request body for `POST /api/cvs`."""

    model_config = pydantic.ConfigDict(extra="forbid")

    name: str | None = pydantic.Field(
        default=None,
        max_length=MAX_CV_NAME_LENGTH,
        description="Display name for the new CV; defaults to `Untitled CV`.",
    )


class CvUpdateRequest(pydantic.BaseModel):
    """Request body for `PUT /api/cvs/{id}` (the autosave write).

    Why:
        `seen_updated_at` is the optimistic-concurrency token the client
        last read (see `repository.update_cv_conditional`); the write only
        applies if the stored `updated_at` still matches it.
    """

    model_config = pydantic.ConfigDict(extra="forbid")

    name: str = pydantic.Field(max_length=MAX_CV_NAME_LENGTH)
    documents: CvDocumentsPayload
    seen_updated_at: datetime


class CvUpdateResponse(pydantic.BaseModel):
    """Response body for a successful `PUT /api/cvs/{id}` or version restore."""

    updated_at: datetime


class CvConflictCurrent(pydantic.BaseModel):
    """The server's current state, returned on a `409` autosave conflict."""

    updated_at: datetime
    documents: CvDocumentsPayload


class CvConflictResponse(pydantic.BaseModel):
    """Response body for a `409` autosave conflict.

    Why:
        Lets the client reconcile: it can diff `current` against its own
        pending edit and decide whether to overwrite, merge, or discard.
    """

    current: CvConflictCurrent


class ThemeDesignPayload(pydantic.BaseModel):
    """Body of `GET`/`PUT /api/cvs/{id}/theme-designs/{theme}`.

    Why:
        The parsed `design:` mapping, not its YAML text: the editor switches
        theme by setting the whole mapping (`EditorPane.switchTheme`), so
        that is the shape it has in hand when leaving a theme and the shape
        it needs back when returning.
    """

    model_config = pydantic.ConfigDict(extra="forbid")

    design: dict[str, Any] = pydantic.Field(
        description="The design mapping, including its `theme` key."
    )


class CvVersionSummary(pydantic.BaseModel):
    """One row of `GET /api/cvs/{id}/versions`."""

    id: int
    created_at: datetime


class AuthStatus(pydantic.BaseModel):
    """Response body for `GET /api/auth/me`.

    Why `provider_available` sits alongside the identity: a deployment with
    no Google credentials is a supported deployment, and the client must be
    able to hide the sign-in UI entirely rather than offering a button that
    can only fail.
    """

    authenticated: bool
    email: str | None
    display_name: str | None
    provider_available: bool


class PreferenceUpdateRequest(pydantic.BaseModel):
    """Request body for `PUT /api/preferences`."""

    model_config = pydantic.ConfigDict(extra="forbid")

    key: str = pydantic.Field(max_length=MAX_PREFERENCE_KEY_LENGTH)
    value: str = pydantic.Field(max_length=MAX_PREFERENCE_VALUE_LENGTH)
