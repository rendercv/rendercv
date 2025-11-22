import pathlib
import time
from collections.abc import Callable
from typing import Unpack

import jinja2
import pydantic
import rich
import rich.live
import rich.panel
import ruamel.yaml
import typer

from rendercv.exception import RenderCVCliUserError
from rendercv.renderer.html import generate_html
from rendercv.renderer.markdown import generate_markdown
from rendercv.renderer.pdf_png import generate_pdf, generate_png
from rendercv.renderer.typst import generate_typst
from rendercv.schema.pydantic_error_handling import parse_validation_errors
from rendercv.schema.rendercv_model_builder import (
    BuildRendercvModelArguments,
    build_rendercv_dictionary_and_model,
)

from .. import printer
from .print_validation_errors import print_validation_errors


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
        paths: list[pathlib.Path] = []
        if isinstance(result, pathlib.Path):
            paths = [result]
        elif isinstance(result, list):
            paths = result
            assert all(isinstance(item, pathlib.Path) for item in paths)

        paths_as_strings = [
            f"{'./' + str(path.relative_to(pathlib.Path.cwd()))}" for path in paths
        ]
        path = "; ".join(paths_as_strings)

        message = message + (": " if path else ".")
        path = f"[purple]{path}[/purple]" if path else ""
        printer.print(
            rich.panel.Panel(
                f"[bold green]{time_taken + ' ms':<8}[/bold green] {message:<26}"
                f" {path}",
                title="Rendered",
                title_align="left",
                border_style="bright_black",
            )
        )
    return result


def run_rendercv(
    main_input_file_path_or_contents: pathlib.Path | str,
    quiet: bool = False,
    **kwargs: Unpack[BuildRendercvModelArguments],
):
    rendercv_dictionary_as_commented_map = None
    error = True
    try:
        panel = rich.panel.Panel(
            "Rendering...",
            title="Rendered",
            title_align="left",
            border_style="bright_black",
        )
        # Use Live context to enable updates
        with rich.live.Live(panel, refresh_per_second=4) as live:
            rendercv_dictionary_as_commented_map, rendercv_model = timed_step(
                "Validated the input file",
                quiet,
                build_rendercv_dictionary_and_model,
                main_input_file_path_or_contents,
                **kwargs,
            )
            typst_path = timed_step(
                "Generated Typst",
                quiet,
                generate_typst,
                rendercv_model,
            )
            _ = timed_step(
                "Generated PDF",
                quiet,
                generate_pdf,
                rendercv_model,
                typst_path,
            )
            _ = timed_step(
                "Generated PNG",
                quiet,
                generate_png,
                rendercv_model,
                typst_path,
            )
            md_path = timed_step(
                "Generated Markdown",
                quiet,
                generate_markdown,
                rendercv_model,
            )
            _ = timed_step(
                "Generated HTML",
                quiet,
                generate_html,
                rendercv_model,
                md_path,
            )
        printer.print()
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
        print_validation_errors(validation_errors)
    finally:
        if error:
            typer.Exit(code=1)
