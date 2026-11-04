"""Create the pool of accounts the e2e suite runs as, using production code.

Why a script rather than an HTTP call: there is no endpoint that creates
an account without going through Google, and adding one would put an
authentication bypass in the shipped server. This runs the same
`repository.create_account_user` the OAuth callback runs, against the
throwaway database the suite's own backend was started on.

Why a pool rather than one account: every test needs to start from an
empty CV list, the way a new visitor does. Before accounts were required
that came for free -- a fresh browser context meant a fresh anonymous
session -- and handing each test its own account restores it. They are
created in one process because starting the interpreter costs more than
all the rows put together.

Why existing accounts are emptied rather than left alone: the pool hands
out accounts by a fixed index, so account 7 in one run is account 7 in
the next, and the database in the temp directory outlives the run. Left
as they were, a test would inherit whatever the *previous* run's test at
that index wrote -- a `ui_theme` of dark, a collapsed sidebar, a pile of
CVs. That was observed directly: a second consecutive run failed
dark-mode (the page came up already dark) and persistence (the collapsed
rail hides "Create new CV"), while the same suite passed whenever the
database file happened to be fresh.

Deleting the database file instead would be simpler, but there is no
moment to do it: Playwright starts the backend before `globalSetup`
runs, and it re-imports the config in worker processes, so a reset at
config load fires again mid-run and pulls the file out from under the
live server.

Called by `e2e/global-setup.ts` with the pool size as `argv[1]`; the
database URL comes from `RENDERCV_WEB_DATABASE_URL` in the environment,
which Playwright sets for both this and the backend it launched.
"""

import sys

from rendercv_web.db import repository
from rendercv_web.db.session import (
    build_session_factory,
    create_engine_from_url,
    resolve_database_url,
)
from sqlalchemy.orm import Session

PROVIDER = "google"


def empty_account(session: Session, user_id: int) -> None:
    """Remove every CV and preference the account owns.

    Args:
        session: The database session.
        user_id: The account whose data should be cleared.
    """
    for cv in repository.list_cvs(session, user_id):
        repository.delete_cv(session, cv.id, user_id)
    for preference in repository.get_preferences(session, user_id):
        session.delete(preference)
    session.commit()


def main() -> None:
    """Create `argv[1]` accounts, and empty any that already exist."""
    count = int(sys.argv[1])
    factory = build_session_factory(create_engine_from_url(resolve_database_url()))
    with factory() as session:
        for index in range(count):
            subject = f"e2e-subject-{index}"
            token = f"e2e-token-{index}"
            existing = repository.get_user_by_auth_identity(session, PROVIDER, subject)
            if existing is None:
                repository.create_account_user(
                    session,
                    token,
                    auth_provider=PROVIDER,
                    auth_provider_id=subject,
                    email=f"e2e-{index}@example.com",
                    display_name=f"E2E Tester {index}",
                )
            else:
                repository.rotate_session_token(session, existing, token)
                empty_account(session, existing.id)


if __name__ == "__main__":
    main()
