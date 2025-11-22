import pathlib
from typing import Annotated

import typer

from rendercv.schema.models.design.built_in_design import available_themes

from .. import printer
from ..app import app
from ..copy_templates import copy_templates


@app.command(
    name="create-theme",
    help=(
        "Create a custom theme folder based on an existing theme. Example:"
        " [yellow]rendercv create-theme customtheme[/yellow]. Details: [cyan]rendercv"
        " create-theme --help[/cyan]"
    ),
)
def cli_command_create_theme(
    theme_name: Annotated[
        str,
        typer.Argument(help="The name of the new theme"),
    ],
    based_on: Annotated[
        str,
        typer.Option(
            help=(
                "The name of the existing theme to base the new theme on (available"
                f" themes are: {', '.join(available_themes)})"
            )
        ),
    ] = "classic",
):
    """Create a custom theme based on an existing theme"""
    if based_on not in available_themes:
        printer.error(
            f'The theme "{based_on}" is not in the list of available themes:'
            f" {', '.join(available_themes)}"
        )

    theme_folder = copy_templates(
        based_on, pathlib.Path.cwd(), new_folder_name=theme_name
    )

    if theme_folder is None:
        printer.warning(
            f'The theme folder "{theme_name}" already exists! The theme files are not'
            " created"
        )
        return

    based_on_theme_directory = (
        pathlib.Path(__file__).parent.parent / "themes" / based_on
    )
    based_on_theme_init_file = based_on_theme_directory / "__init__.py"
    based_on_theme_init_file_contents = based_on_theme_init_file.read_text()

    # generate the new init file:
    class_name = f"{theme_name.capitalize()}ThemeOptions"
    literal_name = f'Literal["{theme_name}"]'
    new_init_file_contents = based_on_theme_init_file_contents.replace(
        f'Literal["{based_on}"]', literal_name
    ).replace(f"{based_on.capitalize()}ThemeOptions", class_name)

    # create the new __init__.py file:
    (theme_folder / "__init__.py").write_text(new_init_file_contents)

    printer.print(f'The theme folder "{theme_folder.name}" has been created.')
