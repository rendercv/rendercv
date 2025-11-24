import functools
from collections.abc import Callable

import typer
from rich import print

from rendercv.exception import RenderCVUserError


def handle_user_errors[T, **P](function: Callable[P, None]) -> Callable[P, None]:
    @functools.wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            return function(*args, **kwargs)
        except RenderCVUserError as e:
            print(f"[bold red]{e.message}[/bold red]")
            typer.Exit(code=1)

    return wrapper
