"""Contract tests for Phase 4b: session identity, `/api/cvs`, `/api/preferences`.

Why:
    Every test runs against a throwaway SQLite file under `tmp_path`
    (guardrail: never touch a real or shared database) with `get_session`
    overridden so requests hit that file directly. Entering the app via
    `with TestClient(app) as client:` also exercises the real startup path
    (`db.migrate.upgrade_to_head`, docs/plans/completed/cv-editor-web-app.md,
    Phase 4) instead of a shortcut like `Base.metadata.create_all`, so the
    "uvicorn just works against a brand-new DB" guarantee is covered by the
    same tests as the endpoints themselves.
"""

from collections.abc import Iterator

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
from rendercv_web.db.models import User
from rendercv_web.db.session import (
    build_session_factory,
    create_engine_from_url,
    get_session,
)
from rendercv_web.defaults import (
    default_cv_yaml,
    default_design_yaml,
    default_locale_yaml,
    default_settings_yaml,
)

# Asserted against the generator rather than a copy of its output: the
# sample is the core's to change, and a literal here would turn any such
# change into a test failure that says nothing about this API.
DEFAULT_CV_YAML = default_cv_yaml()
DEFAULT_SETTINGS_YAML = default_settings_yaml()


def make_client(
    tmp_path, monkeypatch, db_name: str = "test.db", sign_in_as: str | None = "tester"
) -> TestClient:
    """Build a `TestClient` wired to its own throwaway SQLite database.

    Args:
        tmp_path: pytest's per-test temporary directory.
        monkeypatch: pytest's monkeypatch fixture.
        db_name: File name for the throwaway database, so two clients in
            the same test can share (or not share) a database on purpose.
        sign_in_as: Provider subject id to sign the client in as. `None`
            leaves it anonymous, for the tests that assert an
            unauthenticated caller is refused.

    Returns:
        A `TestClient` whose lifespan already ran migrations against the
        throwaway database, and whose `get_session` dependency is
        overridden to use it.
    """
    database_url = f"sqlite:///{tmp_path / db_name}"
    monkeypatch.setenv("RENDERCV_WEB_DATABASE_URL", database_url)
    monkeypatch.setenv("RENDERCV_WEB_SECRET", "test-secret")

    engine = create_engine_from_url(database_url)
    session_factory = build_session_factory(engine)

    def override_get_session() -> Iterator:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)
    client.__enter__()
    if sign_in_as is not None:
        sign_client_in(client, session_factory, sign_in_as)
    return client


def second_session_factory(tmp_path, db_name: str):
    """Session factory on an existing throwaway database.

    Why: the isolation tests need a *second account* on the *same* database
    as the first client, to prove one account cannot read another's rows.
    """
    return build_session_factory(
        create_engine_from_url(f"sqlite:///{tmp_path / db_name}")
    )


def sign_client_in(client: TestClient, session_factory, subject: str) -> None:
    """Give `client` the cookie of a signed-in account.

    Why it builds the row and the cookie directly instead of driving the
    OAuth flow: `/api/cvs` and `/api/preferences` now require an account
    (`auth.CurrentAccount`), and the only other way in is Google's consent
    screen. Rather than add a test-only login endpoint -- an authentication
    bypass that a misconfigured deployment could expose -- this uses the
    same production code the callback uses, so nothing exists in the app
    that would not exist without tests.

    Args:
        client: The client to sign in.
        session_factory: Factory for sessions on the client's database.
        subject: Provider subject id, so separate accounts stay distinct.
    """
    token = generate_session_token()
    with session_factory() as session:
        repository.create_account_user(
            session,
            token,
            auth_provider="google",
            auth_provider_id=subject,
            email=f"{subject}@example.com",
            display_name=subject,
        )
    client.cookies.set(SESSION_COOKIE_NAME, encode_cookie(token, resolve_secret()))


