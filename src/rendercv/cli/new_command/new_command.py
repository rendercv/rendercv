import pathlib
from collections.abc import Callable
from typing import Annotated

import rich.panel
import typer
from rich import print

from rendercv.exception import RenderCVUserError
from rendercv.schema.models.design.built_in_design import (
    available_cover_themes,
    available_themes,
)
from rendercv.schema.models.locale.locale import available_locales
from rendercv.schema.sample_generator import create_sample_yaml_input_file

from ..app import app
from ..copy_templates import copy_templates
from ..error_handler import handle_user_errors
from .print_welcome import print_welcome


@app.command(
    name="new",
    help=(
        "Generate a YAML input file to get started. Example: [yellow]rendercv new"
        ' "John Doe"[/yellow]. Details: [cyan]rendercv new --help[/cyan]'
    ),
)
@handle_user_errors
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
    locale: Annotated[
        str,
        typer.Option(
            help=(
                "The name of the locale (available locales are:"
                f" {', '.join(available_locales)}). You can also continue with"
                " `English`, and then write your own `locale` field for your own"
                " language."
            )
        ),
    ] = "english",
    create_typst_templates: Annotated[
        bool,
        typer.Option(
            "--create-typst-templates",
            help="Create Typst templates",
        ),
    ] = False,
    create_markdown_templates: Annotated[
        bool,
        typer.Option(
            "--create-markdown-templates",
            help="Create Markdown templates",
        ),
    ] = False,
    cover: Annotated[
        bool,
        typer.Option("--cover", help="Cover letter"),
    ] = False,
):
    if theme not in available_themes:
        message = (
            f"Theme {theme} is not available. Available themes are:"
            f" {', '.join(available_themes)}"
        )
        raise RenderCVUserError(message)

    if locale not in available_locales:
        message = (
            f"Locale {locale} is not available. Available locales are:"
            f" {', '.join(available_locales)}"
        )
        raise RenderCVUserError(message)

    is_cover_theme = theme in available_cover_themes
    if cover and not is_cover_theme:
        message = (
            f"{theme} is not a valid cover theme. Available cover themes are:"
            f" {', '.join(available_cover_themes)}"
        )
        raise RenderCVUserError(message)
    if not cover and is_cover_theme:
        message = "--cover flag used for a CV theme. Please check if this is intended"
        raise RenderCVUserError(message)

    print_welcome()

    suffix = "Cover" if cover else "CV"
    input_file_path = pathlib.Path(f"{full_name.replace(' ', '_')}_{suffix}.yaml")
    typst_templates_folder = pathlib.Path(theme)
    markdown_folder = pathlib.Path("markdown")

    # Define all items to create: (description, path, creator, skip)
    items_to_create: list[tuple[str, pathlib.Path, Callable[[], object], bool]] = [
        (
            "Your YAML input file",
            input_file_path,
            lambda: create_sample_yaml_input_file(
                file_path=input_file_path,
                name=full_name,
                theme=theme,
                locale=locale,
                cover=cover,
            ),
            True,  # never skip the input file
        ),
        (
            "Typst templates",
            typst_templates_folder,
            lambda: copy_templates("typst", typst_templates_folder),
            create_typst_templates,
        ),
        (
            "Markdown templates",
            markdown_folder,
            lambda: copy_templates("markdown", markdown_folder),
            create_markdown_templates,
        ),
    ]

    # Process items
    created_items: list[tuple[str, pathlib.Path]] = []
    existing_items: list[tuple[str, pathlib.Path]] = []
    for description, path, creator, create in items_to_create:
        if not create:
            continue
        if path.exists():
            existing_items.append((description, path))
        else:
            creator()
            created_items.append((description, path))

    # Build the panel
    lines: list[str] = []

    # Input file status (always first)
    input_file_created = any(
        desc == "Your YAML input file" for desc, _ in created_items
    )
    if input_file_created:
        lines.append(
            "[green]✓[/green] Created your YAML input file: "
            f"[purple]./{input_file_path}[/purple]"
        )
    else:
        lines.append(
            f"Your YAML input file already exists: [purple]./{input_file_path}[/purple]"
        )

    # Next steps (always visible)
    lines.append("")
    lines.append("Next steps:")
    lines.append("  1. Edit the YAML input file with your information")
    lines.append(f"  2. Run: [cyan]rendercv render {input_file_path}[/cyan]")

    # Templates (exclude input file from these lists)
    created_templates = [
        (d, p) for d, p in created_items if d != "Your YAML input file"
    ]
    existing_templates = [
        (d, p) for d, p in existing_items if d != "Your YAML input file"
    ]

    if created_templates:
        lines.append("")
        lines.append("Also created:")
        for desc, path in created_templates:
            lines.append(f"  ○ {desc}: ./{path}")

    if existing_templates:
        lines.append("")
        lines.append("Not modified (already exist):")
        for desc, path in existing_templates:
            lines.append(f"  - {desc}: ./{path}")

    if created_templates or existing_templates:
        lines.append("")
        lines.append(
            "Templates are for advanced design customization. You can ignore or"
            " delete them."
        )

    print(
        rich.panel.Panel(
            "\n".join(lines),
            title="Get started",
            title_align="left",
            border_style="bright_black",
        )
    )
