"""SQLAlchemy ORM models for the RenderCV Web Editor's baseline schema.

Why:
    Per the `schema-design` skill: a CV's content is four YAML text
    documents (`cv`, `design`, `locale`, `settings`) stored as-is — the
    pydantic models in `rendercv.schema` own that structure, so it is never
    decomposed into relational columns here. Columns exist only for what
    the database must query or enforce: ids, ownership, names, timestamps,
    and hashes.

    Types are restricted to Integer / String / Text / DateTime so the same
    models work unmodified against SQLite (dev) and Postgres (prod); no
    dialect-specific column types are used without a decision record in
    docs/decisions/ (guardrail: "no engine-specific features").

    Timestamps are naive UTC `datetime` values assigned in Python (see
    `utc_now` in `repository.py`), not `server_default=func.now()` --
    SQLite's `CURRENT_TIMESTAMP` and Postgres's `now()` differ in
    precision and timezone-awareness, and the conditional-update
    concurrency check in `repository.update_cv_conditional` compares
    `updated_at` values byte-for-byte, so both writer and reader must
    agree on exactly how that value is produced.
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base shared by every table; also alembic's autogenerate target."""


class User(Base):
    """One identity: an anonymous device session, or a signed-in account.

    Why:
        A signed HTTPOnly cookie carries the opaque `session_token` that
        identifies this row, and that stays true after Phase 6 added
        Google sign-in -- signing in swaps the cookie to the *account*
        row's token rather than introducing a second identity mechanism.
        That is what lets an anonymous session be "claimed" by an account
        without losing its CVs (`repository.claim_anonymous_user`).

    The auth columns are all nullable because an anonymous row has none of
    them; `(auth_provider, auth_provider_id)` is unique so one Google
    account maps to exactly one row, which is what makes signing in on a
    second device find the existing account instead of creating another.

    Known limitation (acceptable for this phase, not for a large
    deployment): one account has one `session_token`, so signing in on a
    second device reuses the same token rather than minting a per-device
    session. Rotating it on sign-out would therefore sign out every
    device. A separate `sessions` table is the fix when that matters.
    """

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint(
            "auth_provider", "auth_provider_id", name="uq_users_auth_provider_identity"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    # Null on an anonymous row; set together when an account signs in.
    auth_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    auth_provider_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    cvs: Mapped[list["Cv"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    preferences: Mapped[list["Preference"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class Cv(Base):
    """One CV: four YAML documents plus the metadata the app must query on.

    Why:
        `updated_at` doubles as the optimistic-concurrency token for
        autosave (`repository.update_cv_conditional`): a write only
        succeeds if it still matches the value the client last saw.
        `content_hash` lets the render cache and the client detect
        identical content without diffing four text blobs.
    """

    __tablename__ = "cvs"
    __table_args__ = (
        # Access pattern: "list my CVs, most recently updated first"
        # (GET /api/cvs). A plain ascending composite index is walked
        # backwards for the DESC scan on both SQLite and Postgres, so no
        # dialect-specific descending-index syntax is needed.
        Index("ix_cvs_user_id_updated_at", "user_id", "updated_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cv_yaml: Mapped[str] = mapped_column(Text, nullable=False, default="")
    design_yaml: Mapped[str] = mapped_column(Text, nullable=False, default="")
    locale_yaml: Mapped[str] = mapped_column(Text, nullable=False, default="")
    settings_yaml: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # A JSON object `{theme name: design mapping}`: the design each theme
    # had when the user last switched away from it, so switching back
    # restores their tuned values instead of the theme's defaults. Text,
    # not a JSON column type, per the portable-types rule above; it is never
    # queried into, only read and written whole (`repository.*_theme_design`).
    # Deliberately outside `content_hash` and `updated_at`: it is not part of
    # what renders, and bumping `updated_at` would make the open editor's
    # next autosave lose its optimistic-concurrency check.
    theme_designs: Mapped[str] = mapped_column(
        Text, nullable=False, default="{}", server_default="{}"
    )
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="cvs")
    versions: Mapped[list["CvVersion"]] = relationship(
        back_populates="cv", cascade="all, delete-orphan", passive_deletes=True
    )


class CvVersion(Base):
    """An append-only autosave snapshot of a CV's four documents.

    Why:
        Powers undo history across sessions (Phase 4 plan). Rows are never
        updated, only inserted and pruned by `repository.prune_versions`;
        `ON DELETE CASCADE` on `cv_id` means deleting a `Cv` deletes its
        version history in the same statement, never as a second
        application-level step.
    """

    __tablename__ = "cv_versions"
    __table_args__ = (
        # Access pattern: "list versions of this CV, newest first" (undo
        # history) and "find the oldest versions beyond the keep-count"
        # (prune_versions). Same backwards-scan rationale as cvs' index.
        Index("ix_cv_versions_cv_id_created_at", "cv_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cv_id: Mapped[int] = mapped_column(
        ForeignKey("cvs.id", ondelete="CASCADE"), nullable=False
    )
    cv_yaml: Mapped[str] = mapped_column(Text, nullable=False, default="")
    design_yaml: Mapped[str] = mapped_column(Text, nullable=False, default="")
    locale_yaml: Mapped[str] = mapped_column(Text, nullable=False, default="")
    settings_yaml: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(nullable=False)

    cv: Mapped["Cv"] = relationship(back_populates="versions")


class Preference(Base):
    """One UI-state key/value pair for a user (yaml mode, zoom, sidebar...).

    Why:
        Composite primary key `(user_id, key)` is both the uniqueness
        constraint and the lookup index -- one row per key, upserted by
        `repository.set_preference`.
    """

    __tablename__ = "preferences"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship(back_populates="preferences")
