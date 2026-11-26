"""Database health check: `GET /api/health/db`.

Why:
    The production database is a free Supabase project, and Supabase pauses
    a free project after 7 days without activity. A paused database takes
    the whole service down, because startup migrations cannot connect
    (2026-11-20 and 2026-11-26, see
    docs/plans/completed/session-handoff.md). A scheduled GitHub Actions job
    (`.github/workflows/keep-supabase-awake.yaml`) calls this endpoint daily:
    the query it runs counts as database activity, and when the database is
    already unreachable the job fails, so GitHub emails the repository owner.

    `/api/themes` (Render's health check) cannot do this job, because it
    never touches the database.
"""

import logging
from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .db.session import get_session

logger = logging.getLogger("rendercv_web")

router = APIRouter(tags=["health"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/api/health/db")
def database_health(session: SessionDep) -> dict[str, str]:
    """Run a trivial query to prove the database answers.

    Why it needs no sign-in: the caller is a scheduled job with no account,
    and the response says nothing beyond "reachable or not".

    Args:
        session: The database session.

    Returns:
        `{"database": "ok"}` when the query succeeds.

    Raises:
        HTTPException: 503 when the database cannot be reached. The driver's
            error goes to the log, not to the response, because it can name
            hosts and users.
    """
    try:
        session.execute(sa.text("SELECT 1"))
    except SQLAlchemyError as e:
        logger.warning("Database health check failed: %s", e)
        raise HTTPException(status_code=503, detail="Database unreachable.") from e
    return {"database": "ok"}
