"""Programmatic alembic upgrade so the app never needs a manual CLI step.

Why:
    Phase 4b (docs/plans/completed/cv-editor-web-app.md): `uvicorn` must be able
    to start against a brand-new or behind-head database with zero manual
    setup. `upgrade_to_head` runs exactly what `alembic upgrade head` would
    run on the command line (same `Config`, same script location), so it is
    naturally idempotent: a database already at the latest revision is left
    untouched. This is called unconditionally at app startup -- the same
    idempotent call whether the target URL is the SQLite default or an
    explicitly configured one, so there is no separate, less-guarded code
    path for a custom `RENDERCV_WEB_DATABASE_URL`.
"""

import pathlib

from alembic import command
from alembic.config import Config

from .session import resolve_database_url

BACKEND_DIR = pathlib.Path(__file__).resolve().parents[3]


def build_alembic_config(database_url: str) -> Config:
    """Build an `alembic.Config` pointed at this package's migrations.

    Args:
        database_url: The database URL migrations should run against.

    Returns:
        A `Config` with `script_location` and `sqlalchemy.url` set.
    """
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


def upgrade_to_head(database_url: str | None = None) -> None:
    """Idempotently upgrade the target database to the latest migration.

    Why:
        Safe to call on every process startup: alembic no-ops when the
        database is already at `head`, and builds the schema from scratch
        when the database is missing -- the dev-DB creation path approved
        in the plan (docs/plans/completed/cv-editor-web-app.md, Phase 4).

    Args:
        database_url: The database URL to upgrade; defaults to
            `resolve_database_url()` (the `RENDERCV_WEB_DATABASE_URL`
            environment variable, or the SQLite default).
    """
    url = database_url if database_url is not None else resolve_database_url()
    config = build_alembic_config(url)
    command.upgrade(config, "head")