@pytest.fixture
def client(tmp_path, monkeypatch) -> Iterator[TestClient]:
    """A `TestClient` against a fresh per-test database, signed in."""
    test_client = make_client(tmp_path, monkeypatch)
    try:
        yield test_client
    finally:
        test_client.__exit__(None, None, None)
        app.dependency_overrides.pop(get_session, None)


def create_default_cv(client: TestClient, name: str = "My CV") -> dict:
    """Create a CV via the API and return its parsed JSON body."""
    response = client.post("/api/cvs", json={"name": name})
    assert response.status_code == 201
    return response.json()


class TestSessionCookie:
    """The signed session cookie: what carries the account, and what happens without it."""

    def test_an_anonymous_caller_is_refused(self, tmp_path, monkeypatch) -> None:
        # `/api/cvs` holds a user's own documents, so a caller with no
        # account is turned away rather than handed a new identity.
        # Hiding the button in the UI would mean nothing if this returned
        # data to anyone who called it directly.
        anonymous = make_client(tmp_path, monkeypatch, sign_in_as=None)
        try:
            assert anonymous.get("/api/cvs").status_code == 401
            assert anonymous.get("/api/preferences").status_code == 401
        finally:
            anonymous.__exit__(None, None, None)
            app.dependency_overrides.pop(get_session, None)

    def test_refusing_a_caller_creates_no_user_row(self, tmp_path, monkeypatch) -> None:
        # A refusal must not leave anything behind: these endpoints are
        # reachable by any bot, and minting a row per rejected probe would
        # grow the table without limit.
        anonymous = make_client(tmp_path, monkeypatch, sign_in_as=None)
        try:
            for _ in range(3):
                anonymous.get("/api/cvs")

            factory = second_session_factory(tmp_path, "test.db")
            with factory() as session:
                count = session.execute(
                    sa.select(sa.func.count()).select_from(User)
                ).scalar()
            assert count == 0
        finally:
            anonymous.__exit__(None, None, None)
            app.dependency_overrides.pop(get_session, None)

    def test_a_signed_in_client_is_accepted(self, client: TestClient) -> None:
        assert client.get("/api/cvs").status_code == 200

    def test_cookie_is_stable_across_requests(self, client: TestClient) -> None:
        client.get("/api/cvs")
        cookie_value = client.cookies["rendercv_session"]

        second = client.get("/api/cvs")

        # A cookie that already decodes successfully is never re-issued.
        assert "rendercv_session" not in second.cookies
        assert client.cookies["rendercv_session"] == cookie_value

    def test_two_clients_see_disjoint_cv_lists(self, tmp_path, monkeypatch) -> None:
        client_a = make_client(tmp_path, monkeypatch, db_name="shared.db")
        try:
            create_default_cv(client_a, name="A's CV")

            client_b = TestClient(app, cookies={})
            sign_client_in(
                client_b, second_session_factory(tmp_path, "shared.db"), "other"
            )
            try:
                # A brand-new client with no cookie jar gets its own session.
                response = client_b.get("/api/cvs")
                assert response.status_code == 200
                assert response.json() == []

                response_a = client_a.get("/api/cvs")
                assert len(response_a.json()) == 1
            finally:
                client_b.close()
        finally:
            client_a.__exit__(None, None, None)
            app.dependency_overrides.pop(get_session, None)


