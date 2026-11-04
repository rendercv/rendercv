"""Erasing an account.

The operation cannot be undone, so what is tested here is as much about
what it must *not* do -- reach another account's data, accept an
unauthenticated caller -- as about what it does.
"""

import pathlib

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from rendercv_web.app import app
from rendercv_web.auth import (
    SESSION_COOKIE_NAME,
    encode_cookie,
    generate_session_token,
    resolve_secret,
)
from rendercv_web.db import repository
from rendercv_web.db.session import build_session_factory, create_engine_from_url
from test_cvs_api import make_client, second_session_factory


def sign_in_new_account(client: TestClient, session_factory, subject: str) -> int:
    """Give `client` a fresh signed-in account and return its id.

    Args:
        client: The client to hand the session cookie to.
        session_factory: Factory for the database the client is wired to.
        subject: The Google subject id to attach the account to.

    Returns:
        The new account's row id.
    """
    token = generate_session_token()
    with session_factory() as session:
        account = repository.create_account_user(
            session,
            token,
            auth_provider="google",
            auth_provider_id=subject,
            email=f"{subject}@example.com",
            display_name=subject,
        )
        account_id = account.id
    client.cookies.set(SESSION_COOKIE_NAME, encode_cookie(token, resolve_secret()))
    return account_id


def count_rows(tmp_path: pathlib.Path, db_name: str, table: str) -> int:
    """Count rows in one table of a throwaway database.

    Args:
        tmp_path: pytest's per-test temporary directory.
        db_name: The database file's name.
        table: The table to count.

    Returns:
        The number of rows.
    """
    engine = create_engine_from_url(f"sqlite:///{tmp_path / db_name}")
    with build_session_factory(engine)() as session:
        return session.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar_one()


class TestDeletingAnAccount:
    """The happy path, and what it takes with it."""

    def test_it_answers_204_and_clears_the_cookie(self, tmp_path, monkeypatch) -> None:
        # The cookie is cleared as well as the row: leaving it would send
        # the browser back carrying a token whose account no longer exists.
        client = make_client(tmp_path, monkeypatch)

        response = client.delete("/api/auth/me")

        assert response.status_code == 204
        # Asserted on what the server sends, not on the client jar: this
        # test seeds its cookie without a domain, so it lands under a
        # different jar key than the host-only one the server clears, and
        # the seeded copy would survive a correct response.
        set_cookie = response.headers.get("set-cookie", "")
        assert SESSION_COOKIE_NAME in set_cookie
        assert "Max-Age=0" in set_cookie or "1970" in set_cookie

    def test_the_account_can_no_longer_sign_in_with_that_cookie(
        self, tmp_path, monkeypatch
    ) -> None:
        client = make_client(tmp_path, monkeypatch)
        client.post("/api/cvs", json={"name": "Doomed"})
        cookie = client.cookies[SESSION_COOKIE_NAME]

        client.delete("/api/auth/me")

        # A copy of the cookie taken before the delete must be worthless
        # afterwards, not merely absent from this browser.
        replayed = TestClient(app, cookies={SESSION_COOKIE_NAME: cookie})
        assert replayed.get("/api/cvs").status_code == 401

    def test_the_cvs_and_preferences_go_with_it(self, tmp_path, monkeypatch) -> None:
        client = make_client(tmp_path, monkeypatch)
        client.post("/api/cvs", json={"name": "One"})
        client.post("/api/cvs", json={"name": "Two"})
        client.put("/api/preferences", json={"key": "ui_theme", "value": "dark"})

        assert count_rows(tmp_path, "test.db", "cvs") == 2
        assert count_rows(tmp_path, "test.db", "preferences") == 1

        client.delete("/api/auth/me")

        # Cascades, not hand-written deletes -- so this also catches the
        # foreign keys being switched off, which would silently orphan rows
        # rather than raise.
        assert count_rows(tmp_path, "test.db", "users") == 0
        assert count_rows(tmp_path, "test.db", "cvs") == 0
        assert count_rows(tmp_path, "test.db", "preferences") == 0

    def test_the_version_history_goes_too(self, tmp_path, monkeypatch) -> None:
        # Versions hang off CVs rather than off the user, so they are erased
        # by a second hop of the cascade. That is the one most likely to be
        # missed by a hand-written delete.
        client = make_client(tmp_path, monkeypatch)
        created = client.post("/api/cvs", json={"name": "With history"}).json()
        client.put(
            f"/api/cvs/{created['id']}",
            json={
                "name": "With history",
                "documents": {
                    "cv_yaml": "cv:\n  name: Edited\n  sections: {}\n",
                    "design_yaml": "",
                    "locale_yaml": "",
                    "settings_yaml": "",
                },
                "seen_updated_at": created["updated_at"],
            },
        )
        assert count_rows(tmp_path, "test.db", "cv_versions") > 0

        client.delete("/api/auth/me")

        assert count_rows(tmp_path, "test.db", "cv_versions") == 0


class TestWhatItMustNotTouch:
    """The failures that would be worst, and silent."""

    def test_an_anonymous_caller_is_refused(self, tmp_path, monkeypatch) -> None:
        # Without an account there is nothing to delete, and a caller with
        # no session must not be able to mint one and erase it -- which is
        # what resolving the cookie by hand would allow.
        client = make_client(tmp_path, monkeypatch, sign_in_as=None)

        assert client.delete("/api/auth/me").status_code == 401
        assert count_rows(tmp_path, "test.db", "users") == 0

    def test_another_account_survives_untouched(self, tmp_path, monkeypatch) -> None:
        client = make_client(tmp_path, monkeypatch, db_name="shared.db")
        factory = second_session_factory(tmp_path, "shared.db")

        neighbour = TestClient(app)
        sign_in_new_account(neighbour, factory, "the-neighbour")
        neighbour.post("/api/cvs", json={"name": "Not yours"})

        client.post("/api/cvs", json={"name": "Mine"})
        client.delete("/api/auth/me")

        # The neighbour is still signed in and still owns their CV.
        assert count_rows(tmp_path, "shared.db", "users") == 1
        names = [cv["name"] for cv in neighbour.get("/api/cvs").json()]
        assert names == ["Not yours"]

    @pytest.mark.parametrize("method", ["get", "post", "put"])
    def test_only_delete_erases_anything(
        self, tmp_path, monkeypatch, method: str
    ) -> None:
        # `/api/auth/me` answers GET with the account's status. A verb mix-up
        # in a client must not erase the account, so the other verbs are
        # asserted not to.
        client = make_client(tmp_path, monkeypatch)
        client.post("/api/cvs", json={"name": "Keep me"})

        getattr(client, method)("/api/auth/me")

        assert count_rows(tmp_path, "test.db", "users") == 1
        assert count_rows(tmp_path, "test.db", "cvs") == 1
