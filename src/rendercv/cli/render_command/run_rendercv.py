import pathlib
import time
from collections.abc import Callable, Sequence
from typing import Unpack

from rendercv.exception import (
    RenderCVUserError,
    RenderCVUserValidationError,
)
from rendercv.renderer.html import generate_html
from rendercv.renderer.markdown import generate_markdown
from rendercv.renderer.pdf_png import generate_pdf, generate_png, generate_svg
from rendercv.renderer.templater.templater import render_full_template
from rendercv.renderer.typst import generate_typst
from rendercv.schema.input_files import load_rendercv_model
from rendercv.schema.rendercv_model_builder import (
    BuildRendercvModelArguments,
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
        Each generation step (Typst, PDF, PNG, SVG) returns file paths. This wrapper
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
        paths = [p for p in result if isinstance(p, pathlib.Path)]

    if paths:
        progress_panel.update_progress(
            time_took=timing_ms, message=message, paths=paths
        )

    return result


def run_rendercv(
    input_file_path: pathlib.Path,
    progress: ProgressPanel,
    *,
    design: pathlib.Path | None = None,
    locale: pathlib.Path | None = None,
    settings: pathlib.Path | None = None,
    overlays: Sequence[pathlib.Path] = (),
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> bool:
    """Execute the CV generation pipeline with progress tracking and error handling.

    Args:
        input_file_path: Path to the main YAML input file.
        progress: Progress panel for output display.
        design: CLI design overlay path.
        locale: CLI locale overlay path.
        settings: CLI settings overlay path.
        overlays: CLI overlay paths.
        kwargs: Optional YAML overlay strings, output paths, and generation flags.

    Returns:
        Whether rendering succeeded. The caller owns process exit policy.
    """
    try:
        rendercv_model = timed_step(
            "Validated the input file",
            progress,
            load_rendercv_model,
            input_file_path,
            design=design,
            locale=locale,
            settings=settings,
            overlays=overlays,
            **kwargs,
        )
    except RenderCVUserError as error:
        progress.print_user_error(error)
        return False
    except OSError as error:
        progress.print_user_error(
            RenderCVUserError(message=f"Could not read input: {error}")
        )
        return False
    except RenderCVUserValidationError as error:
        progress.print_validation_errors(error.validation_errors)
        return False

    try:
        # Render the Typst source once for all the formats compiled from it:
        source = None
        if rendercv_model.settings.render_command.enabled_outputs & {
            "typst",
            "pdf",
            "png",
            "svg",
        }:
            source = render_full_template(rendercv_model, "typst")
        timed_step(
            "Generated Typst",
            progress,
            generate_typst,
            rendercv_model,
            source,
        )
        timed_step(
            "Generated PDF",
            progress,
            generate_pdf,
            rendercv_model,
            source,
        )
        timed_step(
            "Generated PNG",
            progress,
            generate_png,
            rendercv_model,
            source,
        )
        timed_step(
            "Generated SVG",
            progress,
            generate_svg,
            rendercv_model,
            source,
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
    except OSError as error:
        progress.print_user_error(RenderCVUserError(f"Could not write output: {error}"))
        return False
    progress.finish_progress()
    return True
