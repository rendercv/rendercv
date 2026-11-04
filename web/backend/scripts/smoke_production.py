"""Check a running deployment's public surface, from outside it.

Why this exists:
    Two defects reached production with every test on both sides passing.
    A `typst` version that had drifted between the two lockfiles made the
    editor paginate a CV differently from `rendercv render`, and
    `schema.json` was missing from the container, so `GET /api/schema`
    answered 500 and the whole form mode was dead. Neither is visible from
    inside a test suite: one lives in the comparison between two
    environments, the other in what the image forgot to carry.

    So these checks talk to a deployment over HTTP and assert what a
    visitor would experience.

What it deliberately does not do:
    Sign in. Everything behind the session -- CVs, autosave, import,
    account deletion -- is checked by the e2e suite against a throwaway
    backend, and creating a Google session here would mean holding
    somebody's credentials. What this covers instead is the anonymous
    surface, including the part that must stay shut: those endpoints
    answering 401 is itself one of the assertions.

    It also uses a synthetic CV rather than anybody's real one, so it can
    run anywhere without carrying personal data.

Usage:
    uv run python scripts/smoke_production.py
    uv run python scripts/smoke_production.py --host http://localhost:8000
"""

import argparse
import io
import json
import urllib.error
import urllib.request
import zipfile

DEFAULT_HOST = "https://rendercv-web-uk68.onrender.com"

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ZIP_SIGNATURE = b"PK"

SHORT_CV = "cv:\n  name: Smoke Test\n  sections: {}\n"

# Long enough to need more than one page, built rather than pasted so it is
# obvious why it is long.
LONG_CV = "cv:\n  name: Smoke Test\n  sections:\n    experience:\n" + "".join(
    f"      - company: Company {index}\n"
    "        position: Engineer\n"
    "        start_date: 2020-01\n"
    "        end_date: 2021-01\n"
    "        highlights:\n"
    f"          - A line of text for entry {index}, long enough to wrap.\n"
    f"          - A second line for entry {index}, also long enough to wrap.\n"
    for index in range(40)
)


def documents(cv_yaml: str) -> dict[str, str]:
    """Build a render request body around one CV document.

    Args:
        cv_yaml: The `cv:` document.

    Returns:
        The four-document request body.
    """
    return {
        "cv_yaml": cv_yaml,
        "design_yaml": "",
        "locale_yaml": "",
        "settings_yaml": "",
    }


class Report:
    """Collects check results and prints them as they are decided."""

    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        """Record and print one result.

        Args:
            name: What was checked.
            ok: Whether it held.
            detail: Evidence worth printing beside it.
        """
        if ok:
            self.passed += 1
        else:
            self.failed += 1
        suffix = f"  ({detail})" if detail else ""
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def request(
    host: str, path: str, body: dict | None = None, method: str = "", timeout: int = 180
) -> tuple[int, bytes, dict[str, str]]:
    """Make one request and return its outcome instead of raising.

    Why failures are returned rather than raised: a 401 or a 404 is the
    expected answer for several of these checks, and an exception would
    make the ordinary case the awkward one.

    Args:
        host: Scheme and host to talk to.
        path: Path under the host.
        body: JSON body, or `None` for a request without one.
        method: HTTP method; inferred from `body` when empty.
        timeout: Seconds to wait.

    Returns:
        Status code, response body, and headers.
    """
    outgoing = urllib.request.Request(
        f"{host}{path}",
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers={"content-type": "application/json"} if body is not None else {},
        method=method or ("POST" if body is not None else "GET"),
    )
    try:
        with urllib.request.urlopen(outgoing, timeout=timeout) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers)
    except (urllib.error.URLError, TimeoutError) as error:
        return 0, str(error).encode("utf-8"), {}


def check_pages(host: str, report: Report) -> None:
    """The pages a visitor arrives at, and the documents they are owed.

    Args:
        host: Scheme and host to talk to.
        report: Where to record results.
    """
    status, body, _ = request(host, "/")
    landing = body.decode("utf-8", "replace")
    report.check(
        "landing page is prerendered HTML",
        status == 200 and "YAML-first" in landing,
        "readable without JavaScript",
    )
    report.check("landing links to the privacy policy", 'href="/privacy"' in landing)
    report.check("landing shows the theme images", landing.count("themes/") >= 5)

    status, body, _ = request(host, "/privacy")
    privacy = body.decode("utf-8", "replace")
    report.check(
        "privacy policy is served without JavaScript",
        status == 200 and "Privacy Policy" in privacy,
        "what Google's OAuth review fetches",
    )
    report.check("privacy names the deletion control", "Deleting your data" in privacy)
    report.check("privacy warns the database is disposable", "thirty days" in privacy)
    report.check("privacy carries a contact address", "mailto:" in privacy)

    status, body, _ = request(host, "/app")
    report.check(
        "the editor route serves the SPA shell",
        status == 200 and b"<html" in body.lower(),
    )


