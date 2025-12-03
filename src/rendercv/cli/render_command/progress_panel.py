import pathlib
from dataclasses import dataclass

import rich.box
import rich.live
import rich.panel
import rich.table
import typer

from rendercv.exception import RenderCVUserError, RenderCVValidationError


class ProgressPanel(rich.live.Live):
    def __init__(self, quiet: bool = False):
        self.quiet = quiet
        self.completed_steps: list[CompletedStep] = []
        super().__init__(
            rich.panel.Panel(
                "...",
                title="Rendering your CV...",
                title_align="left",
                border_style="bright_black",
            ),
            refresh_per_second=4,
        )

    def update_progress(
        self, time_took: str, message: str, paths: list[pathlib.Path]
    ) -> None:
        self.completed_steps.append(CompletedStep(time_took, message, paths))
        self.print_progress_panel(title="Rendering your CV...")

    def finish_progress(self) -> None:
        self.print_progress_panel(title="Your CV is ready")
        self.completed_steps.clear()

    def print_progress_panel(self, title: str) -> None:
        if self.quiet:
            return

        lines: list[str] = []
        for step in self.completed_steps:
            paths_str = ""
            if step.paths:
                paths_as_strings = [
                    f"./{path.relative_to(pathlib.Path.cwd())}" for path in step.paths
                ]
                paths_str = "; ".join(paths_as_strings)

            timing = f"[bold green]{step.timing_ms + ' ms':<8}[/bold green]"
            message = step.message + (": " if paths_str else ".")
            paths_display = f"[purple]{paths_str}[/purple]" if paths_str else ""
            lines.append(f"[green]✓[/green] {timing} {message:<26} {paths_display}")

        content = "\n".join(lines) if lines else "Rendering..."

        self.update(
            rich.panel.Panel(
                content,
                title=title,
                title_align="left",
                border_style="bright_black",
            )
        )

    def print_user_error(self, user_error: RenderCVUserError) -> None:
        self.clear()
        self.update(
            rich.panel.Panel(
                user_error.message or "An unknown error occurred.",
                title="[bold red]Error[/bold red]",
                title_align="left",
                border_style="bold red",
            )
        )
        raise typer.Exit(code=1)

    def print_validation_errors(self, errors: list[RenderCVValidationError]) -> None:
        self.completed_steps.clear()
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

        self.update(
            rich.panel.Panel(
                table,
                title="[bold red]There are errors in the input file![/bold red]",
                title_align="left",
                border_style="bold red",
            )
        )

        raise typer.Exit(code=1)

    def clear(self) -> None:
        self.completed_steps.clear()
        self.update("")


@dataclass
class CompletedStep:
    timing_ms: str
    message: str
    paths: list[pathlib.Path]
