import json
import os
import pathlib
import sys
from unittest.mock import patch

import pytest
import typst

from rendercv.cli.render_command.progress_panel import ProgressPanel
from rendercv.cli.render_command.run_rendercv import (
    run_rendercv,
    timed_step,
)
from rendercv.exception import RenderCVUserError
from rendercv.schema.input_files import InputFiles, collect_input_file_paths


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
    @pytest.mark.parametrize(
        "error", [typst.TypstError("broken", "broken"), RuntimeError("broken")]
    )
    def test_renderer_failures_propagate(self, tmp_path, error):
        source = tmp_path / "cv.yaml"
        source.write_text("cv:\n  name: Jane Doe\n", encoding="utf-8")
        progress = ProgressPanel(quiet=True)
        with (
            patch(
                "rendercv.cli.render_command.run_rendercv.render_full_template",
                side_effect=error,
            ),
            progress,
            pytest.raises(type(error)) as raised,
        ):
            run_rendercv(source, progress)
        assert raised.value is error

    def test_invalid_yaml(self, tmp_path):
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content: :", encoding="utf-8")

        progress = ProgressPanel(quiet=True)

        with progress:
            assert not run_rendercv(invalid_yaml, progress)

    def test_invalid_input_file(self, tmp_path):
        invalid_schema = tmp_path / "invalid_schema.yaml"
        invalid_schema.write_text("cv:\n  name: 123", encoding="utf-8")

        progress = ProgressPanel(quiet=True)

        with progress:
            assert not run_rendercv(invalid_schema, progress)

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

        with progress:
            assert not run_rendercv(yaml_file, progress)

    def test_user_error(self, tmp_path):
        yaml_file = tmp_path / "doesnt_exist.yaml"
        progress = ProgressPanel(quiet=True)
        with progress:
            assert not run_rendercv(yaml_file, progress)

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
            with progress:
                assert not run_rendercv(yaml_file, progress)

        finally:
            # Restore permissions for cleanup
            yaml_file.chmod(original_mode)

    def test_user_error_during_rendering(self, tmp_path):
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")
        progress = ProgressPanel(quiet=True)

        with (
            patch(
                "rendercv.cli.render_command.run_rendercv.load_rendercv_model",
                side_effect=RenderCVUserError(message="test error"),
            ),
            progress,
        ):
            assert not run_rendercv(yaml_file, progress)


class TestCollectInputFilePaths:
    def test_returns_only_input_file_by_default(self, tmp_path):
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")

        result = collect_input_file_paths(yaml_file)

        assert result == InputFiles(input=yaml_file)

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

        assert result.input == yaml_file
        assert result.design == design_file
        assert result.settings == settings_file

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

        assert result.input == yaml_file
        assert result.design == design_file.resolve()

    def test_invalid_yaml_still_returns_input_file(self, tmp_path):
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("invalid: yaml: content: :", encoding="utf-8")

        result = collect_input_file_paths(yaml_file)

        assert result == InputFiles(input=yaml_file)

    def test_includes_cli_provided_locale_file(self, tmp_path):
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text("cv:\n  name: John Doe\n", encoding="utf-8")
        locale_file = tmp_path / "locale.yaml"
        locale_file.touch()

        result = collect_input_file_paths(yaml_file, locale=locale_file)

        assert result.input == yaml_file
        assert result.locale == locale_file

    def test_includes_yaml_referenced_locale_file(self, tmp_path):
        locale_file = tmp_path / "my_locale.yaml"
        locale_file.touch()

        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text(
            "cv:\n  name: John Doe\n"
            "settings:\n  render_command:\n    locale: my_locale.yaml\n",
            encoding="utf-8",
        )

        result = collect_input_file_paths(yaml_file)

        assert result.input == yaml_file
        assert result.locale == locale_file.resolve()

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

        assert result.design == cli_design


