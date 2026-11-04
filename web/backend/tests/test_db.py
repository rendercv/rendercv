"""Tests for the persistence layer: models, repository functions, and the
initial alembic migration's upgrade/downgrade round trip.

Why:
    Phase 4a (docs/plans/completed/cv-editor-web-app.md) delivers the schema
    before any endpoint uses it; these tests are the proof the schema and
    its concurrency guarantees hold, independent of Phase 4b's API layer.
    Every test runs against a throwaway SQLite file under `tmp_path` --
    per guardrails, no test ever touches a real or shared database.
"""

import os
import pathlib
from collections.abc import Iterator
from datetime import datetime

import pytest
from alembic import command
from alembic.config import Config
from rendercv_web.db import repository as repo
from rendercv_web.db.migrate import build_alembic_config
from rendercv_web.db.models import Base, CvVersion
from rendercv_web.db.session import (
    create_engine_from_url,
    normalize_database_url,
    resolve_database_url,
)
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session, sessionmaker

BACKEND_DIR = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture
def session_factory(tmp_path: pathlib.Path) -> sessionmaker[Session]:
    """A `sessionmaker` bound to a fresh SQLite file with the schema created.

    Why:
        Bound to the *engine*, not to one `Session`, so tests that need
        two independent writers (the conflict test) can each get their
        own `Session` while still sharing the same underlying database.
    """
    db_path = tmp_path / "test.db"
    engine = create_engine_from_url(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False, future=True
    )


@pytest.fixture
def session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """A single `Session` for tests that only need one writer."""
    active_session = session_factory()
    try:
        yield active_session
    finally:
        active_session.close()


class TestUsers:
    """`get_or_create_user_by_token`."""

    def test_creates_a_new_user_for_an_unseen_token(self, session: Session) -> None:
        user = repo.get_or_create_user_by_token(session, "token-1")

        assert user.id is not None
        assert user.session_token == "token-1"

    def test_reuses_the_existing_user_for_a_known_token(self, session: Session) -> None:
        first = repo.get_or_create_user_by_token(session, "token-2")
        second = repo.get_or_create_user_by_token(session, "token-2")

        assert first.id == second.id


class TestCvCrud:
    """`create_cv`, `get_cv`, `list_cvs`, `delete_cv`."""

    def test_create_and_get_round_trip(self, session: Session) -> None:
        user = repo.get_or_create_user_by_token(session, "token-cv-1")
        created = repo.create_cv(
            session,
            user.id,
            name="My CV",
            cv_yaml="cv:\n  name: John Doe\n",
            design_yaml="design:\n  theme: classic\n",
        )

        fetched = repo.get_cv(session, created.id, user.id)

        assert fetched is not None
        assert fetched.name == "My CV"
        assert fetched.cv_yaml == "cv:\n  name: John Doe\n"
        assert fetched.design_yaml == "design:\n  theme: classic\n"
        assert fetched.content_hash == created.content_hash
        assert fetched.created_at == fetched.updated_at

    def test_get_cv_returns_none_for_another_users_cv(self, session: Session) -> None:
        owner = repo.get_or_create_user_by_token(session, "token-owner")
        stranger = repo.get_or_create_user_by_token(session, "token-stranger")
        cv = repo.create_cv(
            session, owner.id, name="Private", cv_yaml="cv:\n  name: X\n"
        )

        assert repo.get_cv(session, cv.id, stranger.id) is None

    def test_list_cvs_orders_newest_updated_first(self, session: Session) -> None:
        user = repo.get_or_create_user_by_token(session, "token-list")
        first = repo.create_cv(
            session, user.id, name="First", cv_yaml="cv:\n  name: A\n"
        )
        second = repo.create_cv(
            session, user.id, name="Second", cv_yaml="cv:\n  name: B\n"
        )

        # Touch `first` again so it becomes the most recently updated.
        repo.update_cv_conditional(
            session,
            first.id,
            user.id,
            first.updated_at,
            name="First",
            cv_yaml="cv:\n  name: A2\n",
            design_yaml="",
            locale_yaml="",
            settings_yaml="",
        )

        ordered = repo.list_cvs(session, user.id)

        assert [cv.id for cv in ordered] == [first.id, second.id]

    def test_delete_cv_removes_the_row_and_cascades_versions(
        self, session: Session
    ) -> None:
        user = repo.get_or_create_user_by_token(session, "token-delete")
        cv = repo.create_cv(session, user.id, name="Doomed", cv_yaml="cv:\n  name: X\n")
        repo.add_version(session, cv.id, "v1", "", "", "")
        repo.add_version(session, cv.id, "v2", "", "", "")

        deleted = repo.delete_cv(session, cv.id, user.id)

        assert deleted is True
        assert repo.get_cv(session, cv.id, user.id) is None
        remaining_versions = (
            session.execute(select(CvVersion).where(CvVersion.cv_id == cv.id))
            .scalars()
            .all()
        )
        assert remaining_versions == []

    def test_delete_cv_returns_false_when_not_owned(self, session: Session) -> None:
        owner = repo.get_or_create_user_by_token(session, "token-owner-2")
        stranger = repo.get_or_create_user_by_token(session, "token-stranger-2")
        cv = repo.create_cv(
            session, owner.id, name="Private", cv_yaml="cv:\n  name: X\n"
        )

        assert repo.delete_cv(session, cv.id, stranger.id) is False
        assert repo.get_cv(session, cv.id, owner.id) is not None


