"""Ask a deployment's database who is using it, without a psql session.

Why this exists:
    Answering "how many people signed in?" or "which account holds this CV?"
    against the Render database meant assembling a `psql` invocation by
    hand, and every attempt at that leaked or fumbled something: the
    connection string in the shell history, then in the terminal's window
    title, then a placeholder pasted literally, then Render's *internal*
    hostname, which resolves nowhere outside Render. None of those are
    interesting problems, and all of them cost real time.

    So the connection string is typed once, invisibly, into a prompt, and
    every query lives here where it can be read before it is run.

Why emails are masked by default:
    This database now holds other people's CVs. Counting accounts is
    ordinary operation of the service; printing a list of everyone's email
    addresses is not, and the privacy policy this deployment publishes says
    the data is not used for anything else. `--full-emails` is there for the
    one case that needs it -- finding which of *your own* accounts holds a
    CV -- and has to be asked for.

Usage:
    uv run --extra postgres python scripts/db_report.py
    uv run --extra postgres python scripts/db_report.py --cv Quan
    uv run --extra postgres python scripts/db_report.py --cv Quan --full-emails

The connection string comes from `RENDERCV_WEB_DATABASE_URL` if it is set,
and otherwise from a hidden prompt. Paste Render's **External** Database URL
-- the internal one only resolves from inside Render's own network.
"""

import argparse
import getpass
import os
import sys

import sqlalchemy as sa
from rendercv_web.db.session import create_engine_from_url

DATABASE_URL_ENV_VAR = "RENDERCV_WEB_DATABASE_URL"

# What a dashboard shows in place of a secret. Render fills its four
# connection fields with 110 of these, the same count for all of them, so
# selecting the text and copying it yields a row of bullets rather than the
# value -- see `looks_like_a_mask`.
MASK_CHARACTERS = "\u2022\u25cf\u00b7*\u2219"


def resolve_database_url() -> str:
    """Find the database to talk to, asking for it if the environment is silent.

    Returns:
        The connection string.

    Raises:
        SystemExit: When nothing was given, so the caller sees a sentence
            rather than a stack trace.
    """
    from_env = os.environ.get(DATABASE_URL_ENV_VAR)
    if from_env:
        # Cleaned like a paste, because it usually is one: the shell that
        # set it may have taken the value from a clipboard, and
        # `Get-Clipboard` keeps the trailing newline.
        return clean_pasted_url(from_env)

    # `getpass`, not `input`: the string carries the database password, and
    # a terminal's scrollback outlives the session that printed it.
    entered = getpass.getpass(
        "Paste the External Database URL (nothing will appear as you paste): "
    )
    return clean_pasted_url(entered)


