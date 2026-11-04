"""Serving the built frontend from the API process.

These build their own `FastAPI` rather than importing the real `app`:
`mount_frontend` runs at import time there, against whatever the
environment said at that moment, so a test could not choose what it sees.
Constructing an app per case makes the build directory an input.
"""

import pathlib

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from rendercv_web.frontend import FRONTEND_DIR_ENV_VAR, mount_frontend

LANDING_HTML = "<html><body><h1>YAML-first resume builder</h1></body></html>"
FALLBACK_HTML = "<html><body><div id='spa'></div></body></html>"
PRIVACY_HTML = "<html><body><h1>Privacy Policy</h1></body></html>"


def build_frontend(directory: pathlib.Path, with_fallback: bool = True) -> None:
    """Write a miniature version of what `npm run build` produces.

    Args:
        directory: Where to write it.
        with_fallback: Whether to include the SPA entry point. Omitted to
            cover a build made before the fallback was renamed away from
            `index.html`.
    """
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "index.html").write_text(LANDING_HTML, encoding="utf-8")
    if with_fallback:
        (directory / "fallback.html").write_text(FALLBACK_HTML, encoding="utf-8")
    (directory / "robots.txt").write_text("User-agent: *\n", encoding="utf-8")
    # `adapter-static` names a prerendered `/privacy` this way -- as a
    # sibling file, not as `privacy/index.html`.
    (directory / "privacy.html").write_text(PRIVACY_HTML, encoding="utf-8")
    immutable = directory / "_app" / "immutable"
    immutable.mkdir(parents=True, exist_ok=True)
    (immutable / "entry.abc123.js").write_text("export default 1;\n", encoding="utf-8")
    themes = directory / "themes"
    themes.mkdir(parents=True, exist_ok=True)
    (themes / "classic.webp").write_bytes(b"RIFF\x00\x00\x00\x00WEBP")
    (immutable / "font.abc123.woff2").write_bytes(b"wOF2")


def make_app(directory: pathlib.Path | None, monkeypatch) -> FastAPI:
    """Build an app with one API route, then mount the frontend on it.

    Args:
        directory: The build to serve, or `None` to leave the variable unset.
        monkeypatch: pytest's monkeypatch fixture.

    Returns:
        The configured application.
    """
    if directory is None:
        monkeypatch.delenv(FRONTEND_DIR_ENV_VAR, raising=False)
    else:
        monkeypatch.setenv(FRONTEND_DIR_ENV_VAR, str(directory))

    app = FastAPI()
    router = APIRouter()

    @router.get("/api/themes")
    def read_themes() -> list[str]:
        return ["classic"]

    app.include_router(router)
    mount_frontend(app)
    return app


@pytest.fixture
def client(tmp_path, monkeypatch) -> TestClient:
    """A client against an app serving a miniature build."""
    build = tmp_path / "build"
    build_frontend(build)
    return TestClient(make_app(build, monkeypatch))


class TestWithoutABuild:
    """Development, where Vite serves the frontend and proxies here."""

    def test_mounting_is_skipped_when_the_variable_is_unset(
        self, tmp_path, monkeypatch
    ) -> None:
        del tmp_path
        app = make_app(None, monkeypatch)
        client = TestClient(app)

        # No catch-all, so an unknown path is a plain 404 rather than HTML.
        assert client.get("/app").status_code == 404
        assert client.get("/api/themes").status_code == 200

    def test_a_directory_without_an_index_is_not_served(
        self, tmp_path, monkeypatch
    ) -> None:
        # Pointing at a path that exists but holds no build is a
        # misconfiguration; answering every route with a 404 is far easier
        # to diagnose than answering them with an empty 200.
        empty = tmp_path / "not-a-build"
        empty.mkdir()

        client = TestClient(make_app(empty, monkeypatch))

        assert client.get("/").status_code == 404


