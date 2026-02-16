import os
import pathlib
import sys

import pytest
import typer

from rendercv.cli.render_command.progress_panel import ProgressPanel
from rendercv.cli.render_command.run_rendercv import (
    collect_input_file_paths,
    run_rendercv,
    timed_step,
)


class TestTimedStep:
    def test_returns_function_result(self):
        def sample_func(x: int) -> int:
            return x * 2

        progress = ProgressPanel(quiet=True)

        result = timed_step("Test", progress, sample_func, 5)

        assert result == 10

    def test_updates_progress_with_timing(self):
        def sample_func():
            return None

        progress = ProgressPanel(quiet=True)

        timed_step("Test message", progress, sample_func)

        assert len(progress.completed_steps) == 0

    def test_handles_single_path_result(self):
        def sample_func() -> pathlib.Path:
            return pathlib.Path.cwd() / "output.pdf"

        progress = ProgressPanel(quiet=True)

        result = timed_step("Generated PDF", progress, sample_func)

        assert result == pathlib.Path.cwd() / "output.pdf"
        assert len(progress.completed_steps) == 1
        assert progress.completed_steps[0].paths == [pathlib.Path.cwd() / "output.pdf"]

    def test_handles_list_path_result(self):
        def sample_func() -> list[pathlib.Path]:
            return [pathlib.Path.cwd() / "page1.png", pathlib.Path.cwd() / "page2.png"]

        progress = ProgressPanel(quiet=True)

        result = timed_step("Generated PNG", progress, sample_func)

        assert len(result) == 2
        assert len(progress.completed_steps) == 1
        assert progress.completed_steps[0].paths == [
            pathlib.Path.cwd() / "page1.png",
            pathlib.Path.cwd() / "page2.png",
        ]

    def test_pluralizes_message_for_multiple_paths(self):
        def sample_func() -> list[pathlib.Path]:
            return [pathlib.Path.cwd() / "page1.png", pathlib.Path.cwd() / "page2.png"]

        progress = ProgressPanel(quiet=True)

        timed_step("Generated PNG", progress, sample_func)

        assert progress.completed_steps[0].message == "Generated PNGs"

    def test_passes_args_and_kwargs_to_function(self):
        def sample_func(a: int, b: int, c: int = 0) -> int:
            return a + b + c

        progress = ProgressPanel(quiet=True)

        result = timed_step("Test", progress, sample_func, 1, 2, c=3)

        assert result == 6


class TestRunRendercv:
    def test_invalid_yaml(self, tmp_path):
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content: :", encoding="utf-8")

        progress = ProgressPanel(quiet=True)

        with pytest.raises(typer.Exit) as exc_info, progress:
            run_rendercv(invalid_yaml, progress)

        assert exc_info.value.exit_code == 1

    def test_invalid_input_file(self, tmp_path):
        invalid_schema = tmp_path / "invalid_schema.yaml"
        invalid_schema.write_text("cv:\n  name: 123", encoding="utf-8")

        progress = ProgressPanel(quiet=True)

        with pytest.raises(typer.Exit) as exc_info, progress:
            run_rendercv(invalid_schema, progress)

        assert exc_info.value.exit_code == 1

    def test_template_syntax_error(self, tmp_path):
        os.chdir(tmp_path)

        theme_folder = tmp_path / "badtheme"
        theme_folder.mkdir()

        template_file = theme_folder / "Header.j2.typ"
        template_file.write_text(
            "{% for item in items %}\n{{ item }\n", encoding="utf-8"
        )

        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(
            """cv:
    name: John Doe
design:
    theme: badtheme
""",
            encoding="utf-8",
        )

        progress = ProgressPanel(quiet=True)

        with pytest.raises(typer.Exit) as exc_info, progress:
            run_rendercv(yaml_file, progress)

        assert exc_info.value.exit_code == 1

    def test_user_error(self, tmp_path):
        yaml_file = tmp_path / "doesnt_exist.yaml"
        progress = ProgressPanel(quiet=True)
        with pytest.raises(typer.Exit) as _, progress:
            run_rendercv(yaml_file, progress)

    @pytest.mark.skipif(
        sys.platform == "win32", reason="chmod doesn't work the same on Windows"
    )
    def test_os_error_unreadable_file(self, tmp_path):
        """Test that OSError is properly caught when file is unreadable."""
        yaml_file = tmp_path / "unreadable.yaml"
        yaml_file.write_text("cv:\n  name: John Doe", encoding="utf-8")

        # Remove all permissions to make the file unreadable
        original_mode = yaml_file.stat().st_mode
        yaml_file.chmod(0o000)

        progress = ProgressPanel(quiet=True)

        try:
            with pytest.raises(typer.Exit) as exc_info, progress:
                run_rendercv(yaml_file, progress)

            assert exc_info.value.exit_code == 1
        finally:
            # Restore permissions for cleanup
            yaml_file.chmod(original_mode)


class TestCollectInputFilePaths:
    def test_returns_only_input_file_by_default(self, tmp_path):
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")

        result = collect_input_file_paths(yaml_file)

        assert result == {"input": yaml_file}

    def test_includes_cli_provided_files(self, tmp_path):
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")
        design_file = tmp_path / "design.yaml"
        design_file.touch()
        settings_file = tmp_path / "settings.yaml"
        settings_file.touch()

        result = collect_input_file_paths(
            yaml_file, design=design_file, settings=settings_file
        )

        assert result["input"] == yaml_file
        assert result["design"] == design_file
        assert result["settings"] == settings_file

    def test_includes_yaml_referenced_files(self, tmp_path):
        design_file = tmp_path / "my_design.yaml"
        design_file.touch()

        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text(
            "cv:\n  name: John Doe\n"
            "settings:\n  render_command:\n    design: my_design.yaml\n",
            encoding="utf-8",
        )

        result = collect_input_file_paths(yaml_file)

        assert result["input"] == yaml_file
        assert result["design"] == design_file.resolve()

    def test_cli_flags_take_precedence_over_yaml_references(self, tmp_path):
        yaml_ref_design = tmp_path / "yaml_design.yaml"
        yaml_ref_design.touch()
        cli_design = tmp_path / "cli_design.yaml"
        cli_design.touch()

        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text(
            "cv:\n  name: John Doe\n"
            "settings:\n  render_command:\n    design: yaml_design.yaml\n",
            encoding="utf-8",
        )

        result = collect_input_file_paths(yaml_file, design=cli_design)

        assert result["design"] == cli_design