def clean_pasted_url(entered: str) -> str:
    """Tidy a pasted connection string, and refuse an unusable one clearly.

    Why this is not left to SQLAlchemy: its answer is
    `Could not parse SQLAlchemy URL from given URL string`, followed by a
    stack trace, which does not tell you that you copied the row below the
    one you meant. Render's Info page offers the URL and a ready-made
    `psql ...` command directly under it, and the two look alike at a
    glance.

    Nothing derived from the string is printed: it carries the password.

    Args:
        entered: Whatever arrived from the prompt.

    Returns:
        The cleaned connection string.

    Raises:
        SystemExit: When it cannot be a connection string, with a sentence
            saying which row to copy instead.
    """
    cleaned = entered.strip().strip('"').strip("'")
    # Render's "PSQL Command" row is the URL with `psql ` in front of it.
    if cleaned.startswith("psql "):
        cleaned = cleaned[len("psql ") :].strip().strip('"').strip("'")

    if not cleaned:
        print("Nothing was pasted, so there is nothing to connect to.", file=sys.stderr)
        raise SystemExit(1)

    if looks_like_a_mask(cleaned):
        print(
            "What was pasted is the row of dots the dashboard shows,", file=sys.stderr
        )
        print("not the value behind them.", file=sys.stderr)
        print(file=sys.stderr)
        print(
            "Those fields hide their contents, so selecting the text and\n"
            "copying it gives you the mask. Use the copy button at the end of\n"
            "the row instead -- it puts the real string on the clipboard\n"
            "without ever showing it.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if "://" not in cleaned:
        print("That does not look like a connection string.", file=sys.stderr)
        print(file=sys.stderr)
        print(
            "On Render, copy the row named *External Database URL* -- the one\n"
            "starting `postgresql://`. The `Hostname` row on its own is not\n"
            "enough, and the internal URL only resolves from inside Render.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    return cleaned


def looks_like_a_mask(text: str) -> bool:
    """Whether `text` is a dashboard's placeholder rather than a value.

    Args:
        text: The cleaned paste.

    Returns:
        Whether every character is one a dashboard uses to hide a secret.
    """
    return bool(text) and all(character in MASK_CHARACTERS for character in text)


def mask_email(email: str | None, full: bool) -> str:
    """Shorten an email to something recognisable but not reusable.

    Args:
        email: The address, or `None` for an anonymous row.
        full: Whether the caller asked for the address in full.

    Returns:
        The address, a masked form of it, or a placeholder.
    """
    if not email:
        return "(anonymous)"
    if full:
        return email
    name, _, domain = email.partition("@")
    head = name[:2] if len(name) > 2 else name[:1]
    return f"{head}{'*' * 3}@{domain}"


def print_summary(connection: sa.Connection, full_emails: bool) -> None:
    """Report how many people use this deployment, and how much they hold.

    Args:
        connection: An open connection.
        full_emails: Whether to print addresses unmasked.
    """
    counts = connection.execute(
        sa.text(
            "SELECT "
            "  count(*) FILTER (WHERE auth_provider IS NOT NULL) AS accounts, "
            "  count(*) FILTER (WHERE auth_provider IS NULL) AS abandoned "
            "FROM users"
        )
    ).one()
    print(f"Signed-in accounts:      {counts.accounts}")
    print(f"Abandoned sign-ins:      {counts.abandoned}")
    print()

    rows = connection.execute(
        sa.text(
            "SELECT u.email AS email, count(c.id) AS cvs, max(c.updated_at) AS last_edit "
            "FROM users u LEFT JOIN cvs c ON c.user_id = u.id "
            "WHERE u.auth_provider IS NOT NULL "
            "GROUP BY u.id, u.email "
            "ORDER BY cvs DESC"
        )
    ).all()
    if not rows:
        print("No accounts yet.")
        return
    print(f"{'account':<28} {'CVs':>4}  last edit")
    for row in rows:
        print(
            f"{mask_email(row.email, full_emails):<28} {row.cvs:>4}  {row.last_edit or '-'}"
        )


def print_cv_search(connection: sa.Connection, needle: str, full_emails: bool) -> None:
    """Report which account holds the CVs whose name contains `needle`.

    Args:
        connection: An open connection.
        needle: Fragment of the CV name to look for, case-insensitively.
        full_emails: Whether to print addresses unmasked.
    """
    rows = connection.execute(
        sa.text(
            "SELECT u.email AS email, c.name AS name, c.updated_at AS updated_at "
            "FROM cvs c JOIN users u ON u.id = c.user_id "
            "WHERE lower(c.name) LIKE :pattern "
            "ORDER BY c.updated_at DESC"
        ),
        {"pattern": f"%{needle.lower()}%"},
    ).all()

    if not rows:
        print(f'No CV has "{needle}" in its name.')
        print()
        print("If you expected one, it never reached the server -- which is a")
        print("different problem from being on the wrong account.")
        return

    print(f'CVs matching "{needle}":')
    print()
    print(f"{'account':<28} {'CV name':<32} last edit")
    for row in rows:
        print(
            f"{mask_email(row.email, full_emails):<28} {row.name:<32} {row.updated_at}"
        )


def main() -> None:
    """Parse the arguments, open the database, and print what was asked for."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--cv",
        metavar="TEXT",
        help="Show which account holds the CVs whose name contains TEXT.",
    )
    parser.add_argument(
        "--full-emails",
        action="store_true",
        help="Print email addresses in full instead of masking them.",
    )
    args = parser.parse_args()

    # The application's own builder, so this script accepts exactly the
    # URL forms the server does -- `postgres://` included, which
    # SQLAlchemy itself rejects.
    engine = create_engine_from_url(resolve_database_url())
    try:
        with engine.connect() as connection:
            if args.cv:
                print_cv_search(connection, args.cv, args.full_emails)
            else:
                print_summary(connection, args.full_emails)
    except sa.exc.ArgumentError as error:
        print(f"That connection string could not be read: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    except sa.exc.OperationalError as error:
        print(f"Could not connect: {error.orig}", file=sys.stderr)
        # Offered only for the failure it explains. Printed unconditionally
        # it would be advice about hostnames attached to, say, a missing
        # file -- the kind of hint that sends people the wrong way.
        if "translate host name" in str(error.orig) or "could not resolve" in str(
            error.orig
        ):
            print(file=sys.stderr)
            print(
                "A host with no dots is Render's *internal* name and resolves\n"
                "only from inside Render. Copy the External Database URL.",
                file=sys.stderr,
            )
        raise SystemExit(1) from error
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
