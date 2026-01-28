import functools
from collections.abc import Callable

import rich.panel
import typer
from rich import print

from rendercv.exception import RenderCVUserError


def handle_user_errors[T, **P](function: Callable[P, None]) -> Callable[P, None]:
    """Decorator that catches user errors and displays friendly messages without stack traces.

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
        except RenderCVUserError as e:
            if e.message:
                print(
                    rich.panel.Panel(
                        e.message,
                        title="[bold red]Error[/bold red]",
                        title_align="left",
                        border_style="bold red",
                    )
                )
            raise typer.Exit(code=1) from e

    return wrapper
