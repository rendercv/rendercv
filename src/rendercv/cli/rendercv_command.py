import pathlib
from typing import Annotated

import typer

from . import printer
from .app import app

help_message = (
    "Render a YAML input file. Example: [yellow]rendercv render"
    " John_Doe_CV.yaml[/yellow]. Details: [cyan]rendercv render --help[/cyan]"
)


@app.command(
    name="render",
    help=help_message,
    # allow extra arguments for updating the old_data model (for overriding the values of
    # the input file):
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def cli_command_render(
    input_file_name: Annotated[str, typer.Argument(help="The YAML input file.")],
    design: Annotated[
        str | None,
        typer.Option(
            "--design",
            "-d",
            help='The "design" field\'s YAML input file.',
        ),
    ] = None,
    locale: Annotated[
        str | None,
        typer.Option(
            "--locale-catalog",
            "-lc",
            help='The "locale" field\'s YAML input file.',
        ),
    ] = None,
    settings: Annotated[
        str | None,
        typer.Option(
            "--settings",
            "-s",
            help='The "settings" field\'s YAML input file.',
        ),
    ] = None,
    typst_path: Annotated[
        str | None,
        typer.Option(
            "--typst-path",
            "-typst",
            help="Path to the output Typst file, relative to the input YAML file.",
        ),
    ] = None,
    pdf_path: Annotated[
        str | None,
        typer.Option(
            "--pdf-path",
            "-pdf",
            help="Path to the output PDF file, relative to the input YAML file.",
        ),
    ] = None,
    markdown_path: Annotated[
        str | None,
        typer.Option(
            "--markdown-path",
            "-md",
            help="Path to the output Markdown file, relative to the input YAML file.",
        ),
    ] = None,
    html_path: Annotated[
        str | None,
        typer.Option(
            "--html-path",
            "-html",
            help="Path to the output HTML file, relative to the input YAML file.",
        ),
    ] = None,
    png_path: Annotated[
        str | None,
        typer.Option(
            "--png-path",
            "-png",
            help="Path to the output PNG file, relative to the input YAML file.",
        ),
    ] = None,
    dont_generate_markdown: Annotated[
        bool,
        typer.Option(
            "--dont-generate-markdown",
            "-nomd",
            help="If provided, the Markdown file will not be generated.",
        ),
    ] = False,
    dont_generate_html: Annotated[
        bool,
        typer.Option(
            "--dont-generate-html",
            "-nohtml",
            help="If provided, the HTML file will not be generated.",
        ),
    ] = False,
    dont_generate_pdf: Annotated[
        bool,
        typer.Option(
            "--dont-generate-pdf",
            "-nopdf",
            help="If provided, the PDF file will not be generated.",
        ),
    ] = False,
    dont_generate_png: Annotated[
        bool,
        typer.Option(
            "--dont-generate-png",
            "-nopng",
            help="If provided, the PNG file will not be generated.",
        ),
    ] = False,
    watch: Annotated[
        bool,
        typer.Option(
            "--watch",
            "-w",
            help=(
                "If provided, RenderCV will automatically re-run when the input file is"
                " updated."
            ),
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
    extra_data_model_override_arguments: typer.Context = None,  # pyright: ignore[reportArgumentType]
):
    """Render a CV from a YAML input file."""
    printer.welcome()

    # from . import utilities as u  # removed redundant alias import
    cli_render_arguments = {name: variables[name] for name in argument_names}

    input_file_as_a_dict = utilities.read_and_construct_the_input(
        input_file_path, cli_render_arguments, extra_data_model_override_arguments
    )

    watch = input_file_as_a_dict["rendercv_settings"]["render_command"]["watch"]

    if watch:

        @printer.handle_and_print_raised_exceptions_without_exit
        def run_rendercv():
            input_file_as_a_dict = (
                utilities.update_render_command_settings_of_the_input_file(
                    old_data.read_a_yaml_file(input_file_path), cli_render_arguments
                )
            )
            utilities.run_rendercv_with_printer(
                input_file_as_a_dict, original_working_directory, input_file_path
            )

        utilities.run_a_function_if_a_file_changes(input_file_path, run_rendercv)
    else:
        utilities.run_rendercv_with_printer(
            input_file_as_a_dict, original_working_directory, input_file_path
        )