class TestCvCrud:
    """`GET/POST/PUT/DELETE /api/cvs` happy paths."""

    def test_create_seeds_the_frontend_default_documents(
        self, client: TestClient
    ) -> None:
        body = create_default_cv(client, name="My CV")

        assert body["name"] == "My CV"
        assert body["documents"]["cv_yaml"] == DEFAULT_CV_YAML
        # Design and locale used to be seeded empty. They now carry the
        # theme's own values, spelled out, so the panes open on something a
        # user can edit rather than on nothing -- see `defaults`.
        assert body["documents"]["design_yaml"] == default_design_yaml()
        assert body["documents"]["locale_yaml"] == default_locale_yaml()
        assert body["documents"]["settings_yaml"] == DEFAULT_SETTINGS_YAML
        assert "id" in body
        assert "updated_at" in body

    def test_create_without_a_name_uses_a_default_name(
        self, client: TestClient
    ) -> None:
        response = client.post("/api/cvs", json={})

        assert response.status_code == 201
        assert response.json()["name"] == "Untitled CV"

    def test_list_orders_newest_updated_first(self, client: TestClient) -> None:
        first = create_default_cv(client, name="First")
        second = create_default_cv(client, name="Second")
        client.put(
            f"/api/cvs/{first['id']}",
            json={
                "name": "First",
                "documents": first["documents"],
                "seen_updated_at": first["updated_at"],
            },
        )

        listed = client.get("/api/cvs").json()

        assert [cv["id"] for cv in listed] == [first["id"], second["id"]]

    def test_get_returns_the_full_document_set(self, client: TestClient) -> None:
        created = create_default_cv(client)

        response = client.get(f"/api/cvs/{created['id']}")

        assert response.status_code == 200
        assert response.json() == created

    def test_update_happy_path_bumps_updated_at(self, client: TestClient) -> None:
        created = create_default_cv(client)
        new_documents = {**created["documents"], "cv_yaml": "cv:\n  name: Jane Doe\n"}

        response = client.put(
            f"/api/cvs/{created['id']}",
            json={
                "name": "Renamed",
                "documents": new_documents,
                "seen_updated_at": created["updated_at"],
            },
        )

        assert response.status_code == 200
        assert response.json()["updated_at"] >= created["updated_at"]

        fetched = client.get(f"/api/cvs/{created['id']}").json()
        assert fetched["name"] == "Renamed"
        assert fetched["documents"]["cv_yaml"] == "cv:\n  name: Jane Doe\n"

    def test_update_rejects_an_oversized_document(self, client: TestClient) -> None:
        created = create_default_cv(client)
        oversized = "a" * (512 * 1024 + 1)

        response = client.put(
            f"/api/cvs/{created['id']}",
            json={
                "name": created["name"],
                "documents": {**created["documents"], "cv_yaml": oversized},
                "seen_updated_at": created["updated_at"],
            },
        )

        assert response.status_code == 413

    def test_update_conflict_returns_409_with_current_state(
        self, client: TestClient
    ) -> None:
        created = create_default_cv(client)
        stale_seen_at = created["updated_at"]

        # A first writer wins.
        first_write = client.put(
            f"/api/cvs/{created['id']}",
            json={
                "name": "First writer",
                "documents": created["documents"],
                "seen_updated_at": stale_seen_at,
            },
        )
        assert first_write.status_code == 200

        # A second writer, still holding the now-stale `seen_updated_at`,
        # must be told about the conflict instead of overwriting it.
        second_write = client.put(
            f"/api/cvs/{created['id']}",
            json={
                "name": "Second writer",
                "documents": created["documents"],
                "seen_updated_at": stale_seen_at,
            },
        )

        assert second_write.status_code == 409
        body = second_write.json()
        assert body["current"]["updated_at"] == first_write.json()["updated_at"]
        assert body["current"]["documents"] == created["documents"]

    def test_update_returns_404_for_missing_cv(self, client: TestClient) -> None:
        response = client.put(
            "/api/cvs/999999",
            json={
                "name": "X",
                "documents": {
                    "cv_yaml": DEFAULT_CV_YAML,
                    "design_yaml": "",
                    "locale_yaml": "",
                    "settings_yaml": "",
                },
                "seen_updated_at": "2020-01-01T00:00:00",
            },
        )

        assert response.status_code == 404

    def test_duplicate_creates_a_named_copy(self, client: TestClient) -> None:
        created = create_default_cv(client, name="Original")

        response = client.post(f"/api/cvs/{created['id']}/duplicate")

        assert response.status_code == 201
        copy = response.json()
        assert copy["name"] == "Copy of Original"
        assert copy["id"] != created["id"]
        assert copy["documents"] == created["documents"]
        assert len(client.get("/api/cvs").json()) == 2

    def test_delete_removes_the_cv(self, client: TestClient) -> None:
        created = create_default_cv(client)

        response = client.delete(f"/api/cvs/{created['id']}")

        assert response.status_code == 204
        assert client.get(f"/api/cvs/{created['id']}").status_code == 404

    def test_delete_returns_404_for_missing_cv(self, client: TestClient) -> None:
        response = client.delete("/api/cvs/999999")

        assert response.status_code == 404