@pytest.mark.parametrize("reference", [None, 123, []])
def test_invalid_or_null_overlay_reference_does_not_fall_back(tmp_path, reference):

    main = tmp_path / "cv.yaml"
    main.write_text(
        "cv: {}\nsettings:\n  render_command:\n    design: missing.yaml\n",
        encoding="utf-8",
    )
    overlay = tmp_path / "settings.yaml"
    overlay.write_text(
        json.dumps({"settings": {"render_command": {"design": reference}}}),
        encoding="utf-8",
    )
    assert collect_input_file_paths(main, settings=overlay).design is None


class TestCollectInputFilePathsOverlays:
    def test_merges_referenced_overlays_before_cli_overlays(self, tmp_path):
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text(
            "settings:\n  render_command:\n    overlays:\n      - publications.yaml\n",
            encoding="utf-8",
        )
        secrets = tmp_path / "secrets.yaml"

        result = collect_input_file_paths(yaml_file, overlays=[secrets])

        assert result.overlays == ((tmp_path / "publications.yaml").resolve(), secrets)
        assert result.paths == [yaml_file, *result.overlays]

    def test_takes_the_overlays_of_the_settings_file_first(self, tmp_path):
        yaml_file = tmp_path / "cv.yaml"
        yaml_file.write_text(
            "settings:\n  render_command:\n    overlays: [a.yaml]\n", encoding="utf-8"
        )
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text(
            "settings:\n  render_command:\n    overlays: [b.yaml]\n", encoding="utf-8"
        )

        result = collect_input_file_paths(yaml_file, settings=settings_file)

        assert result.overlays == ((tmp_path / "b.yaml").resolve(),)


def test_run_rendercv_merges_overlays(tmp_path):
    input_file = tmp_path / "cv.yaml"
    input_file.write_text(
        "cv:\n  name: Jane Doe\n  email: jane@example.com\n"
        "settings:\n  render_command:\n    dont_generate_pdf: true\n"
        "    dont_generate_png: true\n    dont_generate_html: true\n"
        "    dont_generate_typst: true\n",
        encoding="utf-8",
    )
    overlay = tmp_path / "secrets.yaml"
    overlay.write_text("cv:\n  email: jane@private.com\n", encoding="utf-8")

    with ProgressPanel(quiet=True) as progress:
        assert run_rendercv(input_file, progress, overlays=[overlay])

    markdown = (tmp_path / "rendercv_output" / "Jane_Doe_CV.md").read_text(
        encoding="utf-8"
    )
    assert "jane@private.com" in markdown
    assert "jane@example.com" not in markdown


def test_invalid_custom_typst_propagates_a_compiler_error(tmp_path):
    input_file = tmp_path / "cv.yaml"
    input_file.write_text("cv:\n  name: Jane Doe\n", encoding="utf-8")
    custom = tmp_path / "classic"
    custom.mkdir()
    (custom / "Preamble.j2.typ").write_text("#unknown-function()", encoding="utf-8")
    with (
        ProgressPanel(quiet=True) as progress,
        pytest.raises(typst.TypstError),
    ):
        run_rendercv(input_file, progress)


def test_run_rendercv_renders_typst_only_when_an_output_needs_it(tmp_path):
    input_file = tmp_path / "cv.yaml"
    input_file.write_text(
        "cv:\n  name: Jane Doe\n"
        "settings:\n  render_command:\n    dont_generate_pdf: true\n"
        "    dont_generate_png: true\n    dont_generate_svg: true\n"
        "    dont_generate_typst: true\n",
        encoding="utf-8",
    )
    # A broken Typst template doesn't matter to Markdown and HTML:
    (tmp_path / "classic").mkdir()
    (tmp_path / "classic" / "Preamble.j2.typ").write_text("{{", encoding="utf-8")

    with ProgressPanel(quiet=True) as progress:
        assert run_rendercv(input_file, progress)

    assert (tmp_path / "rendercv_output" / "Jane_Doe_CV.md").exists()