class TestConditionalUpdate:
    """`update_cv_conditional`: the autosave concurrency guarantee."""

    def test_succeeds_and_bumps_updated_at_when_seen_value_matches(
        self, session: Session
    ) -> None:
        user = repo.get_or_create_user_by_token(session, "token-update-ok")
        cv = repo.create_cv(session, user.id, name="CV", cv_yaml="cv:\n  name: A\n")

        result = repo.update_cv_conditional(
            session,
            cv.id,
            user.id,
            cv.updated_at,
            name="CV renamed",
            cv_yaml="cv:\n  name: A2\n",
            design_yaml="",
            locale_yaml="",
            settings_yaml="",
        )

        assert result.conflict is None
        assert result.cv is not None
        assert result.cv.name == "CV renamed"
        assert result.cv.cv_yaml == "cv:\n  name: A2\n"
        assert result.cv.updated_at >= cv.updated_at

    def test_returns_not_found_conflict_for_missing_cv(self, session: Session) -> None:
        user = repo.get_or_create_user_by_token(session, "token-update-missing")

        result = repo.update_cv_conditional(
            session,
            999_999,
            user.id,
            datetime(2020, 1, 1),
            name="X",
            cv_yaml="",
            design_yaml="",
            locale_yaml="",
            settings_yaml="",
        )

        assert result.conflict == "not_found"
        assert result.cv is None

    def test_returns_not_found_conflict_when_not_owned(self, session: Session) -> None:
        owner = repo.get_or_create_user_by_token(session, "token-update-owner")
        stranger = repo.get_or_create_user_by_token(session, "token-update-stranger")
        cv = repo.create_cv(session, owner.id, name="CV", cv_yaml="cv:\n  name: A\n")

        result = repo.update_cv_conditional(
            session,
            cv.id,
            stranger.id,
            cv.updated_at,
            name="Hijacked",
            cv_yaml="cv:\n  name: HACK\n",
            design_yaml="",
            locale_yaml="",
            settings_yaml="",
        )

        assert result.conflict == "not_found"

    def test_second_writer_loses_the_race_and_first_writers_content_wins(
        self, session_factory: sessionmaker[Session]
    ) -> None:
        """Two concurrent autosaves: the second to attempt the UPDATE with a
        now-stale `seen_updated_at` must get a conflict, never silently
        overwrite the winner (guardrail: no last-write-wins on cv_versions
        data, enforced here at the `cvs` row level via the WHERE clause).
        """
        writer_a = session_factory()
        writer_b = session_factory()
        try:
            user = repo.get_or_create_user_by_token(writer_a, "token-race")
            cv = repo.create_cv(
                writer_a, user.id, name="CV", cv_yaml="cv:\n  name: base\n"
            )
            seen_by_both = cv.updated_at

            # Writer B saves first and succeeds.
            result_b = repo.update_cv_conditional(
                writer_b,
                cv.id,
                user.id,
                seen_by_both,
                name="CV",
                cv_yaml="cv:\n  name: from-b\n",
                design_yaml="",
                locale_yaml="",
                settings_yaml="",
            )
            assert result_b.conflict is None

            # Writer A still holds the now-stale `seen_by_both` -> conflict.
            result_a = repo.update_cv_conditional(
                writer_a,
                cv.id,
                user.id,
                seen_by_both,
                name="CV",
                cv_yaml="cv:\n  name: from-a\n",
                design_yaml="",
                locale_yaml="",
                settings_yaml="",
            )
            assert result_a.conflict == "stale"
            assert result_a.cv is None

            # The persisted content is writer B's -- writer A's write never
            # landed, silently or otherwise.
            final = repo.get_cv(writer_a, cv.id, user.id)
            assert final is not None
            assert final.cv_yaml == "cv:\n  name: from-b\n"
        finally:
            writer_a.close()
            writer_b.close()


