from typing import Annotated

import typer

from rendercv import __version__

from . import printer

app = typer.Typer(
    rich_markup_mode="rich",
    # to make `rendercv --version` work:
    invoke_without_command=True,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def cli_command_no_args(
    version_requested: Annotated[
        bool | None, typer.Option("--version", "-v", help="Show the version")
    ] = None,
):
    if version_requested:
        there_is_a_new_version = printer.warn_if_new_version_is_available()
        if not there_is_a_new_version:
            printer.print(f"RenderCV v{__version__}")
