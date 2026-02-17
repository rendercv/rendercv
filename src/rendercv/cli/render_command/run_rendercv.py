import contextlib
import pathlib
import time
from collections.abc import Callable
from typing import Literal, Unpack

import jinja2

from rendercv.exception import RenderCVUserError, RenderCVUserValidationError
from rendercv.renderer.html import generate_html
from rendercv.renderer.markdown import generate_markdown
from rendercv.renderer.pdf_png import generate_pdf, generate_png
from rendercv.renderer.typst import generate_typst
from rendercv.schema.rendercv_model_builder import (
    BuildRendercvModelArguments,
    build_rendercv_dictionary_and_model,
    read_yaml_with_validation_errors,
)

from .progress_panel import ProgressPanel


def timed_step[T, **P](
    message: str,
    progress_panel: ProgressPanel,
    func: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    """Execute function, measure timing, and update progress panel with result.

    Why:
        Each generation step (Typst, PDF, PNG) returns file paths. This wrapper
        times execution and automatically displays results in progress panel.

    Example:
        ```py
        pdf_path = timed_step(
            "Generated PDF", progress, generate_pdf, rendercv_model, typst_path
        )
        # Progress shows: ✓ 150 ms  Generated PDF: ./cv.pdf
        ```

    Args:
        message: Step description for progress display.
        progress_panel: Progress panel to update.
        func: Function to execute and time.
        args: Positional arguments for func.
        kwargs: Keyword arguments for func.

    Returns:
        Function result.
    """
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    timing_ms = f"{(end - start) * 1000:.0f}"

    paths: list[pathlib.Path] = []
    if isinstance(result, pathlib.Path):
        paths = [result]
    elif isinstance(result, list) and result:
        if len(result) > 1:
            message = f"{message}s"
        paths = result  # ty: ignore[invalid-assignment]

    if paths:
        progress_panel.update_progress(
            time_took=timing_ms, message=message, paths=paths
        )

    return result


def collect_input_file_paths(
    input_file_path: pathlib.Path,
    design: pathlib.Path | None = None,
    locale: pathlib.Path | None = None,
    settings: pathlib.Path | None = None,
) -> dict[Literal["input", "design", "locale", "settings"], pathlib.Path]:
    """Collect all input file paths involved in a render.

    Why:
        A render may involve multiple files: the main YAML, plus overlay
        files for design/locale/settings provided via CLI flags or referenced
        in settings.render_command. Watch mode needs this complete list to
        monitor all of them for changes, and the render pipeline needs the
        resolved paths to read overlay file contents.

    Args:
        input_file_path: Path to the main YAML input file.
        design: CLI-provided design file path.
        locale: CLI-provided locale file path.
        settings: CLI-provided settings file path.

    Returns:
        Mapping from role ("input", "design", "locale", "settings") to path.
    """
    files: dict[Literal["input", "design", "locale", "settings"], pathlib.Path] = {
        "input": input_file_path
    }

    if design:
        files["design"] = design
    if locale:
        files["locale"] = locale
    if settings:
        files["settings"] = settings

    # Also include design/locale files referenced in the YAML itself
    # (CLI flags take precedence, so skip if already provided).
    # If YAML is invalid, watch mode should still start by watching the main file.
    with contextlib.suppress(RenderCVUserValidationError):
        main_dict = read_yaml_with_validation_errors(
            input_file_path.read_text(encoding="utf-8"),
            "main_yaml_file",
        )
        rc = main_dict.get("settings", {}).get("render_command", {})
        if "design" not in files and rc.get("design"):
            files["design"] = (input_file_path.parent / rc["design"]).resolve()
        if "locale" not in files and rc.get("locale"):
            files["locale"] = (input_file_path.parent / rc["locale"]).resolve()

    return files


def run_rendercv(
    input_file_path: pathlib.Path,
    progress: ProgressPanel,
    **kwargs: Unpack[BuildRendercvModelArguments],
):
    """Execute complete CV generation pipeline with progress tracking and error handling.

    Args:
        input_file_path: Path to the main YAML input file.
        progress: Progress panel for output display.
        kwargs: Optional YAML overlay strings, output paths, and generation flags.
    """
    try:
        main_yaml = input_file_path.read_text(encoding="utf-8")

        _, rendercv_model = timed_step(
            "Validated the input file",
            progress,
            build_rendercv_dictionary_and_model,
            main_yaml,
            input_file_path=input_file_path,
            **kwargs,
        )
        typst_path = timed_step(
            "Generated Typst",
            progress,
            generate_typst,
            rendercv_model,
        )
        timed_step(
            "Generated PDF",
            progress,
            generate_pdf,
            rendercv_model,
            typst_path,
        )
        timed_step(
            "Generated PNG",
            progress,
            generate_png,
            rendercv_model,
            typst_path,
        )
        md_path = timed_step(
            "Generated Markdown",
            progress,
            generate_markdown,
            rendercv_model,
        )
        timed_step(
            "Generated HTML",
            progress,
            generate_html,
            rendercv_model,
            md_path,
        )
        progress.finish_progress()
    except RenderCVUserError as e:
        progress.print_user_error(e)
    except jinja2.exceptions.TemplateSyntaxError as e:
        progress.print_user_error(
            RenderCVUserError(
                message=(
                    f"There is a problem with the template ({e.filename}) at line"
                    f" {e.lineno}!\n\n{e}"
                )
            )
        )
    except OSError as e:
        progress.print_user_error(RenderCVUserError(message=f"OS Error: {e}"))
    except RenderCVUserValidationError as e:
        progress.print_validation_errors(e.validation_errors)
