"""Contract tests for `GET /api/health/db`.

Why:
    The keep-awake job relies on two behaviours: a reachable database answers
    200, and an unreachable one answers 503, so the job fails and GitHub
    sends an email. Both run against throwaway databases, never a real one.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from rendercv_web.app import app
from rendercv_web.db.session import (
    build_session_factory,
    create_engine_from_url,
    get_session,
)
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def clear_overrides() -> Iterator[None]:
    """Drop the `get_session` override after each test."""
    yield
    app.dependency_overrides.clear()


def client_for(database_url: str) -> TestClient:
    """Build a client whose `get_session` points at `database_url`.

    Why the client is not entered as a context manager: that would run the
    startup migrations, which cannot connect to the unreachable database in
    the failure test. The endpoint itself needs no tables.

    Args:
        database_url: The database the endpoint should query.

    Returns:
        A `TestClient` with `get_session` overridden.
    """
    session_factory = build_session_factory(create_engine_from_url(database_url))

    def override_get_session() -> Iterator[Session]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


def test_reachable_database_answers_ok(tmp_path) -> None:
    client = client_for(f"sqlite:///{tmp_path / 'health.db'}")

    response = client.get("/api/health/db")

    assert response.status_code == 200
    assert response.json() == {"database": "ok"}


def test_unreachable_database_answers_503_without_details(tmp_path) -> None:
    # A SQLite file inside a directory that does not exist cannot be opened,
    # which stands in for a paused Supabase project.
    missing = tmp_path / "missing-dir" / "health.db"
    client = client_for(f"sqlite:///{missing}")

    response = client.get("/api/health/db")

    assert response.status_code == 503
    assert response.json()["detail"] == "Database unreachable."
    assert str(tmp_path) not in response.text


def test_needs_no_sign_in(tmp_path) -> None:
    client = client_for(f"sqlite:///{tmp_path / 'health.db'}")

    response = client.get("/api/health/db")

    assert "set-cookie" not in response.headers
    assert response.status_code == 200
