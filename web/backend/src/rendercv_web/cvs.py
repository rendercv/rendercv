"""Multi-CV persistence: `/api/cvs` and its version-history sub-resource.

Why:
    Phase 4b (docs/plans/completed/cv-editor-web-app.md): the sidebar's list of
    saved CVs, the autosave write, and undo history. Every endpoint here
    requires a signed-in account (`auth.CurrentAccount`, which refuses an
    anonymous caller with a 401 rather than minting an identity for them),
    because these are the endpoints holding a user's own documents.

    Every read and write is scoped to `current_user.id`; a CV id that
    exists but belongs to someone else is treated exactly like a CV id
    that doesn't exist at all (guardrail: never leak ownership via a 403).
"""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from rendercv.schema.models.design.built_in_design import available_themes

from .auth import CurrentAccount
from .db import repository
from .db.models import Cv
from .db.session import get_session
from .defaults import (
    DEFAULT_CV_NAME,
    default_cv_yaml,
    default_design_yaml,
    default_locale_yaml,
    default_settings_yaml,
)
from .errors import CvConflictError
from .limits import enforce_documents_size_cap
from .models import (
    MAX_CV_NAME_LENGTH,
    MAX_DOCUMENT_BYTES,
    CvConflictCurrent,
    CvCreateRequest,
    CvDetail,
    CvDocumentsPayload,
    CvSummary,
    CvUpdateRequest,
    CvUpdateResponse,
    CvVersionSummary,
    ThemeDesignPayload,
)

router = APIRouter(tags=["cvs"])

SessionDep = Annotated[Session, Depends(get_session)]

VERSIONS_TO_KEEP = 50


def cv_documents(cv: Cv) -> CvDocumentsPayload:
    """Extract a CV row's four YAML documents into the API payload shape.

    Args:
        cv: The database row.

    Returns:
        The four documents as a `CvDocumentsPayload`.
    """
    return CvDocumentsPayload(
        cv_yaml=cv.cv_yaml,
        design_yaml=cv.design_yaml,
        locale_yaml=cv.locale_yaml,
        settings_yaml=cv.settings_yaml,
    )


def cv_to_summary(cv: Cv) -> CvSummary:
    """Convert a CV row into a `GET /api/cvs` list entry.

    Args:
        cv: The database row.

    Returns:
        The row's id, name, and `updated_at`.
    """
    return CvSummary(id=cv.id, name=cv.name, updated_at=cv.updated_at)


def cv_to_detail(cv: Cv) -> CvDetail:
    """Convert a CV row into the full `CvDetail` response shape.

    Args:
        cv: The database row.

    Returns:
        The row's id, name, `updated_at`, and its four documents.
    """
    return CvDetail(
        id=cv.id, name=cv.name, updated_at=cv.updated_at, documents=cv_documents(cv)
    )


def get_owned_cv_or_404(session: Session, cv_id: int, user_id: int) -> Cv:
    """Fetch a CV owned by `user_id`, or raise the API's not-found error.

    Args:
        session: The database session.
        cv_id: The CV to fetch.
        user_id: The caller's user id.

    Returns:
        The owned `Cv` row.

    Raises:
        HTTPException: 404 if no such CV is owned by `user_id` -- this is
            also what a CV owned by someone else looks like, deliberately.
    """
    cv = repository.get_cv(session, cv_id, user_id)
    if cv is None:
        raise HTTPException(status_code=404, detail="CV not found.")
    return cv


def apply_update_result(
    session: Session, cv_id: int, user_id: int, result: repository.CvUpdateResult
) -> CvUpdateResponse:
    """Turn an `update_cv_conditional` outcome into a response, or raise.

    Why:
        Shared by the autosave write and version restore, both of which
        must record a version snapshot and prune old ones on success, and
        surface the same 404/409 shapes on failure (docs/plans/active/
        cv-editor-web-app.md, Phase 4).

    Args:
        session: The database session.
        cv_id: The CV that was written to.
        user_id: The caller's user id.
        result: The outcome of `repository.update_cv_conditional`.

    Returns:
        The new `updated_at` on success.

    Raises:
        HTTPException: 404 if the CV doesn't exist or isn't owned.
        CvConflictError: 409 (translated by the exception boundary) if the
            write lost the optimistic-concurrency race; carries the
            server's current state so the client can reconcile.
    """
    if result.conflict == "not_found":
        raise HTTPException(status_code=404, detail="CV not found.")

    if result.conflict == "stale":
        current = get_owned_cv_or_404(session, cv_id, user_id)
        raise CvConflictError(
            current=CvConflictCurrent(
                updated_at=current.updated_at, documents=cv_documents(current)
            )
        )

    cv = result.cv
    if cv is None:  # pragma: no cover - conflict is None iff cv is set
        raise HTTPException(status_code=404, detail="CV not found.")

    repository.add_version(
        session, cv_id, cv.cv_yaml, cv.design_yaml, cv.locale_yaml, cv.settings_yaml
    )
    repository.prune_versions(session, cv_id, keep=VERSIONS_TO_KEEP)
    return CvUpdateResponse(updated_at=cv.updated_at)


