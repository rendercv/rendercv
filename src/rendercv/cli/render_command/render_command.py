import pathlib
from typing import Annotated

import typer

from rendercv.schema.rendercv_model_builder import BuildRendercvModelArguments

from ..app import app
from ..error_handler import handle_user_errors
from .parse_override_arguments import parse_override_arguments
from .progress_panel import ProgressPanel
from .run_rendercv import run_rendercv
from .watcher import run_function_if_file_changes


@app.command(
    name="render",
    help=(
        "Render a YAML input file. Example: [yellow]rendercv render"
        " John_Doe_CV.yaml[/yellow]. Details: [cyan]rendercv render --help[/cyan]"
    ),
    # allow extra arguments for updating the old_data model (for overriding the values of
    # the input file):
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
@handle_user_errors
def cli_command_render(
    input_file_name: Annotated[
        pathlib.Path, typer.Argument(help="The YAML input file.")
    ],
    design: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--design",
            "-d",
            help='The "design" field\'s YAML input file.',
        ),
    ] = None,
    locale: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--locale-catalog",
            "-lc",
            help='The "locale" field\'s YAML input file.',
        ),
    ] = None,
    settings: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--settings",
            "-s",
            help='The "settings" field\'s YAML input file.',
        ),
    ] = None,
    typst_path: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--typst-path",
            "-typ",
            help=(
                "Save the generated Typst file to the specified path, relative to the"
                " input file."
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
                " input file."
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
                " the input file."
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
                " input file."
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
                " input file."
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
                "If provided, the Typst file will not be generated. Disabling Typst"
                " generation implicitly disables PDF and PNG."
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
    version: Annotated[
        str | None,
        typer.Option(
            "--version",
            "-V",
            help=(
                "Generate CV for a specific version defined in the YAML file. "
                "Only entries matching the version's tag filters will be included."
            ),
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
    # This is a dummy argument for the help message for
    # extra_data_model_override_argumets:
    _: Annotated[
        str | None,
        typer.Option(
            "--YAMLLOCATION",
            help="Overrides the value of YAMLLOCATION. For example,"
            ' [cyan bold]--cv.phone "123-456-7890"[/cyan bold].',
        ),
    ] = None,
    extra_data_model_override_arguments: typer.Context = None,  # ty: ignore[invalid-parameter-default]
):
    arguments: BuildRendercvModelArguments = {
        "design_file_path_or_contents": design if design else None,
        "locale_file_path_or_contents": locale if locale else None,
        "settings_file_path_or_contents": settings if settings else None,
        "typst_path": typst_path,
        "pdf_path": pdf_path,
        "markdown_path": markdown_path,
        "html_path": html_path,
        "png_path": png_path,
        "dont_generate_typst": dont_generate_typst,
        "dont_generate_html": dont_generate_html,
        "dont_generate_markdown": dont_generate_markdown,
        "dont_generate_pdf": dont_generate_pdf,
        "dont_generate_png": dont_generate_png,
        "overrides": parse_override_arguments(extra_data_model_override_arguments),
        "version": version,
    }
    input_file_path = pathlib.Path(input_file_name)

    with ProgressPanel(quiet=quiet) as progress_panel:
        if watch:
            run_function_if_file_changes(
                input_file_path,
                lambda: run_rendercv(input_file_path, progress_panel, **arguments),
            )
        else:
            run_rendercv(input_file_path, progress_panel, **arguments)
