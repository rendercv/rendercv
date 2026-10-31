import os
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from rendercv.cli.app import app
from rendercv.cli.new_command.new_command import cli_command_new
from rendercv.cli.render_command import render_command
from rendercv.cli.render_command.render_command import cli_command_render


class TestCliCommandRender:
    @pytest.fixture
    def default_arguments(self):
        context = MagicMock()
        context.args = []
        return {
            "design": None,
            "locale": None,
            "settings": None,
            "typst_path": None,
            "pdf_path": None,
            "markdown_path": None,
            "html_path": None,
            "png_path": None,
            "dont_generate_markdown": False,
            "dont_generate_html": False,
            "dont_generate_typst": False,
            "dont_generate_pdf": False,
            "dont_generate_png": False,
            "watch": False,
            "quiet": False,
            "yaml_field_override": None,
            "extra_data_model_override_arguments": context,
        }

    @pytest.fixture
    def input_file(self, tmp_path):
        os.chdir(tmp_path)
        cli_command_new(
            full_name="John Doe",
            create_typst_templates=False,
            create_markdown_templates=False,
        )
        return tmp_path / "John_Doe_CV.yaml"

    @pytest.mark.parametrize(
        ("quiet", "flags", "expected_files", "missing_files"),
        [
            # Default: generates all files
            (
                False,
                {},
                [
                    "John_Doe_CV.typ",
                    "John_Doe_CV.pdf",
                    "John_Doe_CV_1.png",
                    "John_Doe_CV.md",
                    "John_Doe_CV.html",
                ],
                [],
            ),
            (
                True,
                {},
                [
                    "John_Doe_CV.typ",
                    "John_Doe_CV.pdf",
                    "John_Doe_CV_1.png",
                    "John_Doe_CV.md",
                    "John_Doe_CV.html",
                ],
                [],
            ),
            # dont_generate_markdown: skips markdown and HTML
            (
                False,
                {"dont_generate_markdown": True},
                ["John_Doe_CV.typ", "John_Doe_CV.pdf", "John_Doe_CV_1.png"],
                ["John_Doe_CV.md", "John_Doe_CV.html"],
            ),
            # dont_generate_html: skips only HTML
            (
                False,
                {"dont_generate_html": True},
                [
                    "John_Doe_CV.typ",
                    "John_Doe_CV.pdf",
                    "John_Doe_CV_1.png",
                    "John_Doe_CV.md",
                ],
                ["John_Doe_CV.html"],
            ),
            # dont_generate_typst: skips only the source file
            (
                False,
                {"dont_generate_typst": True},
                [
                    "John_Doe_CV.md",
                    "John_Doe_CV.html",
                    "John_Doe_CV.pdf",
                    "John_Doe_CV_1.png",
                ],
                ["John_Doe_CV.typ"],
            ),
            # dont_generate_pdf: skips only PDF
            (
                False,
                {"dont_generate_pdf": True},
                [
                    "John_Doe_CV.typ",
                    "John_Doe_CV_1.png",
                    "John_Doe_CV.md",
                    "John_Doe_CV.html",
                ],
                ["John_Doe_CV.pdf"],
            ),
            # dont_generate_png: skips only PNG
            (
                False,
                {"dont_generate_png": True},
                [
                    "John_Doe_CV.typ",
                    "John_Doe_CV.pdf",
                    "John_Doe_CV.md",
                    "John_Doe_CV.html",
                ],
                ["John_Doe_CV_1.png"],
            ),
        ],
    )
    def test_output_file_generation(
        self, input_file, default_arguments, quiet, flags, expected_files, missing_files
    ):
        cli_command_render(
            input_file_name=input_file,
            **{**default_arguments, "quiet": quiet, **flags},
        )

        rendercv_output = input_file.parent / "rendercv_output"
        for file in expected_files:
            assert (rendercv_output / file).exists()
        for file in missing_files:
            assert not (rendercv_output / file).exists()

    def test_uses_custom_output_paths(self, input_file, default_arguments):
        custom_paths = {
            "typst_path": input_file.parent / "custom.typ",
            "pdf_path": input_file.parent / "custom.pdf",
            "markdown_path": input_file.parent / "custom.md",
            "html_path": input_file.parent / "custom.html",
            "png_path": input_file.parent / "custom.png",
        }

        cli_command_render(
            input_file_name=input_file,
            **{**default_arguments, **custom_paths},
        )

        assert (input_file.parent / "custom.typ").exists()
        assert (input_file.parent / "custom.pdf").exists()
        assert (input_file.parent / "custom.md").exists()
        assert (input_file.parent / "custom.html").exists()
        assert (input_file.parent / "custom_1.png").exists()

    def test_accepts_relative_input_file_path(self, input_file, default_arguments):
        cli_command_render(
            input_file_name=input_file.name,
            **default_arguments,
        )

        rendercv_output = input_file.parent / "rendercv_output"
        assert (rendercv_output / "John_Doe_CV.pdf").exists()

    @patch("rendercv.cli.render_command.render_command.run_rendercv")
    def test_converts_relative_input_path_to_absolute(
        self, mock_run, input_file, default_arguments
    ):
        cli_command_render(
            input_file_name=input_file.name,
            **default_arguments,
        )

        called_path = mock_run.call_args[0][0]
        assert called_path.is_absolute()

    @patch("rendercv.cli.render_command.render_command.run_function_if_files_change")
    def test_calls_watcher_when_watch_flag_is_true(
        self, mock_watcher, input_file, default_arguments
    ):
        cli_command_render(
            input_file_name=input_file,
            **{**default_arguments, "watch": True},  # ty: ignore[invalid-argument-type]
        )

        mock_watcher.assert_called_once()

    @pytest.mark.parametrize(
        ("config_type", "config_content", "expected_in_output"),
        [
            ("design", "design:\n  theme: moderncv\n", "Fontin"),
            (
                "locale",
                "locale:\n  language: turkish\n",
                'locale-catalog-language: "tr"',
            ),
            ("settings", "settings:\n  current_date: 1999-01-15\n", "Jan 1999"),
        ],
    )
    def test_uses_custom_config_files(
        self,
        input_file,
        default_arguments,
        config_type,
        config_content,
        expected_in_output,
    ):
        config_file = input_file.parent / f"custom_{config_type}.yaml"
        config_file.write_text(config_content, encoding="utf-8")

        arguments = {**default_arguments, config_type: config_file}
        cli_command_render(input_file_name=input_file, **arguments)

        typst_file = input_file.parent / "rendercv_output" / "John_Doe_CV.typ"
        assert expected_in_output in typst_file.read_text()

    @pytest.mark.parametrize(
        ("render_command_field", "config_content", "expected_in_output"),
        [
            ("design", "design:\n  theme: moderncv\n", "Fontin"),
            (
                "locale",
                "locale:\n  language: turkish\n",
                'locale-catalog-language: "tr"',
            ),
        ],
    )
    def test_loads_overlay_files_from_yaml_settings(
        self,
        tmp_path,
        default_arguments,
        render_command_field,
        config_content,
        expected_in_output,
    ):
        os.chdir(tmp_path)

        config_file = tmp_path / f"my_{render_command_field}.yaml"
        config_file.write_text(config_content, encoding="utf-8")

        # Create a minimal YAML with render_command referencing the overlay file
        input_file = tmp_path / "test_cv.yaml"
        input_file.write_text(
            "cv:\n"
            "  name: John Doe\n"
            "settings:\n"
            "  render_command:\n"
            f"    {render_command_field}: my_{render_command_field}.yaml\n",
            encoding="utf-8",
        )

        cli_command_render(input_file_name=input_file, **default_arguments)

        typst_file = tmp_path / "rendercv_output" / "John_Doe_CV.typ"
        assert expected_in_output in typst_file.read_text()


