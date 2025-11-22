import pathlib
from typing import Annotated

import typer

from rendercv.exception import RenderCVUserError
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.sample_generator import create_sample_yaml_input_file

from .. import printer
from ..app import app
from ..copy_templates import copy_templates


@app.command(
    name="new",
    help=(
        "Generate a YAML input file to get started. Example: [yellow]rendercv new"
        ' "John Doe"[/yellow]. Details: [cyan]rendercv new --help[/cyan]'
    ),
)
def cli_command_new(
    full_name: Annotated[str, typer.Argument(help="Your full name")],
    theme: Annotated[
        str,
        typer.Option(
            help=(
                "The name of the theme (available themes are:"
                f" {', '.join(available_themes)})"
            )
        ),
    ] = "classic",
    dont_create_theme_source_files: Annotated[
        bool,
        typer.Option(
            "--dont-create-theme-source-files",
            "-notypst",
            help="Don't create theme source files",
        ),
    ] = False,
    dont_create_markdown_source_files: Annotated[
        bool,
        typer.Option(
            "--dont-create-markdown-source-files",
            "-nomd",
            help="Don't create the Markdown source files",
        ),
    ] = False,
):
    created_files_and_folders = []

    input_file_name = f"{full_name.replace(' ', '_')}_CV.yaml"
    input_file_path = pathlib.Path(input_file_name)

    if input_file_path.exists():
        printer.warning(
            f'The input file "{input_file_name}" already exists! A new input file is'
            " not created"
        )
    else:
        try:
            create_sample_yaml_input_file(input_file_path, name=full_name, theme=theme)
            created_files_and_folders.append(input_file_path.name)
        except RenderCVUserError as e:
            printer.error(e.message)
            typer.Exit(code=1)

    if not dont_create_theme_source_files:
        # copy the package's theme files to the current directory
        theme_folder = copy_templates(theme, pathlib.Path.cwd())
        if theme_folder is not None:
            created_files_and_folders.append(theme_folder.name)
        else:
            printer.warning(
                f'The theme folder "{theme}" already exists! The theme files are not'
                " created"
            )

    if not dont_create_markdown_source_files:
        # copy the package's markdown files to the current directory
        markdown_folder = copy_templates("markdown", pathlib.Path.cwd())
        if markdown_folder is not None:
            created_files_and_folders.append(markdown_folder.name)
        else:
            printer.warning(
                'The "markdown" folder already exists! The Markdown files are not'
                " created"
            )

    if len(created_files_and_folders) > 0:
        created_files_and_folders_string = ",\n".join(created_files_and_folders)
        printer.print(
            "The following RenderCV input file and folders have been"
            f" created:\n{created_files_and_folders_string}"
        )