def check_public_api(host: str, report: Report) -> None:
    """The API a visitor can reach without an account.

    Args:
        host: Scheme and host to talk to.
        report: Where to record results.
    """
    status, body, _ = request(host, "/api/themes")
    themes = json.loads(body) if status == 200 else []
    report.check(
        "themes endpoint lists the built-ins",
        status == 200 and len(themes) == 9,
        f"{len(themes)} themes",
    )

    status, body, _ = request(host, "/api/auth/me")
    me = json.loads(body) if status == 200 else {}
    report.check(
        "sign-in is offered and nobody is signed in",
        me.get("provider_available") is True and me.get("authenticated") is False,
    )

    # The one that was answering 500: `schema.json` was absent from the
    # image, and the four form editors are generated from this response.
    status, body, _ = request(host, "/api/schema")
    report.check(
        "schema endpoint answers, so the form editors can be built",
        status == 200 and b'"$defs"' in body,
        f"{len(body)} bytes",
    )

    status, _, _ = request(host, "/api/validate", documents(SHORT_CV))
    report.check("validate accepts a good document", status == 200)

    status, body, _ = request(
        host,
        "/api/validate",
        documents("cv:\n  name: X\n  bogus_field: true\n  sections: {}\n"),
    )
    report.check(
        "validate rejects an unknown field",
        status == 422 and b"errors" in body,
        f"HTTP {status}",
    )

    status, body, _ = request(host, "/api/documents/parse", {"yaml": SHORT_CV})
    report.check(
        "parse turns YAML into a form model", status == 200 and b"data" in body
    )


def check_rendering(host: str, report: Report) -> None:
    """Rendering, in both formats and at both page counts.

    Args:
        host: Scheme and host to talk to.
        report: Where to record results.
    """
    status, body, headers = request(host, "/api/render", documents(SHORT_CV))
    report.check(
        "render returns a PDF",
        status == 200
        and body.startswith(b"%PDF-")
        and headers.get("Content-Type", "").startswith("application/pdf"),
        f"{len(body)} bytes",
    )

    status, body, headers = request(host, "/api/render/images", documents(SHORT_CV))
    report.check(
        "a one-page CV comes back as a bare PNG",
        status == 200
        and headers.get("Content-Type", "").startswith("image/png")
        and body.startswith(PNG_SIGNATURE),
        headers.get("Content-Type", ""),
    )

    status, body, headers = request(host, "/api/render/images", documents(LONG_CV))
    zipped = headers.get("Content-Type", "").startswith("application/zip")
    names: list[str] = []
    if zipped and body.startswith(ZIP_SIGNATURE):
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            names = archive.namelist()
    report.check(
        "a longer CV comes back as every page, zipped",
        status == 200 and zipped and len(names) > 1,
        f"{len(names)} pages",
    )


def check_what_must_stay_shut(host: str, report: Report) -> None:
    """The refusals, which are as much of the contract as the answers.

    Args:
        host: Scheme and host to talk to.
        report: Where to record results.
    """
    for path in ("/api/cvs", "/api/preferences"):
        status, _, _ = request(host, path)
        report.check(
            f"{path} refuses an anonymous caller", status == 401, f"HTTP {status}"
        )

    status, _, _ = request(host, "/api/auth/me", method="DELETE")
    report.check(
        "account deletion refuses an anonymous caller",
        status == 401,
        f"HTTP {status}",
    )

    # Without this the catch-all answers a mistyped endpoint with the HTML
    # shell and a 200, so a broken call looks like a working one.
    status, body, _ = request(host, "/api/does-not-exist")
    report.check(
        "an unknown API path is a 404, not the HTML shell",
        status == 404 and b"<html" not in body.lower(),
        f"HTTP {status}",
    )

    # Percent-encoded dots: the shape that reaches the handler intact.
    #
    # Several answers are safe and which one you get depends on the stack in
    # front: the application falls through to the SPA entry point (200),
    # while the proxy in front of this deployment rejects the path outright
    # (400). What must never happen is the file being served.
    #
    # The status is asserted at all because "the response does not contain a
    # secret" is trivially true of no response -- an earlier version of this
    # check passed against a host that was simply down.
    status, body, _ = request(host, "/%2e%2e/secrets.txt")
    report.check(
        "a path climbing out of the build is refused",
        status in (200, 400, 404)
        and b"-----BEGIN" not in body
        and b"do not serve me" not in body,
        f"HTTP {status}, and no file served",
    )


def check_assets(host: str, report: Report) -> None:
    """Static files, and the MIME types a slim image gets wrong by default.

    Args:
        host: Scheme and host to talk to.
        report: Where to record results.
    """
    status, body, _ = request(host, "/robots.txt")
    report.check("robots.txt is served", status == 200 and b"User-agent" in body)

    status, _, headers = request(host, "/themes/classic.webp")
    report.check(
        "theme images are labelled image/webp",
        status == 200 and headers.get("Content-Type", "").startswith("image/webp"),
        headers.get("Content-Type", "") or "no response",
    )


def main() -> None:
    """Run every check against the given host and exit non-zero on failure."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Scheme and host to check (default: {DEFAULT_HOST}).",
    )
    host = parser.parse_args().host.rstrip("/")

    print(f"\nChecking {host}\n")
    report = Report()
    check_pages(host, report)
    check_public_api(host, report)
    check_rendering(host, report)
    check_what_must_stay_shut(host, report)
    check_assets(host, report)

    total = report.passed + report.failed
    print(f"\n{report.passed}/{total} checks passed")
    if report.failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