@router.get("/api/cvs", response_model=list[CvSummary])
def list_cvs(current_user: CurrentAccount, session: SessionDep) -> list[CvSummary]:
    """List the current session's CVs, most recently updated first.

    Args:
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.

    Returns:
        One `CvSummary` per owned CV, newest-updated first.
    """
    cvs = repository.list_cvs(session, current_user.id)
    return [cv_to_summary(cv) for cv in cvs]


@router.post("/api/cvs", response_model=CvDetail, status_code=201)
def create_cv(
    request: CvCreateRequest, current_user: CurrentAccount, session: SessionDep
) -> CvDetail:
    """Create a new CV seeded with the editor's default documents.

    Why:
        Seeds the same placeholder content the frontend shows for a
        brand-new, unsaved session (`defaults.py`), so saving it
        immediately is a no-op from the user's point of view.

    Args:
        request: The optional display name for the new CV.
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.

    Returns:
        The newly created CV, in full.
    """
    cv = repository.create_cv(
        session,
        current_user.id,
        name=request.name or DEFAULT_CV_NAME,
        cv_yaml=default_cv_yaml(),
        design_yaml=default_design_yaml(),
        locale_yaml=default_locale_yaml(),
        settings_yaml=default_settings_yaml(),
    )
    return cv_to_detail(cv)


@router.get("/api/cvs/{cv_id}", response_model=CvDetail)
def get_cv(cv_id: int, current_user: CurrentAccount, session: SessionDep) -> CvDetail:
    """Fetch one CV, in full.

    Args:
        cv_id: The CV to fetch.
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.

    Returns:
        The CV's id, name, `updated_at`, and documents.

    Raises:
        HTTPException: 404 if the CV doesn't exist or isn't owned by the
            current session.
    """
    cv = get_owned_cv_or_404(session, cv_id, current_user.id)
    return cv_to_detail(cv)


@router.put("/api/cvs/{cv_id}", response_model=CvUpdateResponse)
def update_cv(
    cv_id: int,
    request: CvUpdateRequest,
    current_user: CurrentAccount,
    session: SessionDep,
) -> CvUpdateResponse:
    """Autosave a CV, iff it hasn't changed since the client last read it.

    Args:
        cv_id: The CV to update.
        request: The new name, documents, and the `updated_at` the client
            last saw.
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.

    Returns:
        The new `updated_at` on success.

    Raises:
        HTTPException: 404 if the CV doesn't exist or isn't owned, 413 if
            any document exceeds the size cap.
        CvConflictError: 409 (translated by the exception boundary) if the
            write lost the optimistic-concurrency race.
    """
    enforce_documents_size_cap(request.documents.model_dump())
    result = repository.update_cv_conditional(
        session,
        cv_id,
        current_user.id,
        request.seen_updated_at,
        name=request.name,
        cv_yaml=request.documents.cv_yaml,
        design_yaml=request.documents.design_yaml,
        locale_yaml=request.documents.locale_yaml,
        settings_yaml=request.documents.settings_yaml,
    )
    return apply_update_result(session, cv_id, current_user.id, result)


@router.post("/api/cvs/{cv_id}/duplicate", response_model=CvDetail, status_code=201)
def duplicate_cv(
    cv_id: int, current_user: CurrentAccount, session: SessionDep
) -> CvDetail:
    """Create a copy of a CV, named `Copy of {name}`.

    Args:
        cv_id: The CV to duplicate.
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.

    Returns:
        The newly created copy, in full.

    Raises:
        HTTPException: 404 if the source CV doesn't exist or isn't owned.
    """
    source = get_owned_cv_or_404(session, cv_id, current_user.id)
    copy = repository.create_cv(
        session,
        current_user.id,
        name=f"Copy of {source.name}"[:MAX_CV_NAME_LENGTH],
        cv_yaml=source.cv_yaml,
        design_yaml=source.design_yaml,
        locale_yaml=source.locale_yaml,
        settings_yaml=source.settings_yaml,
        theme_designs=source.theme_designs,
    )
    return cv_to_detail(copy)


@router.delete("/api/cvs/{cv_id}", status_code=204)
def delete_cv(cv_id: int, current_user: CurrentAccount, session: SessionDep) -> None:
    """Delete a CV and its version history.

    Why:
        Returns `None` rather than a fresh `Response` object: see the
        identical note on `preferences.set_preference` -- returning a new
        `Response` here would silently drop any session cookie the auth
        dependency just set on the shared response object.

    Args:
        cv_id: The CV to delete.
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.

    Raises:
        HTTPException: 404 if the CV doesn't exist or isn't owned.
    """
    deleted = repository.delete_cv(session, cv_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="CV not found.")