class TestCrossSessionIsolation:
    """A CV id belonging to another session must look exactly like 404."""

    def test_get_another_sessions_cv_is_404(self, tmp_path, monkeypatch) -> None:
        client_a = make_client(tmp_path, monkeypatch, db_name="isolation.db")
        try:
            created = create_default_cv(client_a, name="Private")

            client_b = TestClient(app, cookies={})
            sign_client_in(
                client_b, second_session_factory(tmp_path, "isolation.db"), "other"
            )
            try:
                response = client_b.get(f"/api/cvs/{created['id']}")
                assert response.status_code == 404
            finally:
                client_b.close()
        finally:
            client_a.__exit__(None, None, None)
            app.dependency_overrides.pop(get_session, None)


class TestVersions:
    """`GET /api/cvs/{id}/versions` and version restore."""

    def test_versions_list_grows_with_each_successful_update(
        self, client: TestClient
    ) -> None:
        created = create_default_cv(client)

        client.put(
            f"/api/cvs/{created['id']}",
            json={
                "name": created["name"],
                "documents": created["documents"],
                "seen_updated_at": created["updated_at"],
            },
        )

        versions = client.get(f"/api/cvs/{created['id']}/versions").json()

        assert len(versions) == 1
        assert "id" in versions[0]
        assert "created_at" in versions[0]

    def test_versions_returns_404_for_another_sessions_cv(
        self, tmp_path, monkeypatch
    ) -> None:
        client_a = make_client(tmp_path, monkeypatch, db_name="versions.db")
        try:
            created = create_default_cv(client_a)

            client_b = TestClient(app, cookies={})
            sign_client_in(
                client_b, second_session_factory(tmp_path, "versions.db"), "other"
            )
            try:
                response = client_b.get(f"/api/cvs/{created['id']}/versions")
                assert response.status_code == 404
            finally:
                client_b.close()
        finally:
            client_a.__exit__(None, None, None)
            app.dependency_overrides.pop(get_session, None)

    def test_restore_applies_the_snapshot_as_a_new_update(
        self, client: TestClient
    ) -> None:
        created = create_default_cv(client)
        first_update = client.put(
            f"/api/cvs/{created['id']}",
            json={
                "name": created["name"],
                "documents": {
                    **created["documents"],
                    "cv_yaml": "cv:\n  name: First Edit\n",
                },
                "seen_updated_at": created["updated_at"],
            },
        )
        assert first_update.status_code == 200
        after_first_edit = client.get(f"/api/cvs/{created['id']}").json()

        second_update = client.put(
            f"/api/cvs/{created['id']}",
            json={
                "name": created["name"],
                "documents": {
                    **created["documents"],
                    "cv_yaml": "cv:\n  name: Second Edit\n",
                },
                "seen_updated_at": after_first_edit["updated_at"],
            },
        )
        assert second_update.status_code == 200

        versions = client.get(f"/api/cvs/{created['id']}/versions").json()
        # Newest first: index 1 is the snapshot taken right after the first edit.
        version_to_restore = versions[1]

        restore_response = client.post(
            f"/api/cvs/{created['id']}/versions/{version_to_restore['id']}/restore"
        )

        assert restore_response.status_code == 200
        restored = client.get(f"/api/cvs/{created['id']}").json()
        assert restored["documents"]["cv_yaml"] == "cv:\n  name: First Edit\n"
        # The restore itself is recorded as a fourth version.
        assert len(client.get(f"/api/cvs/{created['id']}/versions").json()) == 3

    def test_restore_returns_404_for_missing_version(self, client: TestClient) -> None:
        created = create_default_cv(client)

        response = client.post(f"/api/cvs/{created['id']}/versions/999999/restore")

        assert response.status_code == 404

    def test_prune_keeps_only_the_newest_50_versions(self, client: TestClient) -> None:
        created = create_default_cv(client)
        seen_at = created["updated_at"]

        for i in range(55):
            response = client.put(
                f"/api/cvs/{created['id']}",
                json={
                    "name": created["name"],
                    "documents": {
                        **created["documents"],
                        "cv_yaml": f"cv:\n  name: Edit {i}\n",
                    },
                    "seen_updated_at": seen_at,
                },
            )
            assert response.status_code == 200
            seen_at = response.json()["updated_at"]

        versions = client.get(f"/api/cvs/{created['id']}/versions").json()

        assert len(versions) == 50


