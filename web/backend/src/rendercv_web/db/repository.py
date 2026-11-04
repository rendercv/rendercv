"""Typed repository functions the Phase 4b API endpoints call.

Why:
    Keeps every SQL statement in one reviewable place instead of scattered
    across route handlers, and keeps the concurrency-sensitive parts (the
    conditional autosave update, version pruning) implemented exactly once.

Transaction model:
    Each function here commits its own transaction -- callers get a
    consistent, already-committed result back and never have to remember
    to call `session.commit()`. The one place this matters is the autosave
    flow: `update_cv_conditional` is the single atomic statement that
    resolves the write race (guardrail: "concurrent autosaves are resolved
    with a conditional update ... last-write-wins is NOT acceptable"); the
    4b endpoint then calls `add_version` and `prune_versions` only when
    that update reports success. Those two are separate commits, so a
    crash between them can at most skip recording one snapshot -- it can
    never corrupt `cvs` or silently overwrite a concurrent write, because
    the `cvs` row is already durably correct by the time they run.

Access patterns (endpoint -> query -> index), Phase 4b:

    | Endpoint (planned)              | Query                                                          | Index used                        |
    |----------------------------------|-----------------------------------------------------------------|------------------------------------|
    | (any request, cookie middleware) | `get_or_create_user_by_token`: SELECT users WHERE session_token=:t; INSERT if absent | UNIQUE index on users.session_token |
    | `GET /api/cvs`                   | `list_cvs`: SELECT cvs WHERE user_id=:u ORDER BY updated_at DESC | ix_cvs_user_id_updated_at          |
    | `POST /api/cvs`                  | `create_cv`: INSERT INTO cvs (...)                              | cvs PK (autoincrement)             |
    | `GET /api/cvs/{id}`               | `get_cv`: SELECT cvs WHERE id=:id AND user_id=:u                 | cvs PK + user_id equality filter   |
    | `PATCH /api/cvs/{id}` (autosave)  | `update_cv_conditional`: single UPDATE ... WHERE id=:id AND user_id=:u AND updated_at=:seen | cvs PK; rowcount is the conflict check, no extra index needed |
    | (autosave, on success)           | `add_version`: INSERT INTO cv_versions (...)                    | cv_versions PK                     |
    | (autosave, on success)           | `prune_versions`: SELECT ids ORDER BY created_at DESC LIMIT keep; DELETE the rest | ix_cv_versions_cv_id_created_at |
    | `DELETE /api/cvs/{id}`            | `delete_cv`: DELETE cvs WHERE id=:id AND user_id=:u (cascades)   | cvs PK; FK ON DELETE CASCADE       |
    | `GET /api/cvs/{id}/versions`      | `list_versions`: SELECT cv_versions WHERE cv_id=:id ORDER BY created_at DESC | ix_cv_versions_cv_id_created_at |
    | `GET /api/cvs/{id}/versions/{vid}`| `get_version`: SELECT cv_versions WHERE id=:vid AND cv_id=:id    | cv_versions PK                     |
    | `GET /api/cvs/{id}/theme-designs/{theme}` | `get_theme_design`: SELECT cvs WHERE id=:id AND user_id=:u | cvs PK + user_id equality filter |
    | `PUT /api/cvs/{id}/theme-designs/{theme}` | `set_theme_design`: SELECT ... FOR UPDATE, then UPDATE cvs.theme_designs | cvs PK |
    | `GET /api/preferences`            | `get_preferences`: SELECT preferences WHERE user_id=:u           | preferences PK (user_id prefix)    |
    | `PUT /api/preferences/{key}`      | `set_preference`: UPDATE ... WHERE user_id=:u AND key=:k, INSERT if 0 rows | preferences PK              |

    None of these need a table scan at any expected scale (one user's CVs,
    one CV's versions) -- every query above is answered by an equality (or
    equality + range) match on an existing index.
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Cv, CvVersion, Preference, User


def utc_now() -> datetime:
    """Return the current time as a naive UTC `datetime`.

    Why:
        All timestamp columns are naive UTC (see `models.py`); every
        write path in this module must produce values through this one
        function so `updated_at` equality comparisons (the autosave
        concurrency check) are never defeated by mixed precision or
        timezone-awareness between call sites.
    """
    return datetime.now(UTC).replace(tzinfo=None)


def compute_content_hash(
    cv_yaml: str, design_yaml: str, locale_yaml: str, settings_yaml: str
) -> str:
    """Hash the four YAML documents as a unit.

    Args:
        cv_yaml: The `cv:` document.
        design_yaml: The `design:` document.
        locale_yaml: The `locale:` document.
        settings_yaml: The `settings:` document.

    Returns:
        A hex sha256 digest identifying this exact combination of the
        four documents (mirrors the render cache key in `cache.py`).
    """
    joined = "\x00".join([cv_yaml, design_yaml, locale_yaml, settings_yaml])
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def get_or_create_user_by_token(session: Session, session_token: str) -> User:
    """Look up the user for an anonymous session cookie, creating one if new.

    Why:
        Auth model option A (see cv-editor-web-app.md, Phase 4): the
        session token itself, not an email/password, is the identity. A
        brand-new cookie value means a brand-new user row.

    Args:
        session: The database session.
        session_token: The opaque token from the client's session cookie.

    Returns:
        The existing or newly created `User` row.
    """
    existing = session.execute(
        select(User).where(User.session_token == session_token)
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    user = User(session_token=session_token, created_at=utc_now())
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        # Why: two concurrent first-requests with the same brand-new
        # token would otherwise both try to insert; the loser re-reads
        # instead of erroring.
        session.rollback()
        return session.execute(
            select(User).where(User.session_token == session_token)
        ).scalar_one()
    session.refresh(user)
    return user


def list_cvs(session: Session, user_id: int) -> list[Cv]:
    """List a user's CVs, most recently updated first.

    Args:
        session: The database session.
        user_id: The owning user's id.

    Returns:
        The user's `Cv` rows, newest-updated first.
    """
    stmt = (
        select(Cv)
        .where(Cv.user_id == user_id)
        .order_by(Cv.updated_at.desc(), Cv.id.desc())
    )
    return list(session.execute(stmt).scalars())


def create_cv(
    session: Session,
    user_id: int,
    name: str,
    cv_yaml: str,
    design_yaml: str = "",
    locale_yaml: str = "",
    settings_yaml: str = "",
    theme_designs: str = "{}",
) -> Cv:
    """Create a new CV owned by `user_id`.

    Args:
        session: The database session.
        user_id: The owning user's id.
        name: Display name for the CV.
        cv_yaml: The `cv:` document.
        design_yaml: The `design:` document, or empty.
        locale_yaml: The `locale:` document, or empty.
        settings_yaml: The `settings:` document, or empty.
        theme_designs: The stored `{theme: design}` JSON text; a
            duplicate passes its source's so the copy remembers the same
            per-theme designs.

    Returns:
        The newly created `Cv` row.
    """
    now = utc_now()
    cv = Cv(
        user_id=user_id,
        name=name,
        cv_yaml=cv_yaml,
        design_yaml=design_yaml,
        locale_yaml=locale_yaml,
        settings_yaml=settings_yaml,
        theme_designs=theme_designs,
        content_hash=compute_content_hash(
            cv_yaml, design_yaml, locale_yaml, settings_yaml
        ),
        created_at=now,
        updated_at=now,
    )
    session.add(cv)
    session.commit()
    session.refresh(cv)
    return cv


def get_cv(session: Session, cv_id: int, user_id: int) -> Cv | None:
    """Fetch one CV, scoped to its owner.

    Args:
        session: The database session.
        cv_id: The CV's id.
        user_id: The caller's user id -- ownership is enforced in the query,
            not checked after the fact, so a mismatched id looks the same
            as a missing one.

    Returns:
        The `Cv`, or `None` if it doesn't exist or isn't owned by `user_id`.
    """
    stmt = select(Cv).where(Cv.id == cv_id, Cv.user_id == user_id)
    return session.execute(stmt).scalar_one_or_none()


@dataclass(frozen=True)
class CvUpdateResult:
    """Outcome of `update_cv_conditional`.

    Attributes:
        cv: The updated row, present only when `conflict` is `None`.
        conflict: `None` on success; `"stale"` if the row exists but
            `seen_updated_at` no longer matches (someone else wrote first
            -- the caller should return 409 and let the client reconcile);
            `"not_found"` if no such CV is owned by `user_id` (404).
    """

    cv: Cv | None
    conflict: Literal["stale", "not_found"] | None


def update_cv_conditional(
    session: Session,
    cv_id: int,
    user_id: int,
    seen_updated_at: datetime,
    name: str,
    cv_yaml: str,
    design_yaml: str,
    locale_yaml: str,
    settings_yaml: str,
) -> CvUpdateResult:
    """Autosave a CV iff it hasn't changed since the client last saw it.

    Why:
        Guardrails: concurrent autosaves must not be resolved
        last-write-wins. This issues exactly one `UPDATE ... WHERE
        id=:id AND user_id=:user_id AND updated_at=:seen` -- there is no
        read-then-write gap for a second writer to land in between; SQL's
        row-level locking during the UPDATE itself is what makes this
        atomic, not any lock taken by this function.

    Args:
        session: The database session.
        cv_id: The CV being saved.
        user_id: The caller's user id (ownership is part of the WHERE).
        seen_updated_at: The `updated_at` the client last read; the write
            only applies if this still matches the stored value.
        name: New display name.
        cv_yaml: New `cv:` document.
        design_yaml: New `design:` document.
        locale_yaml: New `locale:` document.
        settings_yaml: New `settings:` document.

    Returns:
        A `CvUpdateResult`: the fresh row on success, or a conflict
        sentinel (`"stale"` / `"not_found"`) with `cv=None` on failure.
    """
    new_updated_at = utc_now()
    new_hash = compute_content_hash(cv_yaml, design_yaml, locale_yaml, settings_yaml)

    stmt = (
        update(Cv)
        .where(
            Cv.id == cv_id,
            Cv.user_id == user_id,
            Cv.updated_at == seen_updated_at,
        )
        .values(
            name=name,
            cv_yaml=cv_yaml,
            design_yaml=design_yaml,
            locale_yaml=locale_yaml,
            settings_yaml=settings_yaml,
            content_hash=new_hash,
            updated_at=new_updated_at,
        )
    )
    result = session.execute(stmt)

    if result.rowcount == 1:
        session.commit()
        # Why: a Core-level UPDATE bypasses the ORM unit-of-work, so any
        # copy of this row already in the identity map (e.g. the one the
        # caller read `seen_updated_at` from) is now stale; expire it so
        # the following read goes back to the database.
        session.expire_all()
        cv = session.execute(select(Cv).where(Cv.id == cv_id)).scalar_one()
        return CvUpdateResult(cv=cv, conflict=None)

    session.rollback()
    existing = session.execute(select(Cv).where(Cv.id == cv_id)).scalar_one_or_none()
    if existing is None or existing.user_id != user_id:
        return CvUpdateResult(cv=None, conflict="not_found")
    return CvUpdateResult(cv=None, conflict="stale")


def delete_cv(session: Session, cv_id: int, user_id: int) -> bool:
    """Delete a CV (and, via `ON DELETE CASCADE`, its versions).

    Args:
        session: The database session.
        cv_id: The CV to delete.
        user_id: The caller's user id (ownership is part of the WHERE).

    Returns:
        `True` if a row was deleted, `False` if none matched.
    """
    stmt = delete(Cv).where(Cv.id == cv_id, Cv.user_id == user_id)
    result = session.execute(stmt)
    session.commit()
    return result.rowcount == 1


def read_theme_designs(cv: Cv) -> dict[str, dict[str, Any]]:
    """Decode a CV's stored `{theme: design}` map.

    Why:
        Tolerant on purpose: the column only ever holds what
        `set_theme_design` wrote, but a hand-edited or truncated value must
        cost the user their remembered designs, not every request on that CV.

    Args:
        cv: The database row.

    Returns:
        The map; empty if the stored text is not a JSON object. Entries
        whose value is not an object are dropped.
    """
    try:
        decoded = json.loads(cv.theme_designs or "{}")
    except ValueError:
        return {}
    if not isinstance(decoded, dict):
        return {}
    return {
        str(theme): design
        for theme, design in decoded.items()
        if isinstance(design, dict)
    }


def get_theme_design(
    session: Session, cv_id: int, user_id: int, theme: str
) -> tuple[bool, dict[str, Any] | None]:
    """Fetch the design a CV last had under `theme`.

    Args:
        session: The database session.
        cv_id: The CV's id.
        user_id: The caller's user id (ownership is part of the query).
        theme: The theme name.

    Returns:
        `(cv_found, design)`: `cv_found` is `False` if no such CV is owned
        by `user_id`; `design` is `None` if the CV has none stored for
        `theme`.
    """
    cv = get_cv(session, cv_id, user_id)
    if cv is None:
        return False, None
    return True, read_theme_designs(cv).get(theme)


def set_theme_design(
    session: Session, cv_id: int, user_id: int, theme: str, design: dict[str, Any]
) -> bool:
    """Store the design a CV has under `theme`, replacing any earlier one.

    Why:
        Leaves `updated_at` and `content_hash` alone: this is not an edit to
        what renders, and moving `updated_at` would make the editor's next
        autosave fail its optimistic-concurrency check against its own
        session. The read-modify-write takes a row lock (`FOR UPDATE`, a
        no-op on SQLite) so two devices saving different themes at once
        cannot drop each other's entry.

    Args:
        session: The database session.
        cv_id: The CV's id.
        user_id: The caller's user id (ownership is part of the query).
        theme: The theme name.
        design: The design mapping to remember.

    Returns:
        `True` on success, `False` if no such CV is owned by `user_id`.
    """
    stmt = select(Cv).where(Cv.id == cv_id, Cv.user_id == user_id).with_for_update()
    cv = session.execute(stmt).scalar_one_or_none()
    if cv is None:
        session.rollback()
        return False
    designs = read_theme_designs(cv)
    designs[theme] = design
    cv.theme_designs = json.dumps(designs, ensure_ascii=False)
    session.commit()
    return True


def add_version(
    session: Session,
    cv_id: int,
    cv_yaml: str,
    design_yaml: str,
    locale_yaml: str,
    settings_yaml: str,
) -> CvVersion:
    """Append an autosave snapshot for a CV.

    Args:
        session: The database session.
        cv_id: The CV this snapshot belongs to.
        cv_yaml: Snapshot of the `cv:` document.
        design_yaml: Snapshot of the `design:` document.
        locale_yaml: Snapshot of the `locale:` document.
        settings_yaml: Snapshot of the `settings:` document.

    Returns:
        The newly inserted `CvVersion` row.
    """
    version = CvVersion(
        cv_id=cv_id,
        cv_yaml=cv_yaml,
        design_yaml=design_yaml,
        locale_yaml=locale_yaml,
        settings_yaml=settings_yaml,
        created_at=utc_now(),
    )
    session.add(version)
    session.commit()
    session.refresh(version)
    return version


def prune_versions(session: Session, cv_id: int, keep: int = 50) -> int:
    """Delete all but the newest `keep` versions of a CV.

    Args:
        session: The database session.
        cv_id: The CV whose version history is being pruned.
        keep: How many of the newest versions to retain.

    Returns:
        The number of version rows deleted.
    """
    keep_ids_stmt = (
        select(CvVersion.id)
        .where(CvVersion.cv_id == cv_id)
        .order_by(CvVersion.created_at.desc(), CvVersion.id.desc())
        .limit(keep)
    )
    keep_ids = [row[0] for row in session.execute(keep_ids_stmt)]
    if not keep_ids:
        return 0

    delete_stmt = delete(CvVersion).where(
        CvVersion.cv_id == cv_id, CvVersion.id.not_in(keep_ids)
    )
    result = session.execute(delete_stmt)
    session.commit()
    return result.rowcount


def list_versions(session: Session, cv_id: int, user_id: int) -> list[CvVersion] | None:
    """List a CV's versions, newest first, scoped to its owner.

    Args:
        session: The database session.
        cv_id: The CV whose versions to list.
        user_id: The caller's user id -- must own `cv_id`.

    Returns:
        The versions newest-first, or `None` if `cv_id` doesn't exist or
        isn't owned by `user_id` (caller should treat that as 404).
    """
    owner_check = select(Cv.id).where(Cv.id == cv_id, Cv.user_id == user_id)
    if session.execute(owner_check).scalar_one_or_none() is None:
        return None

    stmt = (
        select(CvVersion)
        .where(CvVersion.cv_id == cv_id)
        .order_by(CvVersion.created_at.desc(), CvVersion.id.desc())
    )
    return list(session.execute(stmt).scalars())


def get_version(
    session: Session, cv_id: int, user_id: int, version_id: int
) -> CvVersion | None:
    """Fetch one version snapshot, scoped to its CV's owner.

    Args:
        session: The database session.
        cv_id: The version's CV.
        user_id: The caller's user id -- must own `cv_id`.
        version_id: The version's id.

    Returns:
        The `CvVersion`, or `None` if it doesn't exist, doesn't belong to
        `cv_id`, or `cv_id` isn't owned by `user_id`.
    """
    owner_check = select(Cv.id).where(Cv.id == cv_id, Cv.user_id == user_id)
    if session.execute(owner_check).scalar_one_or_none() is None:
        return None

    stmt = select(CvVersion).where(CvVersion.id == version_id, CvVersion.cv_id == cv_id)
    return session.execute(stmt).scalar_one_or_none()


def get_preferences(session: Session, user_id: int) -> list[Preference]:
    """List all preference rows for a user.

    Args:
        session: The database session.
        user_id: The user whose preferences to list.

    Returns:
        The user's `Preference` rows.
    """
    stmt = (
        select(Preference).where(Preference.user_id == user_id).order_by(Preference.key)
    )
    return list(session.execute(stmt).scalars())


def set_preference(session: Session, user_id: int, key: str, value: str) -> Preference:
    """Upsert one preference key/value pair for a user.

    Args:
        session: The database session.
        user_id: The user the preference belongs to.
        key: The preference key.
        value: The preference value.

    Returns:
        The `Preference` row after the write.
    """
    existing = session.get(Preference, (user_id, key))
    if existing is not None:
        existing.value = value
        session.commit()
        session.refresh(existing)
        return existing

    pref = Preference(user_id=user_id, key=key, value=value)
    session.add(pref)
    try:
        session.commit()
    except IntegrityError:
        # Why: a second writer inserted the same (user_id, key) between
        # our existence check and our insert; that writer's value already
        # won, so fall back to an update instead of raising.
        session.rollback()
        existing = session.get(Preference, (user_id, key))
        assert existing is not None
        existing.value = value
        session.commit()
        session.refresh(existing)
        return existing

    session.refresh(pref)
    return pref


def get_user_by_auth_identity(
    session: Session, auth_provider: str, auth_provider_id: str
) -> User | None:
    """Find the account row for a provider identity, if it exists.

    Why:
        The provider's stable subject id -- not the email, which a user can
        change at the provider -- is what identifies an account across
        devices and across sign-ins.

    Args:
        session: The database session.
        auth_provider: Provider key, e.g. `"google"`.
        auth_provider_id: The provider's stable subject id for this user.

    Returns:
        The matching `User`, or None if this identity has never signed in.
    """
    return session.execute(
        select(User).where(
            User.auth_provider == auth_provider,
            User.auth_provider_id == auth_provider_id,
        )
    ).scalar_one_or_none()


def promote_user_to_account(
    session: Session,
    user: User,
    new_session_token: str,
    auth_provider: str,
    auth_provider_id: str,
    email: str | None,
    display_name: str | None,
) -> User:
    """Turn the caller's existing anonymous row into an account row.

    Why:
        This is the first-sign-in path, and it is deliberately not a data
        migration: the anonymous row already owns the user's CVs and
        preferences, so stamping the account identity onto that same row
        carries everything across with zero copying and zero chance of a
        partial move.

    Args:
        session: The database session.
        user: The anonymous row identified by the caller's session cookie.
        new_session_token: Replacement token. The row's current one existed
            before this user authenticated, so it must not survive into the
            account -- see `rotate_session_token`.
        auth_provider: Provider key, e.g. `"google"`.
        auth_provider_id: The provider's stable subject id.
        email: The account's email, if the provider supplied one.
        display_name: The account's display name, if the provider supplied one.

    Returns:
        The same row, now carrying the account identity.
    """
    user.session_token = new_session_token
    user.auth_provider = auth_provider
    user.auth_provider_id = auth_provider_id
    user.email = email
    user.display_name = display_name
    session.commit()
    session.refresh(user)
    return user


def claim_anonymous_user(
    session: Session, anonymous_user: User, account_user: User
) -> User:
    """Move an anonymous session's CVs and preferences into an existing account.

    Why:
        Signing in on a second browser resolves to an account row that
        already exists, so the CVs written while anonymous in *this*
        browser would otherwise be stranded on a row nothing points at any
        more. Moving them is the behaviour that never loses a user's work.

        Preferences are merged the other way round: a key the account
        already has keeps the account's value, and only keys it lacks are
        carried over. The account's own settings are the durable ones; a
        throwaway anonymous session should not silently redecorate them.

    Args:
        session: The database session.
        anonymous_user: The row identified by the caller's current cookie.
        account_user: The already-existing account row to merge into.

    Returns:
        `account_user`, now owning the merged CVs and preferences.

    Raises:
        ValueError: If asked to merge a row into itself, which would delete
            the very row it just moved everything to.
    """
    if anonymous_user.id == account_user.id:
        message = "claim_anonymous_user called with the same row twice."
        raise ValueError(message)

    session.execute(
        update(Cv)
        .where(Cv.user_id == anonymous_user.id)
        .values(user_id=account_user.id)
    )

    account_keys = {
        key
        for (key,) in session.execute(
            select(Preference.key).where(Preference.user_id == account_user.id)
        )
    }
    for preference in session.execute(
        select(Preference).where(Preference.user_id == anonymous_user.id)
    ).scalars():
        if preference.key not in account_keys:
            session.add(
                Preference(
                    user_id=account_user.id,
                    key=preference.key,
                    value=preference.value,
                )
            )
        session.delete(preference)

    # The anonymous row is now empty of anything worth keeping, and leaving
    # it would let its still-valid cookie resolve to a live, CV-less user.
    session.delete(anonymous_user)
    session.commit()
    session.refresh(account_user)
    return account_user


def get_user_by_token(session: Session, session_token: str) -> User | None:
    """Look up a session's user without creating one.

    Why this exists next to `get_or_create_user_by_token`: endpoints that
    merely *report* on the session (`GET /api/auth/me`) must not bring a
    user row into existence. The landing page asks that question on every
    visit, so creating there would mint a row and a year-long cookie for
    every crawler and link preview that touches the front page.

    Args:
        session: The database session.
        session_token: The opaque token from the client's session cookie.

    Returns:
        The matching `User`, or None if the token belongs to no row.
    """
    return session.execute(
        select(User).where(User.session_token == session_token)
    ).scalar_one_or_none()


def create_account_user(
    session: Session,
    session_token: str,
    auth_provider: str,
    auth_provider_id: str,
    email: str | None,
    display_name: str | None,
) -> User:
    """Create a brand-new row for an account, owning nothing yet.

    Why:
        Used when someone already signed in switches to a different
        provider identity. Their current row belongs to the account they
        were signed into and must not be rewritten, so the incoming
        identity gets a row of its own.

    Args:
        session: The database session.
        session_token: The token the new session's cookie will carry.
        auth_provider: Provider key, e.g. `"google"`.
        auth_provider_id: The provider's stable subject id.
        email: The account's email, if the provider supplied one.
        display_name: The account's display name, if supplied.

    Returns:
        The newly created account row.
    """
    user = User(
        session_token=session_token,
        created_at=utc_now(),
        auth_provider=auth_provider,
        auth_provider_id=auth_provider_id,
        email=email,
        display_name=display_name,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user: User) -> None:
    """Erase an account and everything that belongs to it.

    Why:
        A published app has to let people take their data back out of it,
        and a privacy policy that promises deletion has to be backed by
        something that deletes.

    Why one `delete` is enough: every table that references a user does so
    with `ON DELETE CASCADE` (`db.models`), and SQLite has foreign keys
    enabled for the same reason (`db.session`), so the CVs, their version
    history and the preferences go with the row. Deleting them by hand
    here would be a second description of the schema, free to fall out of
    step with the first.

    Args:
        session: The database session.
        user: The account to erase.
    """
    session.delete(user)
    session.commit()


def rotate_session_token(session: Session, user: User, new_session_token: str) -> User:
    """Replace a row's session token, invalidating every cookie carrying the old one.

    Why:
        Two things need this. Signing in must not keep a token that existed
        before authentication -- whoever used the browser first may know it,
        and it would otherwise stay valid against the account for a year
        (session fixation). Signing out must actually revoke, or the control
        promises something it does not do.

    Args:
        session: The database session.
        user: The row whose token is being replaced.
        new_session_token: The replacement token.

    Returns:
        The same row, carrying the new token.
    """
    user.session_token = new_session_token
    session.commit()
    session.refresh(user)
    return user