@router.get("/api/cvs/{cv_id}/versions", response_model=list[CvVersionSummary])
def list_versions(
    cv_id: int, current_user: CurrentAccount, session: SessionDep
) -> list[CvVersionSummary]:
    """List a CV's autosave snapshots, newest first.

    Args:
        cv_id: The CV whose versions to list.
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.

    Returns:
        One `CvVersionSummary` per snapshot, newest first.

    Raises:
        HTTPException: 404 if the CV doesn't exist or isn't owned.
    """
    versions = repository.list_versions(session, cv_id, current_user.id)
    if versions is None:
        raise HTTPException(status_code=404, detail="CV not found.")
    return [
        CvVersionSummary(id=version.id, created_at=version.created_at)
        for version in versions
    ]


@router.post(
    "/api/cvs/{cv_id}/versions/{version_id}/restore", response_model=CvUpdateResponse
)
def restore_version(
    cv_id: int,
    version_id: int,
    current_user: CurrentAccount,
    session: SessionDep,
) -> CvUpdateResponse:
    """Restore a version snapshot as a new autosave write.

    Why:
        Applied as a normal conditional update (not an in-place rewrite) so
        it bumps `updated_at`, records its own new version, and can lose an
        optimistic-concurrency race exactly like any other autosave would
        (docs/plans/completed/cv-editor-web-app.md, Phase 4).

    Args:
        cv_id: The CV to restore a version onto.
        version_id: The version snapshot to restore.
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.

    Returns:
        The new `updated_at` on success.

    Raises:
        HTTPException: 404 if the CV or the version doesn't exist or isn't
            owned.
        CvConflictError: 409 (translated by the exception boundary) if the
            write lost the optimistic-concurrency race against a
            concurrent autosave.
    """
    cv = get_owned_cv_or_404(session, cv_id, current_user.id)
    version = repository.get_version(session, cv_id, current_user.id, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found.")

    result = repository.update_cv_conditional(
        session,
        cv_id,
        current_user.id,
        cv.updated_at,
        name=cv.name,
        cv_yaml=version.cv_yaml,
        design_yaml=version.design_yaml,
        locale_yaml=version.locale_yaml,
        settings_yaml=version.settings_yaml,
    )
    return apply_update_result(session, cv_id, current_user.id, result)


def ensure_known_theme(theme: str) -> None:
    """Refuse a theme name the core does not ship.

    Why:
        The path segment becomes a key in the stored map. Accepting only
        built-in names keeps that map bounded (one entry per theme) instead
        of growing with whatever a caller puts in the URL.

    Args:
        theme: The theme name from the path.

    Raises:
        HTTPException: 404 if `theme` is not a built-in theme.
    """
    if theme not in available_themes:
        raise HTTPException(status_code=404, detail="Unknown theme.")


@router.get("/api/cvs/{cv_id}/theme-designs/{theme}", response_model=ThemeDesignPayload)
def get_theme_design(
    cv_id: int, theme: str, current_user: CurrentAccount, session: SessionDep
) -> ThemeDesignPayload:
    """Return the design a CV last had under `theme`.

    Why:
        Read at switch time rather than shipped with `GET /api/cvs/{id}`, so
        a design remembered on another device after this one loaded the CV
        is still the one restored.

    Args:
        cv_id: The CV.
        theme: The built-in theme name.
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.

    Returns:
        The remembered design mapping.

    Raises:
        HTTPException: 404 if the theme is unknown, the CV doesn't exist or
            isn't owned, or nothing is remembered for this theme yet.
    """
    ensure_known_theme(theme)
    found, design = repository.get_theme_design(session, cv_id, current_user.id, theme)
    if not found:
        raise HTTPException(status_code=404, detail="CV not found.")
    if design is None:
        raise HTTPException(status_code=404, detail="No design saved for this theme.")
    return ThemeDesignPayload(design=design)


@router.put("/api/cvs/{cv_id}/theme-designs/{theme}", status_code=204)
def put_theme_design(
    cv_id: int,
    theme: str,
    request: ThemeDesignPayload,
    current_user: CurrentAccount,
    session: SessionDep,
) -> None:
    """Remember the design a CV has under `theme`, for when it comes back.

    Why:
        Returns `None` for the same cookie reason as `delete_cv`. Does not
        touch `updated_at` (see `repository.set_theme_design`), so it never
        races the autosave write.

    Args:
        cv_id: The CV.
        theme: The built-in theme name.
        request: The design mapping to remember.
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.

    Raises:
        HTTPException: 404 if the theme is unknown or the CV doesn't exist
            or isn't owned; 422 if the design names a different theme; 413
            if it is over the document size cap.
    """
    ensure_known_theme(theme)
    if request.design.get("theme") != theme:
        raise HTTPException(
            status_code=422, detail="The design's `theme` must match the path."
        )
    encoded_size = len(json.dumps(request.design, ensure_ascii=False).encode("utf-8"))
    if encoded_size > MAX_DOCUMENT_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"`design` exceeds the {MAX_DOCUMENT_BYTES} byte limit.",
        )
    stored = repository.set_theme_design(
        session, cv_id, current_user.id, theme, request.design
    )
    if not stored:
        raise HTTPException(status_code=404, detail="CV not found.")