class TestVersions:
    """`add_version`, `list_versions`, `get_version`, `prune_versions`."""

    def test_add_and_list_versions_newest_first(self, session: Session) -> None:
        user = repo.get_or_create_user_by_token(session, "token-versions")
        cv = repo.create_cv(session, user.id, name="CV", cv_yaml="cv:\n  name: A\n")
        first = repo.add_version(session, cv.id, "v1", "", "", "")
        second = repo.add_version(session, cv.id, "v2", "", "", "")

        versions = repo.list_versions(session, cv.id, user.id)

        assert versions is not None
        assert [v.id for v in versions] == [second.id, first.id]

    def test_list_versions_returns_none_when_cv_not_owned(
        self, session: Session
    ) -> None:
        owner = repo.get_or_create_user_by_token(session, "token-versions-owner")
        stranger = repo.get_or_create_user_by_token(session, "token-versions-stranger")
        cv = repo.create_cv(session, owner.id, name="CV", cv_yaml="cv:\n  name: A\n")
        repo.add_version(session, cv.id, "v1", "", "", "")

        assert repo.list_versions(session, cv.id, stranger.id) is None

    def test_get_version_round_trip(self, session: Session) -> None:
        user = repo.get_or_create_user_by_token(session, "token-get-version")
        cv = repo.create_cv(session, user.id, name="CV", cv_yaml="cv:\n  name: A\n")
        version = repo.add_version(session, cv.id, "v1", "", "", "")

        fetched = repo.get_version(session, cv.id, user.id, version.id)

        assert fetched is not None
        assert fetched.cv_yaml == "v1"

    def test_prune_versions_keeps_only_the_newest_keep_count(
        self, session: Session
    ) -> None:
        user = repo.get_or_create_user_by_token(session, "token-prune")
        cv = repo.create_cv(session, user.id, name="CV", cv_yaml="cv:\n  name: A\n")
        for i in range(55):
            repo.add_version(session, cv.id, f"v{i}", "", "", "")

        deleted_count = repo.prune_versions(session, cv.id, keep=50)

        assert deleted_count == 5
        remaining = repo.list_versions(session, cv.id, user.id)
        assert remaining is not None
        assert len(remaining) == 50
        # Newest-first ordering is preserved; the oldest 5 (v0..v4) are gone.
        assert remaining[0].cv_yaml == "v54"
        assert remaining[-1].cv_yaml == "v5"

    def test_prune_versions_is_a_no_op_under_the_keep_count(
        self, session: Session
    ) -> None:
        user = repo.get_or_create_user_by_token(session, "token-prune-noop")
        cv = repo.create_cv(session, user.id, name="CV", cv_yaml="cv:\n  name: A\n")
        repo.add_version(session, cv.id, "v1", "", "", "")

        deleted_count = repo.prune_versions(session, cv.id, keep=50)

        assert deleted_count == 0


class TestPreferences:
    """`get_preferences`, `set_preference`."""

    def test_set_preference_inserts_a_new_key(self, session: Session) -> None:
        user = repo.get_or_create_user_by_token(session, "token-prefs-1")

        repo.set_preference(session, user.id, "zoom", "100")

        prefs = repo.get_preferences(session, user.id)
        assert [(p.key, p.value) for p in prefs] == [("zoom", "100")]

    def test_set_preference_upserts_an_existing_key(self, session: Session) -> None:
        user = repo.get_or_create_user_by_token(session, "token-prefs-2")
        repo.set_preference(session, user.id, "zoom", "100")

        repo.set_preference(session, user.id, "zoom", "125")

        prefs = repo.get_preferences(session, user.id)
        assert [(p.key, p.value) for p in prefs] == [("zoom", "125")]

    def test_preferences_are_scoped_per_user(self, session: Session) -> None:
        user_a = repo.get_or_create_user_by_token(session, "token-prefs-a")
        user_b = repo.get_or_create_user_by_token(session, "token-prefs-b")
        repo.set_preference(session, user_a.id, "zoom", "100")
        repo.set_preference(session, user_b.id, "zoom", "200")

        assert [p.value for p in repo.get_preferences(session, user_a.id)] == ["100"]
        assert [p.value for p in repo.get_preferences(session, user_b.id)] == ["200"]


