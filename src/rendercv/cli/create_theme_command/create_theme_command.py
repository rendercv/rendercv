import pathlib
import textwrap
from typing import Annotated

import rich.panel
import typer
from rich import print

from rendercv.exception import RenderCVUserError

from ..app import app
from ..copy_templates import copy_templates
from .create_init_file_for_theme import create_init_file_for_theme


@app.command(
    name="create-theme",
    help=(
        "Create a custom theme folder with Typst templates to customize. Example:"
        " [yellow]rendercv create-theme customtheme[/yellow]. Details: [cyan]rendercv"
        " create-theme --help[/cyan]"
    ),
)
def cli_command_create_theme(
    theme_name: Annotated[
        str,
        typer.Argument(help="The name of the new theme"),
    ],
):
    new_theme_folder = pathlib.Path.cwd() / theme_name

    if new_theme_folder.exists():
        message = f'The theme folder "{theme_name}" already exists!'
        raise RenderCVUserError(message)

    copy_templates("typst", new_theme_folder)

    # Create the __init__.py file for the new theme:
    create_init_file_for_theme(theme_name, new_theme_folder / "__init__.py")

    # Build the panel
    message = textwrap.dedent(
        f"""
        [green]✓[/green] Created your custom theme: [purple]./{theme_name}[/purple]

        What you can do with this theme:
        1. Modify the Typst templates in [purple]./{theme_name}/
        2. Edit [purple]./{theme_name}/__init__.py[/purple] to:
            - Add your own design options to use in the YAML input file
            - Change the default values of existing options
            - Or simply delete it if you only want to customize templates

        To use your theme, set in your YAML input file:
        [cyan]  design:
        [cyan]    theme: {theme_name}
    """
    ).strip("\n")

    print(
        rich.panel.Panel(
            message,
            title="Theme created",
            title_align="left",
            border_style="bright_black",
        )
    )
