import importlib
import json
import pathlib
import ssl
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
        Non-blocking check on startup ensures users stay informed without
        interrupting workflow if check fails.
    """
    url = "https://pypi.org/pypi/rendercv/json"
    try:
        with urllib.request.urlopen(
            url, context=ssl.create_default_context()
        ) as response:
            data = response.read()
            encoding = response.info().get_content_charset("utf-8")
            json_data = json.loads(data.decode(encoding))
            version_string = json_data["info"]["version"]
            latest_version = packaging.version.Version(version_string)
    except Exception:
        latest_version = None

    if latest_version is not None:
        version = packaging.version.Version(__version__)
        if version < latest_version:
            print(
                "\n[bold yellow]A new version of RenderCV is available! You are using"
                f" v{__version__}, and the latest version is v{latest_version}.[/bold"
                " yellow]\n"
            )


# Auto import all commands so that they are registered with the app:
cli_folder_path = pathlib.Path(__file__).parent
for file in cli_folder_path.rglob("*_command.py"):
    # Enforce folder structure: ./name_command/name_command.py
    folder_name = file.parent.name  # e.g. "foo_command"
    py_file_name = file.stem  # e.g. "foo_command"

    # Build full module path: <parent_pkg>.foo_command.foo_command
    full_module = f"{__package__}.{folder_name}.{py_file_name}"

    module = importlib.import_module(full_module)
