"""Anonymous device-session identity: a signed cookie backs an implicit account.

Why:
    Phase 4b (auth model option A, docs/plans/completed/cv-editor-web-app.md):
    there is no email/password/OAuth yet -- a signed, HTTPOnly cookie's
    *token* is the only thing that identifies a `User` row. Signing (HMAC-
    SHA256 over the token with a server secret) means a client cannot forge
    or guess another session's cookie by editing the value; the token
    itself is still readable in plain text, which is fine -- it grants
    nothing beyond "this browser's own CVs", the same as an unsigned random
    id would, until real accounts exist.
"""

import hmac
import logging
import os
import secrets
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from .db import repository
from .db.models import User
from .db.session import get_session

logger = logging.getLogger("rendercv_web")

SESSION_COOKIE_NAME = "rendercv_session"
SECRET_ENV_VAR = "RENDERCV_WEB_SECRET"
SESSION_COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 365
HTTPS_ENV_VAR = "RENDERCV_WEB_HTTPS"

# Why a hardcoded fallback at all: local `uvicorn` runs must work with zero
# setup. THIS VALUE IS NOT SAFE FOR PRODUCTION -- it is public (checked into
# a public repository), so anyone can forge a validly-signed session cookie
# against it. Production deployments MUST set RENDERCV_WEB_SECRET to a long
# random value kept out of source control; nothing here enforces that, so
# treat this default as a loud, deliberate development-only convenience.
DEV_DEFAULT_SECRET = "insecure-dev-only-secret-do-not-use-in-production"


def resolve_secret() -> str:
    """Read the cookie-signing secret, warning loudly if it's the dev default.

    Returns:
        The secret configured via `RENDERCV_WEB_SECRET`, or the loud dev
        default if it is unset.
    """
    secret = os.environ.get(SECRET_ENV_VAR)
    if secret:
        return secret
    logger.warning(
        "%s is not set; signing session cookies with an insecure, publicly"
        " known development secret. Set %s before deploying.",
        SECRET_ENV_VAR,
        SECRET_ENV_VAR,
    )
    return DEV_DEFAULT_SECRET


def cookie_is_https_only() -> bool:
    """Whether session cookies should be marked `Secure`.

    Why this is a switch and not a constant: local development serves the
    app over plain http://localhost, where a `Secure` cookie is simply
    never sent and nothing works. Every real deployment serves HTTPS, where
    omitting `Secure` lets the session cookie be read off the wire. Neither
    value is right for both, so the deployment states which one it is.

    Returns:
        True when `RENDERCV_WEB_HTTPS` is set to a truthy value.
    """
    return os.environ.get(HTTPS_ENV_VAR, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def generate_session_token() -> str:
    """Create a new random opaque session token.

    Returns:
        A URL-safe random token, unguessable and unique with overwhelming
        probability.
    """
    return secrets.token_urlsafe(32)


def sign(token: str, secret: str) -> str:
    """Compute the HMAC-SHA256 signature of `token` under `secret`.

    Args:
        token: The session token to sign.
        secret: The server-side signing secret.

    Returns:
        Hex-encoded signature.
    """
    return hmac.new(secret.encode("utf-8"), token.encode("utf-8"), "sha256").hexdigest()


def encode_cookie(token: str, secret: str) -> str:
    """Build the signed cookie value (`token.signature`) for `token`.

    Args:
        token: The session token to encode.
        secret: The server-side signing secret.

    Returns:
        The value to store in the session cookie.
    """
    return f"{token}.{sign(token, secret)}"


def decode_cookie(cookie_value: str, secret: str) -> str | None:
    """Recover and verify the session token from a signed cookie value.

    Args:
        cookie_value: The raw cookie value as sent by the client.
        secret: The server-side signing secret.

    Returns:
        The token, if the signature is valid; `None` if the cookie is
        malformed or its signature doesn't match (tampered with, or signed
        under a different secret) -- the caller should treat that the same
        as "no cookie" and issue a fresh session.
    """
    token, separator, signature = cookie_value.rpartition(".")
    if not separator or not token or not signature:
        return None
    expected_signature = sign(token, secret)
    if not hmac.compare_digest(signature, expected_signature):
        return None
    return token


def get_current_user(
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    rendercv_session: Annotated[str | None, Cookie()] = None,
) -> User:
    """Resolve (or create) the anonymous user for this request's session cookie.

    Why:
        A browser's first request carries no cookie: a new token is minted,
        signed, and set on the response here, once, so every persistence
        endpoint gets session identity the same way instead of each
        implementing its own cookie handling.

    Args:
        response: The response to attach a fresh session cookie to, if one
            is needed.
        session: The database session.
        rendercv_session: The raw cookie value, if the client sent one.

    Returns:
        The `User` row identifying this browser's session.
    """
    secret = resolve_secret()
    token = decode_cookie(rendercv_session, secret) if rendercv_session else None

    if token is None:
        token = generate_session_token()
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=encode_cookie(token, secret),
            httponly=True,
            samesite="lax",
            secure=cookie_is_https_only(),
            max_age=SESSION_COOKIE_MAX_AGE_SECONDS,
        )

    return repository.get_or_create_user_by_token(session, token)


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_account(
    session: Annotated[Session, Depends(get_session)],
    rendercv_session: Annotated[str | None, Cookie()] = None,
) -> User:
    """Resolve the signed-in account for this request, or refuse it.

    Why this exists next to `get_current_user`: that dependency *creates*
    an anonymous row for any caller, which is what makes the editor usable
    without an account. Endpoints holding a user's own data need the
    opposite -- a caller with no account must be turned away, not handed a
    brand-new identity.

    Why it resolves the cookie by hand instead of depending on
    `get_current_user` and checking afterwards: doing it that way would
    still mint a row and a year-long cookie before rejecting the request,
    so every unauthenticated probe would grow the `users` table. A refusal
    must not leave anything behind.

    Args:
        session: The database session.
        rendercv_session: The raw session cookie, if the client sent one.

    Returns:
        The `User` row for the signed-in account.

    Raises:
        HTTPException: 401 when the caller has no session, an unknown
            session, or a session that has never been signed in.
    """
    token = (
        decode_cookie(rendercv_session, resolve_secret()) if rendercv_session else None
    )
    user = repository.get_user_by_token(session, token) if token else None

    if user is None or user.auth_provider is None:
        raise HTTPException(
            status_code=401,
            detail="Sign in to use this endpoint.",
        )
    return user


CurrentAccount = Annotated[User, Depends(get_current_account)]