class TestMigration:
    """The initial alembic revision: `upgrade head` then `downgrade base`."""

    def test_upgrade_head_creates_tables_and_downgrade_base_drops_them(
        self, tmp_path: pathlib.Path
    ) -> None:
        db_path = tmp_path / "alembic_scratch.db"
        database_url = f"sqlite:///{db_path}"
        expected_tables = {"users", "cvs", "cv_versions", "preferences"}

        previous_env_value = os.environ.get("RENDERCV_WEB_DATABASE_URL")
        os.environ["RENDERCV_WEB_DATABASE_URL"] = database_url
        try:
            alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
            alembic_cfg.set_main_option(
                "script_location", str(BACKEND_DIR / "migrations")
            )

            command.upgrade(alembic_cfg, "head")

            engine = create_engine_from_url(database_url)
            try:
                table_names = set(inspect(engine).get_table_names())
            finally:
                engine.dispose()
            assert expected_tables <= table_names

            command.downgrade(alembic_cfg, "base")

            engine = create_engine_from_url(database_url)
            try:
                table_names_after_downgrade = set(inspect(engine).get_table_names())
            finally:
                engine.dispose()
            assert not (expected_tables & table_names_after_downgrade)
        finally:
            if previous_env_value is None:
                os.environ.pop("RENDERCV_WEB_DATABASE_URL", None)
            else:
                os.environ["RENDERCV_WEB_DATABASE_URL"] = previous_env_value


class TestNormalizeDatabaseUrl:
    """Provider connection strings must work when pasted in unchanged.

    Both bare forms fail outright without this: SQLAlchemy has no
    `postgres` dialect, and its default driver for `postgresql` is
    psycopg2 while the `postgres` extra installs psycopg 3.
    """

    def test_railway_and_heroku_style_postgres_scheme_is_rewritten(self) -> None:
        assert (
            normalize_database_url("postgres://user:pw@host:5432/db")
            == "postgresql+psycopg://user:pw@host:5432/db"
        )

    def test_neon_and_supabase_style_postgresql_scheme_is_rewritten(self) -> None:
        assert (
            normalize_database_url("postgresql://user:pw@host:5432/db")
            == "postgresql+psycopg://user:pw@host:5432/db"
        )

    def test_query_parameters_survive_the_rewrite(self) -> None:
        # Managed Postgres almost always requires `sslmode=require`; losing
        # it would turn a working URL into a refused connection.
        assert (
            normalize_database_url("postgresql://u:p@host/db?sslmode=require")
            == "postgresql+psycopg://u:p@host/db?sslmode=require"
        )

    def test_an_explicitly_chosen_driver_is_left_alone(self) -> None:
        # Someone who installed psycopg2 themselves asked for it by name.
        url = "postgresql+psycopg2://user:pw@host/db"

        assert normalize_database_url(url) == url

    def test_sqlite_urls_are_untouched(self) -> None:
        assert (
            normalize_database_url("sqlite:///./data/x.db") == "sqlite:///./data/x.db"
        )


class TestMigrationPathsNormalizeTheUrl:
    """Every consumer of the URL must get the driver rewrite, not just one.

    Regression for a real failure: the normalization originally lived in
    `create_engine_from_url`, but migrations never call it -- alembic
    builds its own engine from the URL string. So `alembic upgrade head`
    and the app's own startup migration both died on exactly the provider
    URLs the rewrite exists to accept, and only a run against a real
    Postgres server surfaced it.
    """

    def test_resolve_database_url_rewrites_a_provider_url(self, monkeypatch) -> None:
        monkeypatch.setenv(
            "RENDERCV_WEB_DATABASE_URL", "postgresql://user:pw@host:5432/db"
        )

        assert resolve_database_url() == "postgresql+psycopg://user:pw@host:5432/db"

    def test_alembic_config_carries_the_rewritten_url(self, monkeypatch) -> None:
        # `migrate.build_alembic_config` is what the app's startup path and
        # the CLI both end up handing to alembic.
        monkeypatch.setenv("RENDERCV_WEB_DATABASE_URL", "postgres://user:pw@host/db")

        config = build_alembic_config(resolve_database_url())

        assert (
            config.get_main_option("sqlalchemy.url")
            == "postgresql+psycopg://user:pw@host/db"
        )

    def test_sqlite_urls_still_pass_through_untouched(self, monkeypatch) -> None:
        monkeypatch.setenv("RENDERCV_WEB_DATABASE_URL", "sqlite:///./data/x.db")

        assert resolve_database_url() == "sqlite:///./data/x.db"