@pytest.mark.parametrize("role", ["design", "locale"])
@pytest.mark.parametrize("winner", ["main", "settings", "cli"])
def test_overlay_precedence_and_base_directory(tmp_path, monkeypatch, role, winner):

    monkeypatch.chdir(tmp_path)
    cv_dir = tmp_path / "cv"
    cv_dir.mkdir()
    input_file = cv_dir / "cv.yaml"
    input_file.write_text(
        f"cv:\n  name: Jane Doe\nsettings:\n  render_command:\n    {role}: main.yaml\n",
        encoding="utf-8",
    )
    contents = (
        "design:\n  theme: moderncv\n"
        if role == "design"
        else "locale:\n  language: turkish\n"
    )
    (cv_dir / "main.yaml").write_text(
        contents if winner == "main" else f"{role}: {{}}", encoding="utf-8"
    )
    (cv_dir / "chosen.yaml").write_text(contents, encoding="utf-8")
    (tmp_path / "cli.yaml").write_text(contents, encoding="utf-8")
    settings = tmp_path / "settings.yaml"
    settings.write_text(
        "settings:\n  current_date: 2020-01-01\n"
        + (
            f"  render_command:\n    {role}:"
            f" {'missing.yaml' if winner == 'cli' else 'chosen.yaml'}\n"
            if winner != "main"
            else ""
        ),
        encoding="utf-8",
    )
    args = [
        "render",
        "cv/cv.yaml",
        "--settings",
        "settings.yaml",
        "-q",
        "-nopdf",
        "-nopng",
    ]
    if winner == "cli":
        args.extend(
            ["--design" if role == "design" else "--locale-catalog", "cli.yaml"]
        )
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.exception
    source = (cv_dir / "rendercv_output" / "Jane_Doe_CV.typ").read_text()
    assert ("Fontin" if role == "design" else 'locale-catalog-language: "tr"') in source


