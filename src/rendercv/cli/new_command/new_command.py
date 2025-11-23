import pathlib
from typing import Annotated

import typer

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
    dont_create_typst_templates: Annotated[
        bool,
        typer.Option(
            "--dont-create-typst-templates",
            "-notyp",
            help="Don't create Typst templates",
        ),
    ] = False,
    dont_create_markdown_templates: Annotated[
        bool,
        typer.Option(
            "--dont-create-markdown-templates",
            "-nomd",
            help="Don't create Markdown templates",
        ),
    ] = False,
):
    input_file_path = pathlib.Path(f"{full_name.replace(' ', '_')}_CV.yaml")
    typst_templates_folder = pathlib.Path(theme)
    markdown_folder = pathlib.Path("markdown")

    file_or_folder_creators = {
        input_file_path: lambda: create_sample_yaml_input_file(
            input_file_path, name=full_name, theme=theme
        ),
        typst_templates_folder: lambda: copy_templates("typst", typst_templates_folder),
        markdown_folder: lambda: copy_templates("markdown", markdown_folder),
    }

    created_files_and_folders = []
    for file_or_folder in [input_file_path, typst_templates_folder, markdown_folder]:
        if file_or_folder.exists():
            printer.warning(
                f"The {file_or_folder.name} already exists! A new {file_or_folder.name}"
                " is not created."
            )
        else:
            file_or_folder_creators[file_or_folder]()
            created_files_and_folders.append(file_or_folder)

    if len(created_files_and_folders) > 0:
        created_files_and_folders_string = ",\n".join(
            [file_or_folder.name for file_or_folder in created_files_and_folders]
        )
        printer.print(
            "The following RenderCV input file and folders have been"
            f" created:\n{created_files_and_folders_string}"
        )
