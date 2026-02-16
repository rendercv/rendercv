import pathlib
import shutil
import time
from collections.abc import Callable
from typing import Unpack

import jinja2
import ruamel.yaml

from rendercv.exception import RenderCVUserError, RenderCVUserValidationError
from rendercv.renderer.html import generate_html
from rendercv.renderer.markdown import generate_markdown
from rendercv.renderer.pdf_png import generate_pdf, generate_png
from rendercv.renderer.typst import generate_typst
from rendercv.schema.rendercv_model_builder import (
    BuildRendercvModelArguments,
    build_rendercv_dictionary_and_model,
)
from rendercv.schema.yaml_reader import read_yaml

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
    temp_typst_dir: pathlib.Path | None = None
    try:
        main_yaml = input_file_path.read_text(encoding="utf-8")

        # Resolve design/locale file references from the YAML itself
        # (CLI flags override YAML references)
        main_dict = read_yaml(main_yaml)
        rc = main_dict.get("settings", {}).get("render_command", {})

        if not kwargs.get("design_yaml_file") and rc.get("design"):
            design_path = (input_file_path.parent / rc["design"]).resolve()
            kwargs["design_yaml_file"] = design_path.read_text(encoding="utf-8")

        if not kwargs.get("locale_yaml_file") and rc.get("locale"):
            locale_path = (input_file_path.parent / rc["locale"]).resolve()
            kwargs["locale_yaml_file"] = locale_path.read_text(encoding="utf-8")

        _, rendercv_model = timed_step(
            "Validated the input file",
            progress,
            build_rendercv_dictionary_and_model,
            main_yaml,
            input_file_path=input_file_path,
            **kwargs,
        )
        typst_path, is_temp_typst = timed_step(
            "Generated Typst",
            progress,
            generate_typst,
            rendercv_model,
        )
        if is_temp_typst:
            temp_typst_dir = typst_path.parent
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
    except ruamel.yaml.YAMLError as e:
        progress.print_user_error(
            RenderCVUserError(message=f"This is not a valid YAML file!\n\n{e}")
        )
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
    finally:
        # Clean up temporary typst directory if it was created
        if temp_typst_dir is not None and temp_typst_dir.exists():
            shutil.rmtree(temp_typst_dir, ignore_errors=True)
