import rich
import rich.table

from rendercv.schema.pydantic_error_handling import RenderCVValidationError

from .. import printer


def print_validation_errors(errors: list[RenderCVValidationError]):
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
            ".".join(error_object["location"]),
            error_object["input"],
            error_object["message"],
        )

    printer.print(table)
