import pathlib
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

from .progress_panel import ProgressPanel


def timed_step[T, **P](
    message: str,
    progress_panel: ProgressPanel,
    func: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
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
        paths = result

    if paths:
        progress_panel.update_progress(
            time_took=timing_ms, message=message, paths=paths
        )

    return result


def run_rendercv(
    main_input_file_path_or_contents: pathlib.Path | str,
    progress: ProgressPanel,
    **kwargs: Unpack[BuildRendercvModelArguments],
):
    try:
        _, rendercv_model = timed_step(
            "Validated the input file",
            progress,
            build_rendercv_dictionary_and_model,
            main_input_file_path_or_contents,
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
    except RenderCVUserValidationError as e:
        progress.print_validation_errors(e.validation_errors)
