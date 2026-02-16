import importlib
import json
import os
import pathlib
import ssl
import sys
import threading
import time
import urllib.request
from typing import Annotated

import packaging.version
import typer
from rich import print

from rendercv import __version__

VERSION_CHECK_TTL_SECONDS = 86400  # 24 hours

app = typer.Typer(
    rich_markup_mode="rich",
    # to make `rendercv --version` work:
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def cli_command_no_args(
    ctx: typer.Context,
    version_requested: Annotated[
        bool | None, typer.Option("--version", "-v", help="Show the version")
    ] = None,
):
    """RenderCV is a command-line tool for rendering CVs from YAML input files. For more
    information, see https://docs.rendercv.com.
    """
    warn_if_new_version_is_available()

    if version_requested:
        print(f"RenderCV v{__version__}")
    elif ctx.invoked_subcommand is None:
        # No command was provided, show help
        print(ctx.get_help())
        raise typer.Exit()


def get_cache_dir() -> pathlib.Path:
    """Return the platform-appropriate cache directory for RenderCV."""
    if sys.platform == "win32":
        base = pathlib.Path(
            os.environ.get("LOCALAPPDATA", pathlib.Path.home() / "AppData" / "Local")
        )
    elif sys.platform == "darwin":
        base = pathlib.Path.home() / "Library" / "Caches"
    else:
        base = pathlib.Path(
            os.environ.get("XDG_CACHE_HOME", pathlib.Path.home() / ".cache")
        )
    return base / "rendercv"


def get_version_cache_file() -> pathlib.Path:
    """Return the path to the version check cache file."""
    return get_cache_dir() / "version_check.json"


def read_version_cache() -> dict | None:
    """Read the cached version check data, or None if unavailable/corrupt."""
    try:
        data = json.loads(get_version_cache_file().read_text(encoding="utf-8"))
        if isinstance(data, dict) and "last_check" in data and "latest_version" in data:
            return data
    except (OSError, json.JSONDecodeError, KeyError):
        pass
    return None


def write_version_cache(version_string: str) -> None:
    """Write the latest version string and current timestamp to the cache file."""
    cache_file = get_version_cache_file()
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(
            json.dumps({"last_check": time.time(), "latest_version": version_string}),
            encoding="utf-8",
        )
    except OSError:
        pass


def fetch_latest_version_from_pypi() -> str | None:
    """Fetch the latest RenderCV version string from PyPI, or None on failure."""
    url = "https://pypi.org/pypi/rendercv/json"
    try:
        with urllib.request.urlopen(
            url, context=ssl._create_unverified_context(), timeout=5
        ) as response:
            data = response.read()
            encoding = response.info().get_content_charset("utf-8")
            json_data = json.loads(data.decode(encoding))
            return json_data["info"]["version"]
    except Exception:
        return None


def fetch_and_cache_latest_version() -> None:
    """Fetch the latest version from PyPI and write it to the cache file."""
    version_string = fetch_latest_version_from_pypi()
    if version_string:
        write_version_cache(version_string)


def warn_if_new_version_is_available() -> None:
    """Check for a newer RenderCV version using a stale-while-revalidate cache.

    Why:
        Uses a disk cache with background refresh so the CLI never blocks on
        network I/O. If the cache is stale or missing, a daemon thread refreshes
        it for the next invocation.
    """
    cache = read_version_cache()

    if not cache or (time.time() - cache["last_check"]) >= VERSION_CHECK_TTL_SECONDS:
        thread = threading.Thread(target=fetch_and_cache_latest_version, daemon=True)
        thread.start()

    if cache:
        try:
            latest = packaging.version.Version(cache["latest_version"])
            current = packaging.version.Version(__version__)
            if current < latest:
                print(
                    "\n[bold yellow]A new version of RenderCV is available!"
                    f" You are using v{__version__}, and the latest version"
                    f" is v{latest}.[/bold yellow]\n"
                )
        except packaging.version.InvalidVersion:
            pass


# Auto import all commands so that they are registered with the app:
cli_folder_path = pathlib.Path(__file__).parent
for file in cli_folder_path.rglob("*_command.py"):
    # Enforce folder structure: ./name_command/name_command.py
    folder_name = file.parent.name  # e.g. "foo_command"
    py_file_name = file.stem  # e.g. "foo_command"

    # Build full module path: <parent_pkg>.foo_command.foo_command
    full_module = f"{__package__}.{folder_name}.{py_file_name}"

    module = importlib.import_module(full_module)
