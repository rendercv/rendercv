"""UI-state preferences: `GET`/`PUT /api/preferences`.

Why:
    Account-scoped key/value pairs (yaml-mode toggle, zoom, sidebar state,
    ...) the frontend reads back on load (docs/plans/completed/cv-editor-web-app.md,
    Phase 4). Like `/api/cvs`, these belong to a signed-in account and use
    `auth.CurrentAccount`, so an anonymous caller gets a 401 instead of a
    new identity.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .auth import CurrentAccount
from .db import repository
from .db.session import get_session
from .models import PreferenceUpdateRequest

router = APIRouter(tags=["preferences"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/api/preferences", response_model=dict[str, str])
def get_preferences(
    current_user: CurrentAccount, session: SessionDep
) -> dict[str, str]:
    """List the current session's UI preferences.

    Args:
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.

    Returns:
        A `{key: value}` map of every stored preference.
    """
    preferences = repository.get_preferences(session, current_user.id)
    return {preference.key: preference.value for preference in preferences}


@router.put("/api/preferences", status_code=204)
def set_preference(
    request: PreferenceUpdateRequest, current_user: CurrentAccount, session: SessionDep
) -> None:
    """Upsert one UI preference for the current session.

    Why:
        Returns `None` rather than a fresh `Response` object: FastAPI only
        merges a session cookie set on the auth dependency's injected
        `Response` into the final reply when the handler's return value is
        serialized into *that* object -- returning a new `Response`
        instance here would silently drop it (regression-tested by
        `TestPreferences` in `test_cvs_api.py`).

    Args:
        request: The preference key/value pair to store.
        current_user: The session's `User`, resolved from the session
            cookie.
        session: The database session.
    """
    repository.set_preference(session, current_user.id, request.key, request.value)
