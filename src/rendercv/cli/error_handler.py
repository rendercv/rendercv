import functools
from collections.abc import Callable

import rich.console
import rich.panel
import rich.text
import typer

from rendercv.exception import RenderCVUserError


def error_panel(message: str) -> rich.panel.Panel:
    """Build the panel that shows an error to the user.

    Args:
        message: The error message.

    Returns:
        The panel.
    """
    return rich.panel.Panel(
        rich.text.Text(message),
        title="[bold red]Error[/bold red]",
        title_align="left",
        border_style="bold red",
    )


def handle_user_errors[**P](function: Callable[P, None]) -> Callable[P, None]:
    """Catch user errors and display friendly messages without stack traces.

    Why:
        CLI commands should show clean error messages for expected user errors
        (invalid YAML, missing files) while preserving stack traces for
        unexpected errors. This decorator wraps all command functions.

    Example:
        ```py
        @app.command()
        @handle_user_errors
        def my_command():
            # Any RenderCVUserError gets caught and displayed cleanly
            pass
        ```

    Args:
        function: CLI command function to wrap.

    Returns:
        Wrapped function with error handling.
    """

    @functools.wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            return function(*args, **kwargs)
        except (RenderCVUserError, OSError) as error:
            message = (
                error.message
                if isinstance(error, RenderCVUserError) and error.message
                else str(error)
            )
            # Typer passes the command's options, like `--quiet`, as keywords:
            console = rich.console.Console(quiet=bool(kwargs.get("quiet")))
            console.print(error_panel(message))
            raise typer.Exit(code=1) from error

    return wrapper
