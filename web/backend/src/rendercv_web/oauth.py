"""Google sign-in: the OAuth 2.0 authorization-code flow and its endpoints.

Why:
    Phase 6 of the web editor plan. Signing in must not introduce a second
    identity mechanism: the session cookie set here is the *same* signed
    `session_token` cookie the anonymous flow already uses (`auth.py`), it
    simply points at a row that now carries an account identity. That is
    what lets `get_current_user` stay untouched, and what lets an anonymous
    session be claimed without moving anything (see
    `repository.claim_anonymous_user`).

Why the whole feature is optional:
    A deployment with no Google credentials configured is a supported,
    fully working deployment -- the editor is usable anonymously. The
    endpoints here report that state rather than failing obscurely, and
    the client hides the sign-in UI when `GET /api/auth/me` says the
    provider is unavailable.

Why `id_token` is never parsed:
    The access token is exchanged server-to-server over TLS and then spent
    on Google's own userinfo endpoint, also over TLS. That avoids shipping
    a JWT verification path, and its key rotation, for information Google
    will hand over directly.
"""

import dataclasses
import logging
import os
import secrets
import urllib.parse
from typing import Annotated

import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from .auth import (
    SESSION_COOKIE_MAX_AGE_SECONDS,
    SESSION_COOKIE_NAME,
    CurrentAccount,
    CurrentUser,
    cookie_is_https_only,
    decode_cookie,
    encode_cookie,
    generate_session_token,
    resolve_secret,
)
from .db import repository
from .db.session import get_session
from .models import AuthStatus

logger = logging.getLogger("rendercv_web")

router = APIRouter(tags=["auth"], prefix="/api/auth")

AUTH_PROVIDER = "google"

CLIENT_ID_ENV_VAR = "GOOGLE_OAUTH_CLIENT_ID"
CLIENT_SECRET_ENV_VAR = "GOOGLE_OAUTH_CLIENT_SECRET"
REDIRECT_URI_ENV_VAR = "GOOGLE_OAUTH_REDIRECT_URI"

# Why this default: in development the browser talks to the SvelteKit dev
# server, which proxies `/api` to this backend. Sending Google back through
# that origin is what makes the session cookie land on the origin the app is
# actually served from. A deployment sets the variable to its own URL.
DEFAULT_REDIRECT_URI = "http://localhost:5173/api/auth/google/callback"

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"

STATE_COOKIE_NAME = "rendercv_oauth_state"
STATE_COOKIE_MAX_AGE_SECONDS = 600

# Where the browser is sent once sign-in succeeds or is abandoned. Relative,
# so it works on whatever origin serves the app.
POST_LOGIN_PATH = "/app"

HTTP_TIMEOUT_SECONDS = 10.0

SessionDep = Annotated[Session, Depends(get_session)]


@dataclasses.dataclass(slots=True)
class GoogleIdentity:
    """The identity fields taken from Google's userinfo response.

    Why a dataclass and not the raw JSON: it is the seam the tests replace
    (`fetch_google_identity`), so the flow can be exercised end to end
    without a network or real credentials.
    """

    subject: str
    email: str | None
    display_name: str | None


@dataclasses.dataclass(slots=True)
class OAuthConfig:
    """Resolved Google OAuth settings."""

    client_id: str
    client_secret: str
    redirect_uri: str


def resolve_oauth_config() -> OAuthConfig | None:
    """Read the Google OAuth settings from the environment.

    Why read on every call rather than caching at import: deployments and
    tests set these per-process, and a cached `None` from import time would
    make a correctly configured server look unconfigured forever.

    Returns:
        The configuration, or None when either credential is missing --
        which is a supported state, not an error.
    """
    client_id = os.environ.get(CLIENT_ID_ENV_VAR)
    client_secret = os.environ.get(CLIENT_SECRET_ENV_VAR)
    if not client_id or not client_secret:
        return None
    return OAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=os.environ.get(REDIRECT_URI_ENV_VAR, DEFAULT_REDIRECT_URI),
    )


def require_oauth_config() -> OAuthConfig:
    """Return the OAuth configuration, or fail with an honest status.

    Returns:
        The resolved configuration.

    Raises:
        HTTPException: 503 when the provider is not configured, so a client
            can tell "this deployment has no sign-in" apart from "sign-in
            is broken".
    """
    config = resolve_oauth_config()
    if config is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Google sign-in is not configured on this server. Set"
                f" {CLIENT_ID_ENV_VAR} and {CLIENT_SECRET_ENV_VAR} to enable it."
            ),
        )
    return config


