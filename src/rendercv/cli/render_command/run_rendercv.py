import pathlib
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Unpack

import jinja2
import pydantic
import rich.live
import rich.panel
import ruamel.yaml
import typer

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


@dataclass
class CompletedStep:
    timing_ms: str
    message: str
    paths: list[pathlib.Path]


@dataclass
class RenderProgress:
    completed_steps: list[CompletedStep] = field(default_factory=list)

    def build_panel(self, title: str = "Rendering your CV...") -> rich.panel.Panel:
        lines: list[str] = []

        for step in self.completed_steps:
            paths_str = ""
            if step.paths:
                paths_as_strings = [
                    f"./{path.relative_to(pathlib.Path.cwd())}" for path in step.paths
                ]
                paths_str = "; ".join(paths_as_strings)

            timing = f"[bold green]{step.timing_ms + ' ms':<8}[/bold green]"
            message = step.message + (": " if paths_str else ".")
            paths_display = f"[purple]{paths_str}[/purple]" if paths_str else ""
            lines.append(f"[green]✓[/green] {timing} {message:<26} {paths_display}")

        content = "\n".join(lines) if lines else "Rendering..."

        return rich.panel.Panel(
            content,
            title=title,
            title_align="left",
            border_style="bright_black",
        )


def timed_step[T, **P](
    message: str,
    progress: RenderProgress,
    live: rich.live.Live,
    quiet: bool,
    func: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    timing_ms = f"{(end - start) * 1000:.0f}"

    if not quiet:
        paths: list[pathlib.Path] = []
        if isinstance(result, pathlib.Path):
            paths = [result]
        elif isinstance(result, list) and result:
            if len(result) > 1:
                message = f"{message}s"
            paths = result

        progress.completed_steps.append(CompletedStep(timing_ms, message, paths))
        live.update(progress.build_panel())

    return result


def run_rendercv(
    main_input_file_path_or_contents: pathlib.Path | str,
    quiet: bool = False,
    **kwargs: Unpack[BuildRendercvModelArguments],
):
    rendercv_dictionary_as_commented_map = None
    error = True
    progress = RenderProgress()

    try:
        with rich.live.Live(
            progress.build_panel(), refresh_per_second=4, console=printer.console
        ) as live:
            rendercv_dictionary_as_commented_map, rendercv_model = timed_step(
                "Validated the input file",
                progress,
                live,
                quiet,
                build_rendercv_dictionary_and_model,
                main_input_file_path_or_contents,
                **kwargs,
            )
            typst_path = timed_step(
                "Generated Typst",
                progress,
                live,
                quiet,
                generate_typst,
                rendercv_model,
            )
            _ = timed_step(
                "Generated PDF",
                progress,
                live,
                quiet,
                generate_pdf,
                rendercv_model,
                typst_path,
            )
            _ = timed_step(
                "Generated PNG",
                progress,
                live,
                quiet,
                generate_png,
                rendercv_model,
                typst_path,
            )
            md_path = timed_step(
                "Generated Markdown",
                progress,
                live,
                quiet,
                generate_markdown,
                rendercv_model,
            )
            _ = timed_step(
                "Generated HTML",
                progress,
                live,
                quiet,
                generate_html,
                rendercv_model,
                md_path,
            )
            if not quiet:
                live.update(progress.build_panel(title="Your CV is ready"))
        printer.print()
        error = False
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
