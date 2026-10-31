import io
import pathlib

import pytest
import rich.console

from rendercv.cli.render_command.progress_panel import (
    CompletedStep,
    ProgressPanel,
    format_validation_error_location,
)
from rendercv.exception import RenderCVUserError, RenderCVValidationError


class TestFormatValidationErrorLocation:
    def test_returns_schema_location_when_available(self):
        error = RenderCVValidationError(
            schema_location=("cv", "email"),
            yaml_location=((2, 3), (2, 8)),
            yaml_source="main_yaml_file",
            input="x",
            message="m",
        )

        assert format_validation_error_location(error) == "cv.email"

    def test_returns_yaml_source_and_single_coordinate_when_schema_location_missing(
        self,
    ):
        error = RenderCVValidationError(
            schema_location=None,
            yaml_location=((3, 7), (3, 7)),
            yaml_source="design_yaml_file",
            input="x",
            message="m",
        )

        assert format_validation_error_location(error) == "design_yaml_file: line 3"

    def test_returns_yaml_source_and_range_when_schema_location_missing(self):
        error = RenderCVValidationError(
            schema_location=None,
            yaml_location=((3, 7), (4, 2)),
            yaml_source="main_yaml_file",
            input="x",
            message="m",
        )

        assert (
            format_validation_error_location(error)
            == "main_yaml_file: line 3 to line 4"
        )

    def test_returns_yaml_source_when_yaml_location_is_missing(self):
        error = RenderCVValidationError(
            schema_location=None,
            yaml_location=None,
            yaml_source="locale_yaml_file",
            input="x",
            message="m",
        )

        assert format_validation_error_location(error) == "locale_yaml_file"


class TestProgressPanelUpdateProgress:
    def test_adds_step_to_completed_steps(self):
        panel = ProgressPanel(quiet=True)
        test_path = pathlib.Path.cwd() / "output.pdf"

        panel.update_progress("100", "Generated PDF", [test_path])

        assert len(panel.completed_steps) == 1
        assert panel.completed_steps[0].timing_ms == "100"
        assert panel.completed_steps[0].message == "Generated PDF"
        assert panel.completed_steps[0].paths == [test_path]

    def test_handles_multiple_paths(self):
        panel = ProgressPanel(quiet=True)
        path1 = pathlib.Path.cwd() / "page1.png"
        path2 = pathlib.Path.cwd() / "page2.png"

        panel.update_progress("250", "Generated PNG", [path1, path2])

        assert len(panel.completed_steps) == 1
        assert panel.completed_steps[0].paths == [path1, path2]

    def test_handles_empty_paths(self):
        panel = ProgressPanel(quiet=True)

        panel.update_progress("50", "Validated input", [])

        assert len(panel.completed_steps) == 1
        assert panel.completed_steps[0].paths == []


class TestProgressPanelFinishProgress:
    def test_clears_completed_steps(self):
        panel = ProgressPanel(quiet=True)
        panel.completed_steps.append(
            CompletedStep("100", "Test", [pathlib.Path.cwd() / "test.pdf"])
        )

        panel.finish_progress()

        assert len(panel.completed_steps) == 0


class TestProgressPanelPrintProgressPanel:
    def test_quiet_mode_produces_no_output(self, capsys):
        with ProgressPanel(quiet=True) as panel:
            panel.update_progress("100", "Test", [])
            panel.finish_progress()

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_respects_quiet_mode(self):
        panel = ProgressPanel(quiet=True)
        panel.completed_steps.append(CompletedStep("100", "Test", []))

        panel.print_progress_panel("Test Title")

    def test_displays_step_without_paths(self):
        panel = ProgressPanel(quiet=True)
        panel.completed_steps.append(CompletedStep("100", "Validated input", []))

        # This should not raise an error
        panel.print_progress_panel("Rendering your CV...")

    def test_displays_step_with_single_path(self):
        panel = ProgressPanel(quiet=True)
        test_path = pathlib.Path.cwd() / "output.pdf"
        panel.completed_steps.append(CompletedStep("250", "Generated PDF", [test_path]))

        panel.print_progress_panel("Rendering your CV...")

    def test_displays_step_with_multiple_paths(self):
        panel = ProgressPanel(quiet=True)
        path1 = pathlib.Path.cwd() / "page1.png"
        path2 = pathlib.Path.cwd() / "page2.png"
        panel.completed_steps.append(
            CompletedStep("500", "Generated PNG", [path1, path2])
        )

        panel.print_progress_panel("Rendering your CV...")

    def test_displays_multiple_steps(self):
        panel = ProgressPanel(quiet=True)
        panel.completed_steps.extend(
            [
                CompletedStep("100", "Step 1", []),
                CompletedStep("200", "Step 2", [pathlib.Path.cwd() / "file.txt"]),
                CompletedStep("300", "Step 3", []),
            ]
        )

        panel.print_progress_panel("Rendering your CV...")

    def test_handles_empty_steps(self):
        panel = ProgressPanel(quiet=True)

        panel.print_progress_panel("Rendering your CV...")


