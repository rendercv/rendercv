"""Persistence layer for the RenderCV Web Editor (Phase 4a).

Why:
    Isolates SQLAlchemy engine/session wiring, ORM models, and the
    repository functions the Phase 4b endpoints call, so the API layer
    never writes raw SQL and never guesses at the schema (see
    docs/plans/completed/cv-editor-web-app.md, Phase 4, and the
    `schema-design` skill).
"""

from .migrate import upgrade_to_head
from .models import Base, Cv, CvVersion, Preference, User
from .session import (
    create_engine_from_url,
    ensure_sqlite_directory,
    resolve_database_url,
)

__all__ = [
    "Base",
    "Cv",
    "CvVersion",
    "Preference",
    "User",
    "create_engine_from_url",
    "ensure_sqlite_directory",
    "resolve_database_url",
    "upgrade_to_head",
]
