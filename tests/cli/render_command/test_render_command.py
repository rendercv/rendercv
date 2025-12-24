import os
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
            # dont_generate_typst: skips Typst, PDF, and PNG
            (
                False,
                {"dont_generate_typst": True},
                ["John_Doe_CV.md", "John_Doe_CV.html"],
                ["John_Doe_CV.typ", "John_Doe_CV.pdf", "John_Doe_CV_1.png"],
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

    @patch("rendercv.cli.render_command.render_command.run_function_if_file_changes")
    def test_calls_watcher_when_watch_flag_is_true(
        self, mock_watcher, input_file, default_arguments
    ):
        cli_command_render(
            input_file_name=input_file,
            **{**default_arguments, "watch": True},  # ty: ignore
        )

        mock_watcher.assert_called_once()
        call_args = mock_watcher.call_args
        # Should watch the input file (now passed as a list)
        assert input_file.absolute() in call_args[0][0]

    @patch("rendercv.cli.render_command.render_command.run_function_if_file_changes")
    def test_watcher_includes_config_files(
        self, mock_watcher, input_file, default_arguments
    ):
        """Test that watch mode monitors included config files (design, locale, settings)."""
        design_file = input_file.parent / "custom_design.yaml"
        design_file.write_text("design:\n  theme: moderncv\n", encoding="utf-8")

        locale_file = input_file.parent / "custom_locale.yaml"
        locale_file.write_text("locale:\n  language: turkish\n", encoding="utf-8")

        cli_command_render(
            input_file_name=input_file,
            **{
                **default_arguments,
                "watch": True,
                "design": design_file,
                "locale": locale_file,
            },
        )

        mock_watcher.assert_called_once()
        call_args = mock_watcher.call_args
        watched_files = call_args[0][0]

        # Should watch all three files
        assert input_file.absolute() in watched_files
        assert design_file in watched_files
        assert locale_file in watched_files

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
