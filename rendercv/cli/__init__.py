"""
The `rendercv.cli` package contains the functions and classes that handle RenderCV's
command-line interface (CLI). It uses [Typer](https://typer.tiangolo.com/) to create the
CLI and [Rich](https://rich.readthedocs.io/en/latest/) to provide a nice-looking
interface.
"""

try:
    from .commands import (
        app,
        cli_command_create_theme,
        cli_command_new,
        cli_command_no_args,
        cli_command_render,
    )

    __all__ = [
        "app",
        "cli_command_create_theme",
        "cli_command_new",
        "cli_command_no_args",
        "cli_command_render",
    ]
except ImportError as e:
    from .. import _parial_install_error_message

    raise ImportError(_parial_install_error_message) from e