class TestServingTheBuild:
    """A deployment where one process serves both halves."""

    def test_the_root_serves_the_prerendered_landing_page(
        self, client: TestClient
    ) -> None:
        response = client.get("/")

        assert response.status_code == 200
        # The prerendered HTML, not the empty shell -- the distinction the
        # `fallback.html` rename exists to preserve.
        assert "YAML-first resume builder" in response.text

    def test_a_client_route_serves_the_spa_entry_point(
        self, client: TestClient
    ) -> None:
        response = client.get("/app")

        assert response.status_code == 200
        assert "id='spa'" in response.text

    def test_a_prerendered_route_serves_its_own_html(self, client: TestClient) -> None:
        # `/privacy` names no file in the build -- the build calls it
        # `privacy.html` -- so without the suffix lookup this answers with
        # the SPA shell. A browser would still render the policy, which is
        # what would hide the fault: the readers who get the empty shell
        # are the ones who do not run JavaScript, and Google's OAuth
        # reviewer is one of them.
        response = client.get("/privacy")

        assert response.status_code == 200
        assert "Privacy Policy" in response.text
        assert "id='spa'" not in response.text

    def test_a_route_without_prerendered_html_still_gets_the_shell(
        self, client: TestClient
    ) -> None:
        # The suffix lookup must not change what happens to the routes that
        # are deliberately not prerendered. `/app` is the whole editor.
        response = client.get("/app")

        assert "id='spa'" in response.text

    def test_a_real_file_is_served_from_the_build(self, client: TestClient) -> None:
        response = client.get("/robots.txt")

        assert response.status_code == 200
        assert "User-agent" in response.text

    def test_hashed_assets_are_marked_immutable(self, client: TestClient) -> None:
        # These carry their content hash in the filename, so a stale copy
        # cannot happen and a year of caching is safe.
        response = client.get("/_app/immutable/entry.abc123.js")

        assert response.status_code == 200
        assert (
            response.headers["cache-control"] == "public, max-age=31536000, immutable"
        )

    def test_other_files_are_not_marked_immutable(self, client: TestClient) -> None:
        # `robots.txt` keeps its name across deploys, so freezing it for a
        # year would strand whatever it said on the day someone first read it.
        response = client.get("/robots.txt")

        assert "immutable" not in response.headers.get("cache-control", "")

    @pytest.mark.parametrize(
        ("path", "media_type"),
        [
            ("themes/classic.webp", "image/webp"),
            ("_app/immutable/font.abc123.woff2", "font/woff2"),
        ],
    )
    def test_modern_asset_types_are_labelled_correctly(
        self, client: TestClient, path: str, media_type: str
    ) -> None:
        # The runtime image has no system MIME database, so without the
        # registrations in `frontend` these come back as
        # `application/octet-stream`. A browser sniffs an image regardless,
        # which is why this hid; a font served that way can simply be
        # refused, with nothing in the response explaining it.
        response = client.get(f"/{path}")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith(media_type)

    def test_the_old_welcome_address_permanently_redirects(
        self, client: TestClient
    ) -> None:
        response = client.get("/welcome", follow_redirects=False)

        assert response.status_code == 308
        assert response.headers["location"] == "/"

    def test_a_build_without_a_fallback_still_serves_client_routes(
        self, tmp_path, monkeypatch
    ) -> None:
        build = tmp_path / "old-build"
        build_frontend(build, with_fallback=False)

        client = TestClient(make_app(build, monkeypatch))

        # Worse for a crawler -- it gets the landing page's HTML for /app --
        # but the client router still resolves the route, so the editor works.
        assert client.get("/app").status_code == 200


class TestWhatTheCatchAllMustNotSwallow:
    """The catch-all matches every path, which is the risk in it."""

    def test_a_real_api_route_still_wins(self, client: TestClient) -> None:
        response = client.get("/api/themes")

        assert response.status_code == 200
        assert response.json() == ["classic"]

    def test_an_unknown_api_path_is_a_404_not_html(self, client: TestClient) -> None:
        # The failure this guards against: a mistyped or renamed endpoint
        # answering with the HTML shell and a 200. Every caller would see a
        # success and then fail to parse it, and nothing in the status code
        # would point at the real problem.
        response = client.get("/api/does-not-exist")

        assert response.status_code == 404
        assert "<html" not in response.text.lower()

    @pytest.mark.parametrize(
        "path",
        [
            # Percent-encoded dots. The client and the router leave these
            # alone, so the handler really is asked for `../secrets.txt` --
            # this is the shape that reaches the guard, and the only one of
            # the three that fails when the guard is removed.
            "%2e%2e/secrets.txt",
            "%2e%2e%2fsecrets.txt",
            # Plain dots, normalised away before the handler ever runs.
            # Kept to record that they are handled, not to prove the guard.
            "_app/../../secrets.txt",
        ],
    )
    def test_paths_climbing_out_of_the_build_are_refused(
        self, client: TestClient, tmp_path, path: str
    ) -> None:
        # Planted one level above the build, exactly where a single `..`
        # lands, so an escape returns its contents rather than 404ing for
        # absence and passing the test for the wrong reason.
        (tmp_path / "secrets.txt").write_text("do not serve me", encoding="utf-8")
        # And again under the name the prerendered-route lookup would try,
        # which is a second way out of the build directory and needs its
        # own guard.
        (tmp_path / "secrets.txt.html").write_text("do not serve me", encoding="utf-8")

        response = client.get(f"/{path}")

        assert "do not serve me" not in response.text
        # Falling through to the SPA entry point is the intended answer: the
        # path is simply not part of the build.
        assert response.status_code == 200
