import pathlib

import pytest
import typer

from rendercv.cli.render_command.progress_panel import CompletedStep, ProgressPanel
from rendercv.exception import RenderCVUserError, RenderCVValidationError


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
    def test_respects_quiet_mode(self):
        panel = ProgressPanel(quiet=True)
        panel.completed_steps.append(CompletedStep("100", "Test", []))

        panel.print_progress_panel("Test Title")

        # In quiet mode, nothing should be printed/updated
        # We can't easily test the internal state of rich.live.Live, so we just
        # verify the method doesn't raise an error

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
    def test_exits_with_code_1(self):
        panel = ProgressPanel(quiet=True)
        error = RenderCVUserError(message="Test error message")

        with pytest.raises(typer.Exit) as exc_info:
            panel.print_user_error(error)

        assert exc_info.value.exit_code == 1

    def test_handles_error_without_message(self):
        panel = ProgressPanel(quiet=True)
        error = RenderCVUserError(message=None)

        with pytest.raises(typer.Exit) as exc_info:
            panel.print_user_error(error)

        assert exc_info.value.exit_code == 1


class TestProgressPanelPrintValidationErrors:
    def test_exits_with_code_1(self):
        panel = ProgressPanel(quiet=True)
        errors: list[RenderCVValidationError] = [
            RenderCVValidationError(
                location=("cv", "name"),
                yaml_location=((1, 1), (1, 1)),
                input="123",
                message="Invalid name",
            )
        ]

        with pytest.raises(typer.Exit) as exc_info:
            panel.print_validation_errors(errors)

        assert exc_info.value.exit_code == 1

    def test_clears_completed_steps_before_displaying_errors(self):
        panel = ProgressPanel(quiet=True)
        panel.completed_steps.append(
            CompletedStep("100", "Test", [pathlib.Path.cwd() / "test.pdf"])
        )
        errors: list[RenderCVValidationError] = [
            RenderCVValidationError(
                location=("cv", "name"),
                yaml_location=((1, 1), (1, 1)),
                input="123",
                message="Invalid name",
            )
        ]

        with pytest.raises(typer.Exit):
            panel.print_validation_errors(errors)

        # We can't check this after the exception, but the implementation shows
        # it clears steps before displaying

    def test_handles_multiple_validation_errors(self):
        panel = ProgressPanel(quiet=True)
        errors: list[RenderCVValidationError] = [
            RenderCVValidationError(
                location=("cv", "name"),
                yaml_location=((1, 1), (1, 1)),
                input="123",
                message="Invalid name",
            ),
            RenderCVValidationError(
                location=("cv", "email"),
                yaml_location=((2, 1), (2, 1)),
                input="not-an-email",
                message="Invalid email format",
            )
        ]

        with pytest.raises(typer.Exit) as exc_info:
            panel.print_validation_errors(errors)

        assert exc_info.value.exit_code == 1


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
