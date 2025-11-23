import importlib
import pathlib
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
    """RenderCV is a command-line tool for rendering CVs from YAML input files. For more information, see https://docs.rendercv.com."""
    printer.warn_if_new_version_is_available()

    if version_requested:
        printer.print(f"RenderCV v{__version__}")


# Auto import all commands so that they are registered with the app:
cli_folder_path = pathlib.Path(__file__).parent
for file in cli_folder_path.rglob("*_command.py"):
    # Enforce folder structure: ./name_command/name_command.py
    folder_name = file.parent.name  # e.g. "foo_command"
    py_file_name = file.stem  # e.g. "foo_command"

    if folder_name != py_file_name:
        message = (
            f"Package name {folder_name} does not match module name {py_file_name}"
        )
        raise ValueError(message)

    # Build full module path: <parent_pkg>.foo_command.foo_command
    full_module = f"{__package__}.{folder_name}.{py_file_name}"

    module = importlib.import_module(full_module)