def test_watch_reads_overlays_each_render_and_refreshes_references(
    tmp_path, monkeypatch
):

    monkeypatch.chdir(tmp_path)
    input_file = tmp_path / "cv.yaml"
    input_file.write_text("cv:\n  name: Jane Doe\n", encoding="utf-8")
    settings = tmp_path / "settings.yaml"
    settings.write_text(
        "settings:\n  render_command:\n    design: design.yaml\n    locale:"
        " locale.yaml\n",
        encoding="utf-8",
    )
    design = tmp_path / "design.yaml"
    design.write_text("design:\n  theme: classic\n", encoding="utf-8")
    locale = tmp_path / "locale.yaml"
    locale.write_text("locale:\n  language: english\n", encoding="utf-8")
    replacement = tmp_path / "nested" / "replacement.yaml"
    replacement.parent.mkdir()
    replacement.write_text("design:\n  theme: sb2nov\n", encoding="utf-8")
    source = tmp_path / "rendercv_output" / "Jane_Doe_CV.typ"

    def watch(paths, render):
        assert set(paths()) == {input_file, settings, design, locale}
        assert render()
        assert "Source Sans 3" in source.read_text()
        design.write_text("design:\n  theme: moderncv\n", encoding="utf-8")
        assert render()
        assert "Fontin" in source.read_text()
        locale.write_text("locale:\n  language: turkish\n", encoding="utf-8")
        assert render()
        assert 'locale-catalog-language: "tr"' in source.read_text()
        settings.write_text("settings: [", encoding="utf-8")
        assert not render()
        settings.write_text(
            "settings:\n  current_date: 1999-01-15\n  render_command:\n    design:"
            " nested/replacement.yaml\n",
            encoding="utf-8",
        )
        assert set(paths()) == {input_file, settings, replacement}
        assert render()
        assert "Jan 1999" in source.read_text()
        assert "New Computer Modern" in source.read_text()

    monkeypatch.setattr(render_command, "run_function_if_files_change", watch)
    context = MagicMock(args=[])
    cli_command_render(
        input_file,
        settings=settings,
        watch=True,
        quiet=True,
        dont_generate_pdf=True,
        dont_generate_png=True,
        extra_data_model_override_arguments=context,
    )


