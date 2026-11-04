"""Engine and session-factory construction for the RenderCV Web Editor.

Why:
    Kept separate from `models.py` and `repository.py` so tests can build
    an engine pointed at a throwaway file (or `sqlite:///:memory:`) without
    ever touching the process-default database, and so 4b's FastAPI
    dependency wiring has one obvious place to import from.

Design notes:
    - The default URL reads `RENDERCV_WEB_DATABASE_URL`, defaulting to
      `sqlite:///./data/rendercv_web.db` (relative to the process's
      working directory when the app starts).
    - SQLite does not enforce foreign keys unless told to per-connection;
      `create_engine_from_url` registers a `connect` listener that runs
      `PRAGMA foreign_keys=ON` so `ON DELETE CASCADE` (cv_versions ->
      cvs, cvs/preferences -> users) actually fires in development the
      same way it does on Postgres in production.
    - The default engine/session-factory are built lazily (only on first
      use via `get_default_engine`/`get_default_session_factory`) so
      importing this module never has a side effect (no directory
      creation, no file opened) -- tests build their own engines against
      tmp paths and never call the lazy default accessors.
"""

import functools
import os
import pathlib
from collections.abc import Iterator

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

DEFAULT_DATABASE_URL = "sqlite:///./data/rendercv_web.db"
DATABASE_URL_ENV_VAR = "RENDERCV_WEB_DATABASE_URL"


def normalize_database_url(url: str) -> str:
    """Point bare Postgres URLs at the driver this project actually installs.

    Why:
        Hosting providers hand out connection strings as `postgres://...`
        (Railway, Heroku) or `postgresql://...` (Neon, Supabase), and both
        fail here if pasted as-is: SQLAlchemy has no `postgres` dialect at
        all, and its default driver for `postgresql` is psycopg2, while the
        `postgres` extra installs psycopg 3. Deployment would fail at
        startup with `NoSuchModuleError` or `ModuleNotFoundError` -- errors
        that say nothing about the real problem being a URL prefix.

        An explicitly chosen driver (`postgresql+psycopg2://`, for someone
        who installed psycopg2 themselves) is left exactly as written.

    Args:
        url: A database URL, possibly in a provider's own form.

    Returns:
        The URL with a driver SQLAlchemy can load, unchanged for every
        non-Postgres URL.
    """
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


def resolve_database_url() -> str:
    """Read the configured database URL, falling back to the SQLite default.

    Why:
        Read fresh on every call (never cached at import time) so tests
        that set the env var per-test, or callers that pass an explicit
        URL, are never shadowed by a stale value from a previous import.

    Why normalization happens *here* and not only in
    `create_engine_from_url`: migrations do not go through that function.
    Alembic builds its own engine from the URL string, so normalizing only
    at engine creation left both migration paths -- the `alembic` CLI and
    the app's own startup `upgrade_to_head` -- failing on exactly the
    provider URLs the normalization exists to accept. Doing it at the
    single point where the URL is read covers every consumer.

    Returns:
        The database URL to connect with, with a driver SQLAlchemy can load.
    """
    return normalize_database_url(
        os.environ.get(DATABASE_URL_ENV_VAR, DEFAULT_DATABASE_URL)
    )


def ensure_sqlite_directory(url: str) -> None:
    """Create the parent directory of a SQLite file URL if it is missing.

    Why:
        SQLite refuses to create a database file inside a directory that
        does not exist yet; Postgres URLs have no local path to create, so
        this is a no-op for them.

    Args:
        url: A SQLAlchemy database URL.
    """
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return
    path_part = url[len(prefix) :]
    if path_part in ("", ":memory:"):
        return
    pathlib.Path(path_part).parent.mkdir(parents=True, exist_ok=True)


def create_engine_from_url(url: str) -> Engine:
    """Build a configured `Engine` for `url`, portable across SQLite/Postgres.

    Args:
        url: A SQLAlchemy database URL (e.g. `sqlite:///./data/x.db` or
            `postgresql://...`, in any form a provider hands out).

    Returns:
        An `Engine` with SQLite foreign-key enforcement enabled when `url`
        is a SQLite URL; a plain engine otherwise.
    """
    url = normalize_database_url(url)
    is_sqlite = url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    engine = sa.create_engine(url, connect_args=connect_args, future=True)

    if is_sqlite:

        @event.listens_for(engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection: object, _: object) -> None:
            cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Build a `sessionmaker` bound to `engine`.

    Args:
        engine: The engine sessions should connect through.

    Returns:
        A `sessionmaker` producing `Session` objects for that engine.
    """
    return sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False, future=True
    )


@functools.lru_cache(maxsize=1)
def get_default_engine() -> Engine:
    """Build (once) the process-default engine from `RENDERCV_WEB_DATABASE_URL`.

    Why:
        Cached so the real app reuses one connection pool for its
        lifetime. Tests must not call this -- they build their own engine
        via `create_engine_from_url` against a tmp path so the cache never
        leaks state between tests.

    Returns:
        The lazily constructed, process-wide default `Engine`.
    """
    url = resolve_database_url()
    ensure_sqlite_directory(url)
    return create_engine_from_url(url)


def get_default_session_factory() -> sessionmaker[Session]:
    """Return a `sessionmaker` bound to the process-default engine.

    Returns:
        A `sessionmaker` for `get_default_engine()`.
    """
    return build_session_factory(get_default_engine())


def get_session() -> Iterator[Session]:
    """FastAPI-dependency-shaped session provider for the Phase 4b app.

    Why:
        Not wired into `app.py` yet (Phase 4a is schema-only) -- 4b adds
        `Depends(get_session)` to the endpoints that need persistence.

    Yields:
        A `Session` against the process-default engine; always closed.
    """
    factory = get_default_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()