def fetch_google_identity(code: str, config: OAuthConfig) -> GoogleIdentity:
    """Exchange an authorization code for the signing-in user's identity.

    Why both HTTP calls live in one function: this is the single seam the
    tests replace, so everything around it -- state checking, account
    resolution, the anonymous merge, cookie handling -- is exercised for
    real without a network.

    Args:
        code: The one-time authorization code Google put on the callback.
        config: The resolved client credentials and redirect URI.

    Returns:
        The identity Google reports for the code.

    Raises:
        HTTPException: 502 if Google rejects the exchange, or returns a
            response without the fields the flow depends on.
    """
    with httpx.Client(timeout=HTTP_TIMEOUT_SECONDS) as client:
        token_response = client.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                "code": code,
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "redirect_uri": config.redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_response.status_code != 200:
            logger.warning(
                "Google token exchange failed with status %s",
                token_response.status_code,
            )
            raise HTTPException(status_code=502, detail="Google rejected the sign-in.")

        access_token = token_response.json().get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=502, detail="Google returned no access token."
            )

        userinfo_response = client.get(
            GOOGLE_USERINFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_response.status_code != 200:
            logger.warning(
                "Google userinfo failed with status %s", userinfo_response.status_code
            )
            raise HTTPException(
                status_code=502, detail="Could not read the Google profile."
            )

    userinfo = userinfo_response.json()
    subject = userinfo.get("sub")
    if not subject:
        raise HTTPException(status_code=502, detail="Google returned no account id.")
    return GoogleIdentity(
        subject=str(subject),
        email=userinfo.get("email"),
        display_name=userinfo.get("name"),
    )


@router.get("/me")
def read_auth_status(
    session: SessionDep,
    rendercv_session: Annotated[str | None, Cookie()] = None,
) -> AuthStatus:
    """Report who the caller is, and whether sign-in is available at all.

    Why one endpoint for both: the client needs both answers before it can
    decide what to render, and asking twice would let them disagree.

    Why this resolves the session by hand instead of depending on
    `CurrentUser`: that dependency *creates* a row and issues a year-long
    cookie for any caller without one. The landing page asks this question
    on every visit, so depending on it would mint a row for every crawler,
    link preview and uptime check that touches the public front page. A
    question about the session must not bring one into existence.

    Args:
        session: The database session.
        rendercv_session: The raw session cookie, if the client sent one.

    Returns:
        The caller's account state plus provider availability.
    """
    token = (
        decode_cookie(rendercv_session, resolve_secret()) if rendercv_session else None
    )
    user = repository.get_user_by_token(session, token) if token else None

    return AuthStatus(
        authenticated=user is not None and user.auth_provider is not None,
        email=user.email if user else None,
        display_name=user.display_name if user else None,
        provider_available=resolve_oauth_config() is not None,
    )


@router.get("/google/start")
def start_google_sign_in() -> RedirectResponse:
    """Begin the authorization-code flow by redirecting to Google.

    Why a signed state cookie: the `state` parameter must come back
    unchanged for the callback to be trustworthy, and signing it with the
    server secret means a forged callback cannot mint one. Without it, a
    third party could complete a sign-in the user never started.

    Returns:
        A redirect to Google's consent screen, carrying the state cookie.
    """
    config = require_oauth_config()
    state = secrets.token_urlsafe(24)

    query = urllib.parse.urlencode(
        {
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "online",
            "prompt": "select_account",
        }
    )
    redirect = RedirectResponse(f"{GOOGLE_AUTH_ENDPOINT}?{query}", status_code=307)
    redirect.set_cookie(
        key=STATE_COOKIE_NAME,
        value=encode_cookie(state, resolve_secret()),
        httponly=True,
        samesite="lax",
        secure=cookie_is_https_only(),
        max_age=STATE_COOKIE_MAX_AGE_SECONDS,
    )
    return redirect


@router.get("/google/callback")
def complete_google_sign_in(
    session: SessionDep,
    current_user: CurrentUser,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    rendercv_oauth_state: Annotated[str | None, Cookie()] = None,
) -> Response:
    """Finish sign-in: verify state, resolve the account, set the cookie.

    The caller's current row is either anonymous or an account already, and
    the two cases must never be treated alike:

    - Anonymous, identity unknown -- promote that row in place, so its CVs
      come along without being copied and cannot be half-moved.
    - Anonymous, identity known -- move the row's CVs into the existing
      account and retire the row (`repository.claim_anonymous_user`).
    - Already an account -- this is an account switch, invited by the
      `prompt=select_account` on `/google/start`. The current row belongs
      to somebody's account: rewriting its identity would destroy that
      account and hand its CVs to the incoming user, and merging would
      delete it outright. So nothing is promoted or merged; the incoming
      identity gets its own session.

    Args:
        session: The database session.
        current_user: The row this browser's cookie currently resolves to.
        code: Google's one-time authorization code.
        state: The state value echoed back by Google.
        error: Set by Google when the user declined, or the request failed.
        rendercv_oauth_state: The signed state cookie set at `/google/start`.

    Returns:
        A redirect back into the editor, carrying the session cookie of
        whichever row the caller is now.

    Raises:
        HTTPException: 400 if the state check fails -- a callback this
            server did not start.
    """
    config = require_oauth_config()

    if error:
        # The user pressed "cancel" on Google's screen. Not an error worth a
        # stack trace: send them back to where they started.
        logger.info("Google sign-in was declined: %s", error)
        declined = RedirectResponse(POST_LOGIN_PATH, status_code=303)
        declined.delete_cookie(STATE_COOKIE_NAME)
        return declined

    expected_state = (
        decode_cookie(rendercv_oauth_state, resolve_secret())
        if rendercv_oauth_state
        else None
    )
    state_is_valid = bool(
        state and expected_state and secrets.compare_digest(state, expected_state)
    )
    if not code or not state_is_valid:
        # Returned rather than raised so the spent state cookie can be
        # cleared on the way out: leaving it valid for its full ten minutes
        # keeps a replayable state around, which is the exact window the
        # state parameter exists to close.
        rejected = JSONResponse(
            status_code=400,
            content={"detail": "This sign-in link is invalid or has expired."},
        )
        rejected.delete_cookie(STATE_COOKIE_NAME)
        return rejected

    identity = fetch_google_identity(code, config)

    existing_account = repository.get_user_by_auth_identity(
        session, AUTH_PROVIDER, identity.subject
    )
    caller_is_signed_in = current_user.auth_provider is not None

    if existing_account is not None and existing_account.id == current_user.id:
        # Already signed into this account in this browser; nothing to do.
        account = existing_account
    elif caller_is_signed_in:
        # Switching accounts. The current row is somebody's account, so it is
        # left completely alone -- including its CVs, which belong to the
        # account being switched away from, not to this sign-in.
        account = existing_account or repository.create_account_user(
            session,
            generate_session_token(),
            auth_provider=AUTH_PROVIDER,
            auth_provider_id=identity.subject,
            email=identity.email,
            display_name=identity.display_name,
        )
    elif existing_account is None:
        account = repository.promote_user_to_account(
            session,
            current_user,
            generate_session_token(),
            auth_provider=AUTH_PROVIDER,
            auth_provider_id=identity.subject,
            email=identity.email,
            display_name=identity.display_name,
        )
    else:
        account = repository.claim_anonymous_user(
            session, current_user, existing_account
        )

    redirect = RedirectResponse(POST_LOGIN_PATH, status_code=303)
    redirect.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=encode_cookie(account.session_token, resolve_secret()),
        httponly=True,
        samesite="lax",
        secure=cookie_is_https_only(),
        max_age=SESSION_COOKIE_MAX_AGE_SECONDS,
    )
    redirect.delete_cookie(STATE_COOKIE_NAME)
    return redirect