class TestPreferences:
    """`GET/PUT /api/preferences`."""

    def test_roundtrip(self, client: TestClient) -> None:
        assert client.get("/api/preferences").json() == {}

        response = client.put("/api/preferences", json={"key": "zoom", "value": "125"})
        assert response.status_code == 204

        assert client.get("/api/preferences").json() == {"zoom": "125"}

    def test_upsert_overwrites_an_existing_key(self, client: TestClient) -> None:
        client.put("/api/preferences", json={"key": "zoom", "value": "100"})

        client.put("/api/preferences", json={"key": "zoom", "value": "150"})

        assert client.get("/api/preferences").json() == {"zoom": "150"}

    def test_preferences_are_scoped_per_session(self, tmp_path, monkeypatch) -> None:
        client_a = make_client(tmp_path, monkeypatch, db_name="prefs.db")
        try:
            client_a.put("/api/preferences", json={"key": "zoom", "value": "100"})

            client_b = TestClient(app, cookies={})
            sign_client_in(
                client_b, second_session_factory(tmp_path, "prefs.db"), "other"
            )
            try:
                assert client_b.get("/api/preferences").json() == {}
            finally:
                client_b.close()
        finally:
            client_a.__exit__(None, None, None)
            app.dependency_overrides.pop(get_session, None)


class TestDesignDiscriminatorRegression:
    """A design document missing its `theme` discriminator must 422, not 500."""

    def test_validate_returns_422_for_a_design_without_a_theme_key(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/api/validate",
            json={
                "cv_yaml": DEFAULT_CV_YAML,
                "design_yaml": "design:\n  page:\n    top_margin: 0.5in\n",
                "locale_yaml": "",
                "settings_yaml": "",
            },
        )

        assert response.status_code == 422
        body = response.json()
        assert body["errors"]
        assert "theme" in body["errors"][0]["message"].lower()

    def test_render_returns_422_for_a_design_without_a_theme_key(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/api/render",
            json={
                "cv_yaml": DEFAULT_CV_YAML,
                "design_yaml": "design:\n  page:\n    top_margin: 0.5in\n",
                "locale_yaml": "",
                "settings_yaml": "",
            },
        )

        assert response.status_code == 422


HARVARD_TUNED = {
    "theme": "harvard",
    "section_titles": {"space_above": "0.25cm"},
    "entries": {"space_between_entries": "0.7em"},
}


