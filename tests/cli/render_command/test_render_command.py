import os
import pathlib
from unittest.mock import MagicMock, patch

import pytest

from rendercv.cli.new_command.new_command import cli_command_new
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
            "_": None,
            "extra_data_model_override_arguments": context,
        }

    @pytest.fixture
    def sample_cv_with_templates(self, tmp_path):
        os.chdir(tmp_path)
        cli_command_new(
            full_name="John Doe",
            create_typst_templates=False,
            create_markdown_templates=False,
        )
        return tmp_path / "John_Doe_CV.yaml"

    @pytest.mark.parametrize("quiet", [True, False])
    def test_generates_all_output_files_by_default(
        self, sample_cv_with_templates, default_arguments, quiet
    ):
        os.chdir(sample_cv_with_templates.parent)

        cli_command_render(
            input_file_name=str(sample_cv_with_templates),
            **{**default_arguments, "quiet": quiet},
        )

        rendercv_output = sample_cv_with_templates.parent / "rendercv_output"
        assert (rendercv_output / "John_Doe_CV.typ").exists()
        assert (rendercv_output / "John_Doe_CV.pdf").exists()
        assert (rendercv_output / "John_Doe_CV_1.png").exists()
        assert (rendercv_output / "John_Doe_CV.md").exists()
        assert (rendercv_output / "John_Doe_CV.html").exists()

    @pytest.mark.parametrize(
        ("flag", "missing_files"),
        [
            (
                "dont_generate_markdown",
                ["John_Doe_CV.md", "John_Doe_CV.html"],
            ),
            ("dont_generate_html", ["John_Doe_CV.html"]),
            (
                "dont_generate_typst",
                ["John_Doe_CV.typ", "John_Doe_CV.pdf", "John_Doe_CV_1.png"],
            ),
            ("dont_generate_pdf", ["John_Doe_CV.pdf"]),
            ("dont_generate_png", ["John_Doe_CV_1.png"]),
        ],
    )
    def test_respects_dont_generate_flags(
        self, sample_cv_with_templates, default_arguments, flag, missing_files
    ):
        os.chdir(sample_cv_with_templates.parent)

        cli_command_render(
            input_file_name=str(sample_cv_with_templates),
            **{**default_arguments, flag: True},
        )

        rendercv_output = sample_cv_with_templates.parent / "rendercv_output"
        for file in missing_files:
            assert not (rendercv_output / file).exists()

    def test_uses_custom_output_paths(
        self, sample_cv_with_templates, default_arguments
    ):
        os.chdir(sample_cv_with_templates.parent)

        custom_paths = {
            "typst_path": "custom.typ",
            "pdf_path": "custom.pdf",
            "markdown_path": "custom.md",
            "html_path": "custom.html",
            "png_path": "custom.png",
        }

        cli_command_render(
            input_file_name=str(sample_cv_with_templates),
            **{**default_arguments, **custom_paths},
        )

        parent = sample_cv_with_templates.parent
        assert (parent / "custom.typ").exists()
        assert (parent / "custom.pdf").exists()
        assert (parent / "custom.md").exists()
        assert (parent / "custom.html").exists()
        assert (parent / "custom_1.png").exists()

    def test_accepts_relative_input_file_path(
        self, sample_cv_with_templates, default_arguments
    ):
        os.chdir(sample_cv_with_templates.parent)

        cli_command_render(
            input_file_name=sample_cv_with_templates.name,
            **default_arguments,
        )

        rendercv_output = sample_cv_with_templates.parent / "rendercv_output"
        assert (rendercv_output / "John_Doe_CV.pdf").exists()

    @patch("rendercv.cli.render_command.render_command.run_function_if_file_changes")
    def test_calls_watcher_when_watch_flag_is_true(
        self, mock_watcher, sample_cv_with_templates, default_arguments
    ):
        os.chdir(sample_cv_with_templates.parent)

        cli_command_render(
            input_file_name=str(sample_cv_with_templates),
            **{**default_arguments, "watch": True},
        )

        mock_watcher.assert_called_once()
        call_args = mock_watcher.call_args
        assert call_args[0][0] == sample_cv_with_templates.absolute()

    def test_uses_custom_design_file(
        self, sample_cv_with_templates, default_arguments, tmp_path
    ):
        os.chdir(sample_cv_with_templates.parent)

        # Create a custom design file with specific color settings
        design_file = tmp_path / "custom_design.yaml"
        design_file.write_text(
            "design:\n  theme: classic\n  colors:\n    name: rgb(255, 0, 0)\n",  # Red color for verification
            encoding="utf-8",
        )

        cli_command_render(
            input_file_name=str(sample_cv_with_templates),
            **{**default_arguments, "design": str(design_file)},
        )

        # Verify output was generated successfully
        rendercv_output = sample_cv_with_templates.parent / "rendercv_output"
        typst_file = rendercv_output / "John_Doe_CV.typ"
        assert typst_file.exists()

        # Verify the custom design was used by checking for the red color
        typst_content = typst_file.read_text()
        assert "colors-name: rgb(255, 0, 0)" in typst_content

    def test_uses_custom_locale_file(
        self, sample_cv_with_templates, default_arguments, tmp_path
    ):
        os.chdir(sample_cv_with_templates.parent)

        # Create a custom locale file
        locale_file: pathlib.Path = tmp_path / "custom_locale.yaml"
        locale_file.write_text(
            "locale:\n"
            "  language: turkish\n"
            "  month_abbreviations:\n"
            "    - Oca\n"
            "    - Şub\n"
            "    - Mar\n"
            "    - Nis\n"
            "    - May\n"
            "    - Haz\n"
            "    - Tem\n"
            "    - Ağu\n"
            "    - Eyl\n"
            "    - Eki\n"
            "    - Kas\n"
            "    - Ara\n",
            encoding="utf-8",
        )

        cli_command_render(
            input_file_name=str(sample_cv_with_templates),
            **{**default_arguments, "locale": str(locale_file)},
        )

        # Verify output was generated successfully
        rendercv_output = sample_cv_with_templates.parent / "rendercv_output"
        assert (rendercv_output / "John_Doe_CV.pdf").exists()
        assert (rendercv_output / "John_Doe_CV.typ").exists()

    def test_uses_custom_settings_file(
        self, sample_cv_with_templates, default_arguments, tmp_path
    ):
        os.chdir(sample_cv_with_templates.parent)

        # Create a custom settings file with a specific date
        settings_file = tmp_path / "custom_settings.yaml"
        settings_file.write_text(
            "settings:\n  current_date: '2024-01-15'\n", encoding="utf-8"
        )

        cli_command_render(
            input_file_name=str(sample_cv_with_templates),
            **{**default_arguments, "settings": str(settings_file)},
        )

        # Verify output was generated successfully
        rendercv_output = sample_cv_with_templates.parent / "rendercv_output"
        assert (rendercv_output / "John_Doe_CV.pdf").exists()
        assert (rendercv_output / "John_Doe_CV.typ").exists()