class TestProgressPanelPrintUserError:
    def test_displays_without_exiting(self):
        panel = ProgressPanel(quiet=True)
        error = RenderCVUserError(message="Test error message")

        panel.print_user_error(error)

    def test_handles_error_without_message(self):
        panel = ProgressPanel(quiet=True)
        error = RenderCVUserError(message=None)

        panel.print_user_error(error)


class TestProgressPanelPrintValidationErrors:
    def test_displays_without_exiting(self):
        panel = ProgressPanel(quiet=True)
        errors: list[RenderCVValidationError] = [
            RenderCVValidationError(
                schema_location=("cv", "name"),
                yaml_location=((1, 1), (1, 1)),
                yaml_source="main_yaml_file",
                input="123",
                message="Invalid name",
            )
        ]

        panel.print_validation_errors(errors)

    def test_clears_completed_steps_before_displaying_errors(self):
        panel = ProgressPanel(quiet=True)
        panel.completed_steps.append(
            CompletedStep("100", "Test", [pathlib.Path.cwd() / "test.pdf"])
        )
        errors: list[RenderCVValidationError] = [
            RenderCVValidationError(
                schema_location=("cv", "name"),
                yaml_location=((1, 1), (1, 1)),
                yaml_source="main_yaml_file",
                input="123",
                message="Invalid name",
            )
        ]

        panel.print_validation_errors(errors)

        assert panel.completed_steps == []

    def test_handles_multiple_validation_errors(self):
        panel = ProgressPanel(quiet=True)
        errors: list[RenderCVValidationError] = [
            RenderCVValidationError(
                schema_location=("cv", "name"),
                yaml_location=((1, 1), (1, 1)),
                yaml_source="main_yaml_file",
                input="123",
                message="Invalid name",
            ),
            RenderCVValidationError(
                schema_location=("cv", "email"),
                yaml_location=((2, 1), (2, 1)),
                yaml_source="main_yaml_file",
                input="not-an-email",
                message="Invalid email format",
            ),
        ]

        panel.print_validation_errors(errors)

    def test_handles_yaml_parse_error_with_no_location(self):
        panel = ProgressPanel(quiet=True)
        errors: list[RenderCVValidationError] = [
            RenderCVValidationError(
                schema_location=None,
                yaml_location=((3, 7), (3, 7)),
                yaml_source="main_yaml_file",
                input="...",
                message="This is not a valid YAML file.",
            )
        ]

        panel.print_validation_errors(errors)


class TestProgressPanelClear:
    def test_clears_completed_steps(self):
        panel = ProgressPanel(quiet=True)
        panel.completed_steps.extend(
            [
                CompletedStep("100", "Step 1", []),
                CompletedStep("200", "Step 2", []),
            ]
        )

        panel.clear()

        assert len(panel.completed_steps) == 0


class TestCompletedStep:
    def test_creates_step_without_paths(self):
        step = CompletedStep("100", "Validated input", [])

        assert step.timing_ms == "100"
        assert step.message == "Validated input"
        assert step.paths == []

    def test_creates_step_with_paths(self):
        test_path = pathlib.Path.cwd() / "output.pdf"
        step = CompletedStep("250", "Generated PDF", [test_path])

        assert step.timing_ms == "250"
        assert step.message == "Generated PDF"
        assert step.paths == [test_path]


@pytest.mark.parametrize(
    "source", ["design_yaml_file", "locale_yaml_file", "settings_yaml_file"]
)
def test_validation_table_shows_overlay_source(source):
    error = RenderCVValidationError(("design", "theme"), None, source, "Invalid!", "x")
    assert format_validation_error_location(error) == f"{source}: design.theme"


def test_validation_table_renders_user_values_literally():
    panel = ProgressPanel(quiet=True)
    error = RenderCVValidationError(
        ("cv", "[red]interests[/red]"),
        None,
        "main_yaml_file",
        "Bad [/bold] value!",
        "[blue]x[/blue]",
    )
    panel.print_validation_errors([error])
    output = io.StringIO()
    console = rich.console.Console(file=output, width=240, color_system=None)
    console.print(panel.renderable)
    assert "[red]interests[/red]" in output.getvalue()
    assert "Bad [/bold] value!" in output.getvalue()
    assert "[blue]x[/blue]" in output.getvalue()


def test_root_error_has_a_nonempty_display_location():
    error = RenderCVValidationError(
        (), ((1, 1), (1, 1)), "main_yaml_file", "Bad root", "..."
    )
    assert format_validation_error_location(error) == "main_yaml_file: line 1"


def test_user_error_renders_diagnostics_literally():
    panel = ProgressPanel(quiet=True)
    message = "Invalid template: [/unknown] [red]source[/red]"
    panel.print_user_error(RenderCVUserError(message))
    output = io.StringIO()
    rich.console.Console(file=output, width=120, color_system=None).print(
        panel.renderable
    )
    assert message in output.getvalue()
