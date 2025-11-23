import functools
from collections.abc import Callable

import typer

from rendercv.exception import RenderCVUserError

from . import printer


def handle_user_errors[T, **P](function: Callable[P, None]) -> Callable[P, None]:
    @functools.wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            return function(*args, **kwargs)
        except RenderCVUserError as e:
            printer.error(e.message)
            typer.Exit(code=1)

    return wrapper