class TestThemeDesigns:
    """`/api/cvs/{id}/theme-designs/{theme}`: a theme's design survives switching away."""

    def test_nothing_is_remembered_for_a_new_cv(self, client: TestClient) -> None:
        created = create_default_cv(client)

        response = client.get(f"/api/cvs/{created['id']}/theme-designs/harvard")

        assert response.status_code == 404

    def test_a_put_design_reads_back_unchanged(self, client: TestClient) -> None:
        created = create_default_cv(client)
        url = f"/api/cvs/{created['id']}/theme-designs/harvard"

        assert client.put(url, json={"design": HARVARD_TUNED}).status_code == 204

        response = client.get(url)
        assert response.status_code == 200
        assert response.json() == {"design": HARVARD_TUNED}

    def test_a_later_put_replaces_only_that_theme(self, client: TestClient) -> None:
        created = create_default_cv(client)
        base = f"/api/cvs/{created['id']}/theme-designs"
        client.put(f"{base}/harvard", json={"design": HARVARD_TUNED})
        client.put(f"{base}/classic", json={"design": {"theme": "classic"}})
        retuned = {**HARVARD_TUNED, "entries": {"space_between_entries": "0.5em"}}

        client.put(f"{base}/harvard", json={"design": retuned})

        assert client.get(f"{base}/harvard").json() == {"design": retuned}
        assert client.get(f"{base}/classic").json() == {"design": {"theme": "classic"}}

    def test_remembering_a_design_does_not_move_updated_at(
        self, client: TestClient
    ) -> None:
        # The open editor's next autosave sends the `updated_at` it last
        # saw; if this write moved it, that save would 409 against itself.
        created = create_default_cv(client)

        client.put(
            f"/api/cvs/{created['id']}/theme-designs/harvard",
            json={"design": HARVARD_TUNED},
        )

        after = client.get(f"/api/cvs/{created['id']}").json()
        assert after["updated_at"] == created["updated_at"]
        assert after["documents"] == created["documents"]

    def test_an_unknown_theme_is_404(self, client: TestClient) -> None:
        created = create_default_cv(client)
        url = f"/api/cvs/{created['id']}/theme-designs/not-a-theme"

        assert client.get(url).status_code == 404
        assert (
            client.put(url, json={"design": {"theme": "not-a-theme"}}).status_code
            == 404
        )

    def test_a_design_naming_another_theme_is_refused(self, client: TestClient) -> None:
        created = create_default_cv(client)

        response = client.put(
            f"/api/cvs/{created['id']}/theme-designs/classic",
            json={"design": HARVARD_TUNED},
        )

        assert response.status_code == 422

    def test_an_oversized_design_is_refused(self, client: TestClient) -> None:
        created = create_default_cv(client)

        response = client.put(
            f"/api/cvs/{created['id']}/theme-designs/harvard",
            json={"design": {"theme": "harvard", "padding": "x" * 600_000}},
        )

        assert response.status_code == 413

    def test_a_missing_cv_is_404(self, client: TestClient) -> None:
        url = "/api/cvs/999999/theme-designs/harvard"

        assert client.get(url).status_code == 404
        assert client.put(url, json={"design": HARVARD_TUNED}).status_code == 404

    def test_a_duplicate_remembers_the_same_designs(self, client: TestClient) -> None:
        created = create_default_cv(client)
        client.put(
            f"/api/cvs/{created['id']}/theme-designs/harvard",
            json={"design": HARVARD_TUNED},
        )

        copy = client.post(f"/api/cvs/{created['id']}/duplicate").json()

        response = client.get(f"/api/cvs/{copy['id']}/theme-designs/harvard")
        assert response.json() == {"design": HARVARD_TUNED}

    def test_another_accounts_cv_looks_missing(self, tmp_path, monkeypatch) -> None:
        client_a = make_client(tmp_path, monkeypatch, db_name="theme-designs.db")
        try:
            created = create_default_cv(client_a)
            url = f"/api/cvs/{created['id']}/theme-designs/harvard"
            client_a.put(url, json={"design": HARVARD_TUNED})

            client_b = TestClient(app, cookies={})
            sign_client_in(
                client_b, second_session_factory(tmp_path, "theme-designs.db"), "other"
            )
            try:
                assert client_b.get(url).status_code == 404
                assert (
                    client_b.put(url, json={"design": HARVARD_TUNED}).status_code == 404
                )
            finally:
                client_b.close()
            assert client_a.get(url).json() == {"design": HARVARD_TUNED}
        finally:
            client_a.__exit__(None, None, None)
            app.dependency_overrides.pop(get_session, None)