@pytest.mark.parametrize(
    "yaml",
    ["cv: [", "settings: null", "settings:\n  render_command: []", "a scalar", ""],
)
def test_invalid_input_has_cli_exit_code_one(tmp_path, monkeypatch, yaml):

    monkeypatch.chdir(tmp_path)
    (tmp_path / "cv.yaml").write_text(yaml, encoding="utf-8")
    result = CliRunner().invoke(app, ["render", "cv.yaml", "-q"])
    assert result.exit_code == 1
    assert result.output == ""


def test_all_cli_output_paths_are_cwd_relative(tmp_path, monkeypatch):

    monkeypatch.chdir(tmp_path)
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs" / "cv.yaml").write_text(
        "cv:\n  name: Jane Doe\nsettings:\n  current_date: 2025-01-02\n",
        encoding="utf-8",
    )
    args = ["render", "inputs/cv.yaml", "-q"]
    for option, extension in [
        ("typst", "typ"),
        ("pdf", "pdf"),
        ("markdown", "md"),
        ("html", "html"),
        ("png", "png"),
    ]:
        args.extend([f"--{option}-path", f"build/2025/NAME_IN_SNAKE_CASE.{extension}"])
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.exception
    assert sorted(p.name for p in (tmp_path / "build" / "2025").iterdir()) == [
        "Jane_Doe.html",
        "Jane_Doe.md",
        "Jane_Doe.pdf",
        "Jane_Doe.typ",
        "Jane_Doe_1.png",
    ]
    assert not (tmp_path / "inputs" / "build").exists()


def test_cli_output_folder_is_cwd_relative(tmp_path, monkeypatch):

    monkeypatch.chdir(tmp_path)
    (tmp_path / "inputs").mkdir()
    (tmp_path / "inputs" / "cv.yaml").write_text(
        "cv:\n  name: Jane Doe\nsettings:\n  current_date: 2025-01-02\n",
        encoding="utf-8",
    )
    result = CliRunner().invoke(
        app,
        [
            "render",
            "inputs/cv.yaml",
            "-q",
            "-nopdf",
            "-nopng",
            "--output-folder",
            "build/2025",
            "--typst-path",
            "OUTPUT_FOLDER/NAME_IN_SNAKE_CASE.typ",
        ],
    )
    assert result.exit_code == 0, result.exception
    assert (tmp_path / "build" / "2025" / "Jane_Doe.typ").is_file()
    assert (tmp_path / "build" / "2025" / "Jane_Doe_CV.md").is_file()
    assert not (tmp_path / "inputs" / "build").exists()


def test_overlays_are_merged_in_order_before_field_overrides(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cv.yaml").write_text(
        "cv:\n  name: Jane Doe\n  email: jane@example.com\n"
        "  location: Public City\n  headline: Public\n",
        encoding="utf-8",
    )
    (tmp_path / "a.yaml").write_text(
        "cv:\n  email: jane@private.com\n  location: Private City\n",
        encoding="utf-8",
    )
    (tmp_path / "b.yaml").write_text("cv:\n  location: Home\n", encoding="utf-8")
    result = CliRunner().invoke(
        app,
        [
            "render",
            "cv.yaml",
            "-q",
            "-nopdf",
            "-nopng",
            "-notyp",
            "-nohtml",
            "--overlay",
            "a.yaml",
            "--overlay",
            "b.yaml",
            "--cv.headline",
            "Override",
        ],
    )
    assert result.exit_code == 0, result.output

    markdown = (tmp_path / "rendercv_output" / "Jane_Doe_CV.md").read_text(
        encoding="utf-8"
    )
    assert "jane@private.com" in markdown
    assert "Home" in markdown
    assert "Override" in markdown
