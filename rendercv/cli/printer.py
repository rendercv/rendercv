"""
The `rendercv.cli.printer` module contains all the functions and classes that are used
to print nice-looking messages to the terminal.
"""

import functools
from collections.abc import Callable
from typing import Optional

import jinja2
import pydantic
import rich
import rich.live
import rich.panel
import rich.progress
import rich.table
import rich.text

try:
    import typer
except ImportError as e:
    from .. import _parial_install_error_message

    raise ImportError(_parial_install_error_message) from e

import packaging.version
from rich import print

from .. import __version__, data
from . import utilities


class LiveProgressReporter(rich.live.Live):
    """This class is a wrapper around `rich.live.Live` that provides the live progress
    reporting functionality.

    Args:
        number_of_steps: The number of steps to be finished.
        end_message: The message to be printed when the progress is finished. Defaults
            to "Your CV is rendered!".
    """

    def __init__(self, number_of_steps: int, end_message: str = "Your CV is rendered!"):
        class TimeElapsedColumn(rich.progress.ProgressColumn):
            def render(self, task: "rich.progress.Task") -> rich.text.Text:
                elapsed = task.finished_time if task.finished else task.elapsed
                assert elapsed is not None
                elapsed = elapsed * 1000  # Convert to milliseconds
                delta = f"{elapsed:.0f} ms"
                return rich.text.Text(str(delta), style="progress.elapsed")

        self.step_progress = rich.progress.Progress(
            TimeElapsedColumn(), rich.progress.TextColumn("{task.description}")
        )

        self.overall_progress = rich.progress.Progress(
            TimeElapsedColumn(),
            rich.progress.BarColumn(),
            rich.progress.TextColumn("{task.description}"),
        )

        self.group = rich.console.Group(
            rich.panel.Panel(rich.console.Group(self.step_progress)),
            self.overall_progress,
        )

        self.overall_task_id = self.overall_progress.add_task("", total=number_of_steps)
        self.number_of_steps = number_of_steps
        self.end_message = end_message
        self.current_step = 0
        self.overall_progress.update(
            self.overall_task_id,
            description=(
                f"[bold #AAAAAA]({self.current_step} out of"
                f" {self.number_of_steps} steps finished)"
            ),
        )
        super().__init__(self.group)

    def __enter__(self) -> "LiveProgressReporter":
        """Overwrite the `__enter__` method for the correct return type."""
        self.start(refresh=self._renderable is not None)
        return self

    def start_a_step(self, step_name: str):
        """Start a step and update the progress bars.

        Args:
            step_name: The name of the step.
        """
        self.current_step_name = step_name
        self.current_step_id = self.step_progress.add_task(
            f"{self.current_step_name} has started."
        )

    def finish_the_current_step(self):
        """Finish the current step and update the progress bars."""
        self.step_progress.stop_task(self.current_step_id)
        self.step_progress.update(
            self.current_step_id, description=f"{self.current_step_name} has finished."
        )
        self.current_step += 1
        self.overall_progress.update(
            self.overall_task_id,
            description=(
                f"[bold #AAAAAA]({self.current_step} out of"
                f" {self.number_of_steps} steps finished)"
            ),
            advance=1,
        )
        if self.current_step == self.number_of_steps:
            self.end()

    def end(self):
        """End the live progress reporting."""
        self.overall_progress.update(
            self.overall_task_id,
            description=f"[yellow]{self.end_message}",
        )


def warn_if_new_version_is_available() -> bool:
    """Check if a new version of RenderCV is available and print a warning message if
    there is a new version. Also, return True if there is a new version, and False
    otherwise.

    Returns:
        True if there is a new version, and False otherwise.
    """
    latest_version = utilities.get_latest_version_number_from_pypi()
    version = packaging.version.Version(__version__)
    if latest_version is not None and version < latest_version:
        warning(
            f"A new version of RenderCV is available! You are using v{__version__},"
            f" and the latest version is v{latest_version}."
        )
        return True
    return False


def welcome():
    """Print a welcome message to the terminal."""
    warn_if_new_version_is_available()

    table = rich.table.Table(
        title=(
            "\nWelcome to [bold]Render[dodger_blue3]CV[/dodger_blue3][/bold]! Some"
            " useful links:"
        ),
        title_justify="left",
    )

    table.add_column("Title", style="magenta", justify="left")
    table.add_column("Link", style="cyan", justify="right", no_wrap=True)

    table.add_row("[bold]RenderCV App", "https://rendercv.com")
    table.add_row("Documentation", "https://docs.rendercv.com")
    table.add_row("Source code", "https://github.com/rendercv/rendercv/")
    table.add_row("Bug reports", "https://github.com/rendercv/rendercv/issues/")
    table.add_row("Feature requests", "https://github.com/rendercv/rendercv/issues/")
    table.add_row("Discussions", "https://github.com/rendercv/rendercv/discussions/")
    table.add_row("RenderCV Pipeline", "https://github.com/rendercv/rendercv-pipeline/")

    print(table)


