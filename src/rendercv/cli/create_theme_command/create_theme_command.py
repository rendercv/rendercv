import pathlib
from typing import Annotated

import rich.panel
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
            f" The provided value is `{theme_name}`."
        )
        return

    new_theme_folder = pathlib.Path.cwd() / theme_name

    if new_theme_folder.exists():
        printer.error(f'The theme folder "{theme_name}" already exists!')
        return

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

    # Build the panel
    lines: list[str] = [
        f"[green]✓[/green] Created your custom theme: [purple]./{theme_name}[/purple]",
        "",
        "What you can do with this theme:",
        f"  1. Modify the Typst templates in [purple]./{theme_name}/[/purple]",
        f"  2. Edit [purple]./{theme_name}/__init__.py[/purple] to:",
        "     - Add your own design options to use in the YAML input file",
        "     - Change the default values of existing options",
        "     - Or simply delete it if you only want to customize templates",
        "",
        "To use your theme, set in your YAML input file:",
        f"  [cyan]design:    theme: {theme_name}[/cyan]",
    ]

    printer.print(
        rich.panel.Panel(
            "\n".join(lines),
            title="Theme created",
            title_align="left",
            border_style="bright_black",
        )
    )
