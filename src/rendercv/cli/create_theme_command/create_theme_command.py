import pathlib
from typing import Annotated

import typer

from rendercv.schema.models.design.design import custom_theme_name_pattern

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
):
    if not custom_theme_name_pattern.match(theme_name):
        printer.error(
            "The custom theme name should only contain lowercase letters and digits."
            " The provided value is `{theme_name}`."
        )
        return

    new_theme_folder = pathlib.Path.cwd() / theme_name

    if new_theme_folder.exists():
        printer.error(f'The theme folder "{theme_name}" already exists!')

    copy_templates("typst", new_theme_folder)

    # generate the new init file:
    classic_theme_file = (
        pathlib.Path(__file__).parent.parent.parent
        / "schema"
        / "models"
        / "design"
        / "classic_theme.py"
    )
    new_init_file_contents = classic_theme_file.read_text()

    new_init_file_contents = new_init_file_contents.replace(
        "class ClassicTheme(BaseModelWithoutExtraKeys):",
        f"class {theme_name.capitalize()}Theme(BaseModelWithoutExtraKeys):",
    )
    new_init_file_contents = new_init_file_contents.replace(
        'theme: Literal["classic"] = "classic"',
        f'theme: Literal["{theme_name}"] = "{theme_name}"',
    )
    (new_theme_folder / "__init__.py").write_text(new_init_file_contents)

    printer.print(f'The theme folder "{new_theme_folder.name}" has been created.')
