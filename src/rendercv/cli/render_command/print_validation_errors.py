import rich
import rich.box
import rich.table
from rich import print

from rendercv.exception import RenderCVInternalError, RenderCVValidationError


def print_validation_errors(errors: list[RenderCVValidationError]):
    if not errors:
        raise RenderCVInternalError("No validation errors provided")

    print("[bold red]\nThere are errors in the input file!\n")

    table = rich.table.Table(expand=True, show_lines=True, box=rich.box.ROUNDED)
    table.add_column("Location", style="cyan", no_wrap=True)
    table.add_column("Input Value", style="magenta", no_wrap=True)
    table.add_column("Explanation", style="orange4")

    for error_object in errors:
        table.add_row(
            ".".join(error_object["location"]),
            error_object["input"],
            error_object["message"],
        )

    print(table)
