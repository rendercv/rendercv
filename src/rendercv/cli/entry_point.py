"""Entry point for the RenderCV CLI.

Why:
    Users might install RenderCV with `pip install rendercv` instead of
    `pip install rendercv[full]`. This module catches that case and shows a helpful
    error message instead of a confusing `ImportError`.
"""

import importlib
import sys


def entry_point() -> None:
    """Entry point for the RenderCV CLI."""
    try:
        cli_app = importlib.import_module("rendercv.cli.app").app
    except ModuleNotFoundError as error:
        if error.name not in {
            "typer",
            "click",
            "rich",
            "shellingham",
            "watchdog",
            "typst",
            "rendercv_fonts",
        }:
            raise
        error_message = (
            "Your RenderCV installation is missing packages needed to run this"
            " command. Install them with:\n\n"
            '    pip install "rendercv[full]"\n\n'
            "This includes the command-line tools, PDF renderer, and fonts.\n"
        )
        sys.stderr.write(error_message)
        raise SystemExit(1) from None

    cli_app()
