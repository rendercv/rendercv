import contextlib
import json
import ssl
import time
import urllib.request

import packaging.version
import rich
import rich.table
from rich import print

from rendercv import __version__
from rendercv.schema.pydantic_error_handling import RenderCVValidationError


def welcome():
    warn_if_new_version_is_available()

    table = rich.table.Table(
        title=(
            "\nWelcome to [bold]Render[dodger_blue3]CV[/dodger_blue3][/bold]! Some"
            " useful links:"
        ),
        title_justify="left",
    )

    table.add_column("Title", style="magenta", justify="left")
    table.add_column("Link", style="cyan", justify="right", no_wrap=True)

    table.add_row("RenderCV App", "https://rendercv.com")
    table.add_row("Documentation", "https://docs.rendercv.com")
    table.add_row("Source code", "https://github.com/rendercv/rendercv/")
    table.add_row("Bug reports", "https://github.com/rendercv/rendercv/issues/")
    table.add_row("Feature requests", "https://github.com/rendercv/rendercv/issues/")

    print(table)


def warn_if_new_version_is_available() -> None:
    """Check if a new version of RenderCV is available and print a warning message if
    there is a new version.
    """
    url = "https://pypi.org/pypi/rendercv/json"
    try:
        with urllib.request.urlopen(
            url, context=ssl._create_unverified_context()
        ) as response:
            data = response.read()
            encoding = response.info().get_content_charset("utf-8")
            json_data = json.loads(data.decode(encoding))
            version_string = json_data["info"]["version"]
            latest_version = packaging.version.Version(version_string)
    except Exception:
        latest_version = None

    if latest_version is None:
        version = packaging.version.Version(__version__)
        if latest_version is not None and version < latest_version:
            warning(
                f"A new version of RenderCV is available! You are using v{__version__},"
                f" and the latest version is v{latest_version}."
            )


def warning(text: str):
    print(f"[bold yellow]{text}")


def error(text: str):
    print(f"[bold red]{text}")


def information(text: str):
    print(f"[green]{text}")



def print_validation_errors(errors: list[RenderCVValidationError]):
    table = rich.table.Table(
        title="[bold red]\nThere are some errors in the data model!\n",
        title_justify="left",
        show_lines=True,
    )
    table.add_column("Location", style="cyan", no_wrap=True)
    table.add_column("Input Value", style="magenta")
    table.add_column("Error Message", style="orange4")

    for error_object in errors:
        table.add_row(
            ".".join(error_object["location"]),
            error_object["input"],
            error_object["message"],
        )

    print(table)
