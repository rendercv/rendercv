import importlib
import json
import pathlib
import ssl
import threading
import time
import urllib.request
from typing import Annotated

import packaging.version
import typer
from rich import print

from rendercv import __version__

app = typer.Typer(
    rich_markup_mode="rich",
    # to make `rendercv --version` work:
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

_VERSION_CACHE_FILE = pathlib.Path.home() / ".cache" / "rendercv" / "version_check.json"
_VERSION_CACHE_TTL_SECONDS = 86400  # 24 hours


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


def warn_if_new_version_is_available() -> None:
    """Check PyPI for newer RenderCV version and display update notice.

    Why:
        Users should be notified of updates for bug fixes and features.
        Uses cached results with 24-hour TTL to avoid blocking network requests
        on every CLI invocation. Background thread refreshes cache when stale.
    """
    cached_latest = _read_version_cache()

    if cached_latest is not None:
        current = packaging.version.Version(__version__)
        if current < cached_latest:
            print(
                "\n[bold yellow]A new version of RenderCV is available! You are using"
                f" v{__version__}, and the latest version is v{cached_latest}.[/bold"
                " yellow]\n"
            )
    else:
        thread = threading.Thread(target=_fetch_and_cache_latest_version, daemon=True)
        thread.start()


def _read_version_cache() -> packaging.version.Version | None:
    """Read cached version if fresh (within TTL), else None."""
    try:
        if not _VERSION_CACHE_FILE.exists():
            return None

        cache_data = json.loads(_VERSION_CACHE_FILE.read_text(encoding="utf-8"))
        cached_time = cache_data.get("timestamp", 0)

        if time.time() - cached_time > _VERSION_CACHE_TTL_SECONDS:
            return None

        version_str = cache_data.get("latest_version")
        if version_str:
            return packaging.version.Version(version_str)
    except Exception:
        pass

    return None


def _fetch_and_cache_latest_version() -> None:
    """Fetch latest version from PyPI and update cache. Silently fails on error."""
    url = "https://pypi.org/pypi/rendercv/json"
    try:
        with urllib.request.urlopen(
            url, context=ssl._create_unverified_context(), timeout=5
        ) as response:
            data = response.read()
            encoding = response.info().get_content_charset("utf-8")
            json_data = json.loads(data.decode(encoding))
            version_string = json_data["info"]["version"]

        _VERSION_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        cache_data = {
            "latest_version": version_string,
            "timestamp": time.time(),
        }
        _VERSION_CACHE_FILE.write_text(json.dumps(cache_data), encoding="utf-8")
    except Exception:
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
