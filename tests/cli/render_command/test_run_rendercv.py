import os
import pathlib
from unittest.mock import MagicMock

import pytest

from rendercv.cli.render_command.run_rendercv import (
    CompletedStep,
    RenderProgress,
    run_rendercv,
    run_rendercv_quietly,
    timed_step,
)
from rendercv.exception import RenderCVUserError


class TestRenderProgressBuildPanel:
    def test_empty_progress(self):
        progress = RenderProgress()
        panel = progress.build_panel()

        assert "Rendering..." in str(panel.renderable)

    def test_single_step_without_paths(self):
        progress = RenderProgress()
        progress.completed_steps.append(
            CompletedStep(timing_ms="100", message="Validated input", paths=[])
        )
        panel = progress.build_panel()

        renderable_str = str(panel.renderable)
        assert "100 ms" in renderable_str
        assert "Validated input" in renderable_str

    def test_single_step_with_one_path(self):
        progress = RenderProgress()
        test_path = pathlib.Path.cwd() / "output.pdf"
        progress.completed_steps.append(
            CompletedStep(timing_ms="250", message="Generated PDF", paths=[test_path])
        )
        panel = progress.build_panel()

        renderable_str = str(panel.renderable)
        assert "250 ms" in renderable_str
        assert "Generated PDF" in renderable_str
        assert "./output.pdf" in renderable_str

    def test_single_step_with_multiple_paths(self):
        progress = RenderProgress()
        path1 = pathlib.Path.cwd() / "page1.png"
        path2 = pathlib.Path.cwd() / "page2.png"
        progress.completed_steps.append(
            CompletedStep(
                timing_ms="500", message="Generated PNG", paths=[path1, path2]
            )
        )
        panel = progress.build_panel()

        renderable_str = str(panel.renderable)
        assert "500 ms" in renderable_str
        assert "Generated PNG" in renderable_str
        assert "./page1.png" in renderable_str
        assert "./page2.png" in renderable_str

    def test_multiple_steps(self):
        progress = RenderProgress()
        progress.completed_steps.extend(
            [
                CompletedStep(timing_ms="100", message="Step 1", paths=[]),
                CompletedStep(
                    timing_ms="200",
                    message="Step 2",
                    paths=[pathlib.Path.cwd() / "file.txt"],
                ),
                CompletedStep(timing_ms="300", message="Step 3", paths=[]),
            ]
        )
        panel = progress.build_panel()

        renderable_str = str(panel.renderable)
        assert "Step 1" in renderable_str
        assert "Step 2" in renderable_str
        assert "Step 3" in renderable_str

    def test_custom_title(self):
        progress = RenderProgress()
        panel = progress.build_panel(title="Custom Title")

        assert panel.title == "Custom Title"


class TestTimedStep:
    def test_returns_function_result(self):
        def sample_func(x: int) -> int:
            return x * 2

        progress = RenderProgress()
        live = MagicMock()

        result = timed_step("Test", progress, live, sample_func, 5)

        assert result == 10

    def test_updates_progress_with_timing(self):
        def sample_func():
            return None

        progress = RenderProgress()
        live = MagicMock()

        timed_step("Test message", progress, live, sample_func)

        assert len(progress.completed_steps) == 1
        assert progress.completed_steps[0].message == "Test message"
        assert progress.completed_steps[0].timing_ms.isdigit()

    def test_handles_single_path_result(self):
        def sample_func() -> pathlib.Path:
            return pathlib.Path.cwd() / "output.pdf"

        progress = RenderProgress()
        live = MagicMock()

        result = timed_step("Generated PDF", progress, live, sample_func)

        assert result == pathlib.Path.cwd() / "output.pdf"
        assert len(progress.completed_steps) == 1
        assert progress.completed_steps[0].paths == [pathlib.Path.cwd() / "output.pdf"]

    def test_handles_list_path_result(self):
        def sample_func() -> list[pathlib.Path]:
            return [pathlib.Path.cwd() / "page1.png", pathlib.Path.cwd() / "page2.png"]

        progress = RenderProgress()
        live = MagicMock()

        result = timed_step("Generated PNG", progress, live, sample_func)

        assert len(result) == 2
        assert len(progress.completed_steps) == 1
        assert progress.completed_steps[0].paths == [
            pathlib.Path.cwd() / "page1.png",
            pathlib.Path.cwd() / "page2.png",
        ]

    def test_pluralizes_message_for_multiple_paths(self):
        def sample_func() -> list[pathlib.Path]:
            return [pathlib.Path.cwd() / "page1.png", pathlib.Path.cwd() / "page2.png"]

        progress = RenderProgress()
        live = MagicMock()

        timed_step("Generated PNG", progress, live, sample_func)

        assert progress.completed_steps[0].message == "Generated PNGs"

    def test_passes_args_and_kwargs_to_function(self):
        def sample_func(a: int, b: int, c: int = 0) -> int:
            return a + b + c

        progress = RenderProgress()
        live = MagicMock()

        result = timed_step("Test", progress, live, sample_func, 1, 2, c=3)

        assert result == 6


class TestRunRendercvAndRunRendercvQuietly:
    @pytest.mark.parametrize("run_function", [run_rendercv, run_rendercv_quietly])
    def test_invalid_yaml(self, tmp_path, run_function):
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content: :")

        with pytest.raises(RenderCVUserError, match="not a valid YAML"):
            run_function(invalid_yaml)

    @pytest.mark.parametrize("run_function", [run_rendercv, run_rendercv_quietly])
    def test_invalid_input_file(self, tmp_path, run_function):
        invalid_schema = tmp_path / "invalid_schema.yaml"
        invalid_schema.write_text("cv:\n  name: 123")

        with pytest.raises(RenderCVUserError):
            run_function(invalid_schema)

    @pytest.mark.parametrize("run_function", [run_rendercv, run_rendercv_quietly])
    def test_template_syntax_error(self, tmp_path, run_function):
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

        with pytest.raises(RenderCVUserError, match="problem with the template"):
            run_function(yaml_file)
