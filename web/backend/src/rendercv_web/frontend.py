"""Serving the built frontend from the API process, on one origin.

Why the same process serves both:
    The session cookie is `SameSite=Lax`, so a browser withholds it from
    any `fetch` to a different site. A frontend hosted apart from the API
    would therefore sign in successfully and lose the session on its very
    next request, and no CORS configuration can change that -- CORS lets
    the request through, `SameSite` keeps the cookie back. Serving both
    from one origin removes the problem rather than working around it.

Why this is optional:
    In development the Vite dev server serves the frontend and proxies
    `/api` here, so there is no build directory to serve and `mount` does
    nothing. The same code therefore runs in both places without a flag
    saying which one it is in.
"""

import mimetypes
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, Response

FRONTEND_DIR_ENV_VAR = "RENDERCV_WEB_FRONTEND_DIR"

# Content-hashed by the build, so a stale copy is impossible: a changed file
# gets a changed name. Anything else in the build (the HTML entry points,
# `robots.txt`, the theme images) is revalidated normally.
IMMUTABLE_PREFIX = "_app/immutable/"
IMMUTABLE_CACHE_CONTROL = "public, max-age=31536000, immutable"

# `python:3.12-slim` carries no system MIME database, so `mimetypes` returns
# `None` for these and `FileResponse` falls back to
# `application/octet-stream`. Browsers usually sniff an `<img>` anyway, which
# is what makes this the kind of thing that ships unnoticed -- but a font
# served as a binary blob is refused outright by some configurations, and
# nothing in the response says why. Registering them costs nothing and makes
# the container behave like a developer's machine.
for _suffix, _media_type in (
    (".webp", "image/webp"),
    (".woff2", "font/woff2"),
    (".woff", "font/woff"),
    (".avif", "image/avif"),
):
    mimetypes.add_type(_media_type, _suffix)


def resolve_frontend_dir() -> Path | None:
    """Locate the built frontend, if this deployment has one.

    Returns:
        The build directory, or `None` when the variable is unset or points
        somewhere that does not exist -- which is the normal case in
        development, where Vite serves the frontend instead.
    """
    configured = os.environ.get(FRONTEND_DIR_ENV_VAR)
    if not configured:
        return None
    directory = Path(configured).resolve()
    return directory if (directory / "index.html").is_file() else None


def mount_frontend(app: FastAPI) -> bool:
    """Add the routes that serve the built frontend, if one is present.

    Must be called *after* every API router is registered. The catch-all
    below matches any path, so anything added after it would be shadowed.

    Args:
        app: The application to add the routes to.

    Returns:
        Whether a build was found and the routes were added.
    """
    build = resolve_frontend_dir()
    if build is None:
        return False

    index = build / "index.html"
    # Written by `adapter-static`'s `fallback` option for the routes that
    # are not prerendered -- `/app`, chiefly. Older builds that predate the
    # fallback being renamed away from `index.html` will not have it, in
    # which case the prerendered page stands in and the client router still
    # resolves the route; it is only worse for a crawler.
    fallback = build / "fallback.html"
    spa_entry = fallback if fallback.is_file() else index

    @app.get("/welcome", include_in_schema=False)
    def redirect_legacy_welcome() -> RedirectResponse:
        """Send the landing page's former address to its current one.

        Why the server does this rather than the client route that also
        handles it: a real 308 is what a bookmark, a shared link or a
        crawler deserves. The client-side redirect still exists for the
        dev server, where this route is not registered.

        Returns:
            A permanent redirect to the landing page.
        """
        return RedirectResponse("/", status_code=308)

    @app.get("/{resource_path:path}", include_in_schema=False)
    def serve_frontend(resource_path: str) -> Response:
        """Serve a built file, or the SPA entry point for a client route.

        Args:
            resource_path: The request path, without its leading slash.

        Returns:
            The requested file when the build contains it, the prerendered
            landing page for `/`, the prerendered HTML for a route that has
            some, and the SPA entry point for any other route the client
            router owns.

        Raises:
            HTTPException: 404 for an unmatched `/api/...` path. Without
                this the catch-all would answer a mistyped API call with
                the HTML shell and a 200, so a broken request would look
                like a working one to everything except a human reading
                the response body.
        """
        if resource_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")

        if not resource_path:
            return FileResponse(index)

        candidate = (build / resource_path).resolve()
        # `resolve()` collapses `..`, so this rejects any path that climbs
        # out of the build directory rather than trusting the URL.
        if candidate.is_relative_to(build) and candidate.is_file():
            headers = (
                {"Cache-Control": IMMUTABLE_CACHE_CONTROL}
                if resource_path.startswith(IMMUTABLE_PREFIX)
                else None
            )
            return FileResponse(candidate, headers=headers)

        # A prerendered route. `adapter-static` writes `/privacy` to
        # `privacy.html`, so the request path never names a file and the
        # lookup above misses it -- the route would fall through to the SPA
        # shell and the prerendering would buy nothing. A browser would
        # still render the page, which is what makes this quiet: the
        # readers who get the empty shell are the ones who do not run
        # JavaScript, and `/privacy` exists precisely for one of them,
        # Google's OAuth reviewer.
        #
        # Guarded like the lookup above: `resolve()` collapses `..`, so a
        # path climbing out of the build is refused here too.
        prerendered = (build / f"{resource_path}.html").resolve()
        if prerendered.is_relative_to(build) and prerendered.is_file():
            return FileResponse(prerendered)

        return FileResponse(spa_entry)

    return True