def warning(text: str):
    """Print a warning message to the terminal.

    Args:
        text: The text of the warning message.
    """
    print(f"[bold yellow]{text}")


def error(text: Optional[str] = None, exception: Optional[Exception] = None):
    """Print an error message to the terminal and exit the program. If an exception is
    given, then print the exception's message as well. If neither text nor exception is
    given, then print an empty line and exit the program.

    Args:
        text: The text of the error message.
        exception: An exception object. Defaults to None.
    """
    if exception is not None:
        exception_messages = [str(arg) for arg in exception.args]
        exception_message = "\n\n".join(exception_messages)
        if text is None:
            text = "An error occurred:"

        print(
            f"\n[bold red]{text}[/bold red]\n\n[orange4]{exception_message}[/orange4]\n"
        )
    elif text is not None:
        print(f"\n[bold red]{text}\n")
    else:
        print()


def information(text: str):
    """Print an information message to the terminal.

    Args:
        text: The text of the information message.
    """
    print(f"[green]{text}")


def print_validation_errors(exception: pydantic.ValidationError):
    """Take a Pydantic validation error and print the error messages in a nice table.

    Pydantic's `ValidationError` object is a complex object that contains a lot of
    information about the error. This function takes a `ValidationError` object and
    extracts the error messages, locations, and the input values. Then, it prints them
    in a nice table with [Rich](https://rich.readthedocs.io/en/latest/).

    Args:
        exception: The Pydantic validation error object.
    """
    errors = data.parse_validation_errors(exception)

    # Print the errors in a nice table:
    table = rich.table.Table(
        title="[bold red]\nThere are some errors in the data model!\n",
        title_justify="left",
        show_lines=True,
    )
    table.add_column("Location", style="cyan", no_wrap=True)
    table.add_column("Input Value", style="magenta")
    table.add_column("Error Message", style="orange4")

    for error_object in errors:
        table.add_row(
            ".".join(error_object["loc"]),
            error_object["input"],
            error_object["msg"],
        )

    print(table)


def handle_and_print_raised_exceptions_without_exit(function: Callable) -> Callable:
    """Return a wrapper function that handles exceptions. It does not exit the program
    after an exception is raised. It just prints the error message and continues the
    execution.

    A decorator in Python is a syntactic convenience that allows a Python to interpret
    the code below:

    ```python
    @handle_exceptions
    def my_function():
        pass
    ```

    as

    ```python
    my_function = handle_exceptions(my_function)
    ```

    which means that the function `my_function` is modified by the `handle_exceptions`.

    Args:
        function: The function to be wrapped.

    Returns:
        The wrapped function.
    """
    try:
        import ruamel.yaml
    except Exception as e:
        from .. import _parial_install_error_message

        raise ImportError(_parial_install_error_message) from e

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        code = 4
        try:
            function(*args, **kwargs)
        except pydantic.ValidationError as e:
            print_validation_errors(e)
        except ruamel.yaml.YAMLError as e:
            error(
                "There is a YAML error in the input file!\n\nTry to use quotation marks"
                " to make sure the YAML parser understands the field is a string.",
                e,
            )
        except FileNotFoundError as e:
            error(exception=e)
        except UnicodeDecodeError as e:
            # find the problematic character that cannot be decoded with utf-8
            bad_character = str(e.object[e.start : e.end])
            try:
                bad_character_context = str(e.object[e.start - 16 : e.end + 16])
            except IndexError:
                bad_character_context = ""

            error(
                "The input file contains a character that cannot be decoded with"
                f" UTF-8 ({bad_character}):\n {bad_character_context}",
            )
        except ValueError as e:
            error(exception=e)
        except typer.Exit:
            pass
        except jinja2.exceptions.TemplateSyntaxError as e:
            error(
                f"There is a problem with the template ({e.filename}) at line"
                f" {e.lineno}!",
                e,
            )
        except RuntimeError as e:
            error(exception=e)
        except Exception as e:
            raise e
        else:
            code = 0

        return code

    return wrapper


def handle_and_print_raised_exceptions(function: Callable) -> Callable:
    """Return a wrapper function that handles exceptions. It exits the program after an
    exception is raised.

    A decorator in Python is a syntactic convenience that allows a Python to interpret
    the code below:

    ```python
    @handle_exceptions
    def my_function():
        pass
    ```

    as

    ```python
    my_function = handle_exceptions(my_function)
    ```

    which means that the function `my_function` is modified by the `handle_exceptions`.

    Args:
        function: The function to be wrapped.

    Returns:
        The wrapped function.
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        without_exit_wrapper = handle_and_print_raised_exceptions_without_exit(function)

        code = without_exit_wrapper(*args, **kwargs)

        if code != 0:
            raise typer.Exit(code)

    return wrapper