@router.post("/logout", status_code=204)
def sign_out(
    response: Response,
    session: SessionDep,
    rendercv_session: Annotated[str | None, Cookie()] = None,
) -> None:
    """Sign out by clearing the cookie *and* invalidating the token it carried.

    Why the token is rotated and not just the cookie dropped: clearing a
    cookie only affects the browser doing the clearing. Anyone holding a
    copy of that cookie value -- taken from a shared machine, a synced
    profile, or a proxy log from before HTTPS was enforced -- would keep
    full access for the cookie's remaining year while the user believes
    the session is closed. A control labelled "Sign out" has to revoke.

    Because one account has one token (`db.models.User` records why), this
    signs the account out of every device rather than only this one. That
    is the safe direction of the two: an unexpected sign-out elsewhere
    costs a click, an unrevoked session costs the account.

    Anonymous rows are deliberately exempt. Their token is the only way
    back to their CVs, so rotating it would strand a user's work rather
    than protecting anything -- there is no account to protect yet.

    Args:
        response: The response to clear the session cookie on.
        session: The database session.
        rendercv_session: The raw session cookie, if the client sent one.
    """
    response.delete_cookie(SESSION_COOKIE_NAME)

    token = (
        decode_cookie(rendercv_session, resolve_secret()) if rendercv_session else None
    )
    user = repository.get_user_by_token(session, token) if token else None
    if user is not None and user.auth_provider is not None:
        repository.rotate_session_token(session, user, generate_session_token())


@router.delete("/me", status_code=204)
def delete_account(
    response: Response, session: SessionDep, account: CurrentAccount
) -> None:
    """Erase the signed-in account and everything it owns.

    Why it takes no confirmation parameter: the request itself is the
    confirmation. Asking the caller to repeat something back would only
    move the decision, and the interface already puts a dialog in front of
    it -- a second gate in the API would protect nobody while making the
    endpoint harder to call correctly.

    Why `CurrentAccount` rather than resolving the cookie by hand: this must
    refuse anonymous callers outright. `CurrentAccount` does that, and it
    also means a request with no valid session cannot reach the delete at
    all rather than deleting whatever row it happened to mint.

    The cookie is cleared as well. Leaving it would send the browser back
    with a token whose row no longer exists, which resolves to "signed
    out" -- correct, but by accident rather than on purpose.

    Args:
        response: The response to clear the session cookie on.
        session: The database session.
        account: The signed-in account, required.
    """
    response.delete_cookie(SESSION_COOKIE_NAME)
    repository.delete_user(session, account)
