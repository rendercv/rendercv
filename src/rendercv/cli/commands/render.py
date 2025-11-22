import contextlib
import pathlib
import sys
import time
from collections.abc import Callable
from typing import Annotated, Unpack

import jinja2
import pydantic
import ruamel.yaml
import typer
import watchdog.events
import watchdog.observers

from rendercv.exception import RenderCVCliUserError
from rendercv.renderer.html import render_html_to_file
from rendercv.renderer.markdown import render_markdown_to_file
from rendercv.renderer.pdf_png import render_pdf_to_file, render_png_to_file
from rendercv.renderer.typst import render_typst_to_file
from rendercv.schema.pydantic_error_handling import parse_validation_errors
from rendercv.schema.rendercv_model_builder import (
    BuildRendercvModelArguments,
    build_rendercv_dictionary_and_model,
)

from .. import printer
from ..app import app

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
            help=(
                "If provided, the Markdown file will not be generated. Disabling"
                " Markdown generation implicitly disables HTML."
            ),
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
    dont_generate_typst: Annotated[
        bool,
        typer.Option(
            "--dont-generate-typst",
            "-notyp",
            help=(
                "If provided, the Typst file will not be generated. Disabling Typst"
                " generation implicitly disables PDF and PNG."
            ),
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
    extra_data_model_override_arguments: typer.Context = None,  # pyright: ignore[reportArgumentType]
):
    if not quiet:
        printer.welcome()

    arguments: BuildRendercvModelArguments = {
        "design_file_path_or_contents": design,
        "locale_file_path_or_contents": locale,
        "settings_file_path_or_contents": settings,
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
        "overrides": parse_render_command_override_arguments(
            extra_data_model_override_arguments
        ),
    }
    input_file_path = pathlib.Path(input_file_name).absolute()

    def run_rendercv_wrapper():
        run_rendercv(input_file_path, quiet, **arguments)

    if watch:
        run_function_if_file_changes(input_file_path, run_rendercv_wrapper)
    else:
        run_rendercv_wrapper()


def parse_render_command_override_arguments(
    extra_arguments: typer.Context,
) -> dict[str, str]:
    """Parse extra arguments given to the `render` command as data model key and value
    pairs and return them as a dictionary.

    Args:
        extra_arguments: The extra arguments context.

    Returns:
        The key and value pairs.
    """
    key_and_values: dict[str, str] = {}

    # `extra_arguments.args` is a list of arbitrary arguments that haven't been
    # specified in `cli_render_command` function's definition. They are used to allow
    # users to edit their data model in CLI. The elements with even indexes in this list
    # are keys that start with double dashed, such as
    # `--cv.sections.education.0.institution`. The following elements are the
    # corresponding values of the key, such as `"Bogazici University"`. The for loop
    # below parses `ctx.args` accordingly.

    if len(extra_arguments.args) % 2 != 0:
        message = (
            "There is a problem with the extra arguments"
            f" ({','.join(extra_arguments.args)})! Each key should have a corresponding"
            " value."
        )
        printer.error(message)
        typer.Exit(code=1)

    for i in range(0, len(extra_arguments.args), 2):
        key = extra_arguments.args[i]
        value = extra_arguments.args[i + 1]
        if not key.startswith("--"):
            message = f"The key ({key}) should start with double dashes!"
            printer.error(message)
            typer.Exit(code=1)

        key = key.replace("--", "")

        key_and_values[key] = value

    return key_and_values


def timed_step[T, **P](
    message: str,
    quiet: bool,
    func: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    time_taken = f"{(end - start) * 1000:.0f}"
    if not quiet and result:
        path = None
        if isinstance(result, pathlib.Path):
            path = result.absolute()
        elif isinstance(result, list) and all(
            isinstance(item, pathlib.Path) for item in result
        ):
            message += "s"
            path = ", ".join([str(item.absolute()) for item in result])

        message_body = f"{message}" + (f": {path}" if path else ".")
        printer.information(f"{time_taken:>5} ms    {message_body}")
    return result


def run_rendercv(
    main_input_file_path_or_contents: pathlib.Path | str,
    quiet: bool = False,
    **kwargs: Unpack[BuildRendercvModelArguments],
):
    rendercv_dictionary_as_commented_map = None
    error = True
    try:
        rendercv_dictionary_as_commented_map, rendercv_model = timed_step(
            "Validated the input file",
            quiet,
            build_rendercv_dictionary_and_model,
            main_input_file_path_or_contents,
            **kwargs,
        )
        typst_path = timed_step(
            "Rendered Typst",
            quiet,
            render_typst_to_file,
            rendercv_model,
        )
        _ = timed_step(
            "Rendered PDF",
            quiet,
            render_pdf_to_file,
            rendercv_model,
            typst_path,
        )
        _ = timed_step(
            "Rendered PNG",
            quiet,
            render_png_to_file,
            rendercv_model,
            typst_path,
        )
        md_path = timed_step(
            "Rendered Markdown",
            quiet,
            render_markdown_to_file,
            rendercv_model,
        )
        _ = timed_step(
            "Rendered HTML",
            quiet,
            render_html_to_file,
            rendercv_model,
            md_path,
        )
        error = False
    except RenderCVCliUserError as e:
        printer.error(e.message)
    except ruamel.yaml.YAMLError as e:
        printer.error(f"This is not a valid YAML file!\n\n{e}")
    except jinja2.exceptions.TemplateSyntaxError as e:
        printer.error(
            f"There is a problem with the template ({e.filename}) at line"
            f" {e.lineno}!\n\n{e}"
        )
    except pydantic.ValidationError as e:
        assert rendercv_dictionary_as_commented_map is not None
        validation_errors = parse_validation_errors(
            e, rendercv_dictionary_as_commented_map
        )
        printer.print_validation_errors(validation_errors)
    finally:
        if error:
            typer.Exit(code=1)


def run_function_if_file_changes(file_path: pathlib.Path, function: Callable):
    """Watch the file located at `file_path` and call the `function` when the file is
    modified. The function should not take any arguments.

    Args:
        file_path (pathlib.Path): The path of the file to watch for.
        function (Callable): The function to be called on file modification.
    """
    # Run the function immediately for the first time
    function()

    path_to_watch = str(file_path.absolute())
    if sys.platform == "win32":
        # Windows does not support single file watching, so we watch the directory
        path_to_watch = str(file_path.parent.absolute())

    class EventHandler(watchdog.events.FileSystemEventHandler):
        def __init__(self, function: Callable):
            super().__init__()
            self.function = function

        def on_modified(self, event: watchdog.events.FileModifiedEvent) -> None:
            if event.src_path != str(file_path.absolute()):
                return

            with contextlib.suppress(Exception):
                # Exceptions in the watchdog event handler thread should not
                # crash the application. They are already handled by the
                # decorated function, but we add this defensive check to ensure
                # the watcher continues running even if an unexpected exception
                # occurs in a background thread.
                self.function()

    event_handler = EventHandler(function)

    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
