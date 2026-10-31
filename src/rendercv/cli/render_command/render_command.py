import pathlib
from typing import Annotated

import typer

from rendercv.schema.input_files import collect_input_file_paths
from rendercv.schema.rendercv_model_builder import (
    BuildRendercvModelArguments,
)

from ..app import app
from ..error_handler import handle_user_errors
from .parse_override_arguments import parse_override_arguments
from .progress_panel import ProgressPanel
from .run_rendercv import run_rendercv
from .watcher import run_function_if_files_change


@app.command(
    name="render",
    help=(
        "Render a YAML input file. Example: [yellow]rendercv render"
        " John_Doe_CV.yaml[/yellow]. Details: [cyan]rendercv render --help[/cyan]"
    ),
    # Allow extra arguments, which override values of the input file:
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
@handle_user_errors
def cli_command_render(
    input_file_name: Annotated[
        pathlib.Path, typer.Argument(help="The YAML input file.")
    ],
    output_folder: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--output-folder",
            "-o",
            help=(
                "Base output folder for all generated files. Replaces the default"
                " 'rendercv_output' folder. Relative to the current working directory."
            ),
        ),
    ] = None,
    design: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--design",
            "-d",
            help=(
                'The "design" field\'s YAML input file, relative to the current working'
                " directory."
            ),
        ),
    ] = None,
    locale: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--locale-catalog",
            "-lc",
            help=(
                'The "locale" field\'s YAML input file, relative to the current working'
                " directory."
            ),
        ),
    ] = None,
    settings: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--settings",
            "-s",
            help=(
                'The "settings" field\'s YAML input file, relative to the current'
                " working directory."
            ),
        ),
    ] = None,
    overlay: Annotated[
        list[pathlib.Path] | None,
        typer.Option(
            "--overlay",
            help=(
                "A YAML file merged over the input file, like a private file with the"
                " real `cv.email` of a public CV. Can be given more than once, merged"
                " in order. Relative to the current working directory."
            ),
        ),
    ] = None,
    typst_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--typst-path",
            "-typ",
            help=(
                "Save the generated Typst file to the specified path, relative to the"
                " current working directory."
            ),
        ),
    ] = None,
    pdf_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--pdf-path",
            "-pdf",
            help=(
                "Save the generated PDF file to the specified path, relative to the"
                " current working directory."
            ),
        ),
    ] = None,
    markdown_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--markdown-path",
            "-md",
            help=(
                "Save the generated Markdown file to the specified path, relative to"
                " the current working directory."
            ),
        ),
    ] = None,
    html_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--html-path",
            "-html",
            help=(
                "Save the generated HTML file to the specified path, relative to the"
                " current working directory."
            ),
        ),
    ] = None,
    png_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--png-path",
            "-png",
            help=(
                "Save the generated PNG files to the specified path, relative to the"
                " current working directory."
            ),
        ),
    ] = None,
    svg_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--svg-path",
            "-svg",
            help=(
                "Save the generated SVG files to the specified path, relative to the"
                " current working directory."
            ),
        ),
    ] = None,
    dont_generate_markdown: Annotated[
        bool | None,
        typer.Option(
            "--dont-generate-markdown",
            "-nomd",
            help=(
                "If provided, the Markdown file will not be generated. Disabling"
                " Markdown generation implicitly disables HTML."
            ),
        ),
    ] = None,
    dont_generate_html: Annotated[
        bool | None,
        typer.Option(
            "--dont-generate-html",
            "-nohtml",
            help="If provided, the HTML file will not be generated.",
        ),
    ] = None,
    dont_generate_typst: Annotated[
        bool | None,
        typer.Option(
            "--dont-generate-typst",
            "-notyp",
            help=(
                "Do not save the Typst source file. PDF, PNG, and SVG generation are"
                " unaffected."
            ),
        ),
    ] = None,
    dont_generate_pdf: Annotated[
        bool | None,
        typer.Option(
            "--dont-generate-pdf",
            "-nopdf",
            help="If provided, the PDF file will not be generated.",
        ),
    ] = None,
    dont_generate_png: Annotated[
        bool | None,
        typer.Option(
            "--dont-generate-png",
            "-nopng",
            help="If provided, the PNG file will not be generated.",
        ),
    ] = None,
    dont_generate_svg: Annotated[
        bool | None,
        typer.Option(
            "--dont-generate-svg",
            "-nosvg",
            help="If provided, the SVG files will not be generated.",
        ),
    ] = None,
    watch: Annotated[
        bool | None,
        typer.Option(
            "--watch",
            "-w",
            help=(
                "If provided, RenderCV will automatically re-run when the input file is"
                " updated."
            ),
        ),
    ] = None,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="If provided, RenderCV will not print any messages.",
        ),
    ] = False,
    # Dummy argument that only exists to show the override syntax in --help:
    yaml_field_override: Annotated[  # noqa: ARG001
        str | None,
        typer.Option(
            "--YAMLLOCATION",
            help="Overrides the value of YAMLLOCATION. For example,"
            ' [cyan bold]--cv.phone "123-456-7890"[/cyan bold].',
        ),
    ] = None,
    extra_data_model_override_arguments: typer.Context = None,  # ty: ignore[invalid-parameter-default]
) -> None:
    input_file_path = pathlib.Path(input_file_name).absolute()

    arguments: BuildRendercvModelArguments = {
        "output_folder": (
            output_folder.absolute() if output_folder is not None else None
        ),
        "typst_path": typst_path.absolute() if typst_path is not None else None,
        "pdf_path": pdf_path.absolute() if pdf_path is not None else None,
        "markdown_path": (
            markdown_path.absolute() if markdown_path is not None else None
        ),
        "html_path": html_path.absolute() if html_path is not None else None,
        "png_path": png_path.absolute() if png_path is not None else None,
        "svg_path": svg_path.absolute() if svg_path is not None else None,
        "dont_generate_typst": dont_generate_typst,
        "dont_generate_html": dont_generate_html,
        "dont_generate_markdown": dont_generate_markdown,
        "dont_generate_pdf": dont_generate_pdf,
        "dont_generate_png": dont_generate_png,
        "dont_generate_svg": dont_generate_svg,
        "overrides": parse_override_arguments(extra_data_model_override_arguments),
    }

    design = design.absolute() if design is not None else None
    locale = locale.absolute() if locale is not None else None
    settings = settings.absolute() if settings is not None else None
    overlays = [path.absolute() for path in overlay or []]

    with ProgressPanel(quiet=quiet) as progress_panel:

        def render() -> bool:
            return run_rendercv(
                input_file_path,
                progress_panel,
                design=design,
                locale=locale,
                settings=settings,
                overlays=overlays,
                **arguments,
            )

        if watch:
            run_function_if_files_change(
                lambda: (
                    collect_input_file_paths(
                        input_file_path, design, locale, settings, overlays
                    ).paths
                ),
                render,
            )
        elif not render():
            raise typer.Exit(code=1)
