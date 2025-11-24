import os

import pytest

from rendercv.cli.new_command.new_command import cli_command_new


class TestCliCommandNew:
    @pytest.mark.parametrize("dont_create_typst_templates", [True, False])
    @pytest.mark.parametrize("dont_create_markdown_templates", [True, False])
    @pytest.mark.parametrize("input_file_exists", [True, False])
    @pytest.mark.parametrize("typst_templates_exist", [True, False])
    @pytest.mark.parametrize("markdown_templates_exist", [True, False])
    def test_cli_command_new(
        self,
        tmp_path,
        dont_create_typst_templates,
        dont_create_markdown_templates,
        input_file_exists,
        typst_templates_exist,
        markdown_templates_exist,
    ):
        os.chdir(tmp_path)

        full_name = "John Doe"
        theme = "classic"
        input_file_path = tmp_path / "John_Doe_CV.yaml"
        typst_folder = tmp_path / theme
        markdown_folder = tmp_path / "markdown"

        # Set up pre-existing files/folders
        if input_file_exists:
            input_file_path.write_text("existing content")
        if typst_templates_exist:
            typst_folder.mkdir()
        if markdown_templates_exist:
            markdown_folder.mkdir()

        cli_command_new(
            full_name=full_name,
            theme=theme,
            dont_create_typst_templates=dont_create_typst_templates,
            dont_create_markdown_templates=dont_create_markdown_templates,
        )

        # Input file should always exist after command
        assert input_file_path.exists()

        # If input file existed before, content should be unchanged
        if input_file_exists:
            assert input_file_path.read_text() == "existing content"

        # Typst templates
        if dont_create_typst_templates:
            # Should not be created (unless already existed)
            if not typst_templates_exist:
                assert not typst_folder.exists()
        else:
            # Should exist (created or already existed)
            assert typst_folder.exists()

        # Markdown templates
        if dont_create_markdown_templates:
            # Should not be created (unless already existed)
            if not markdown_templates_exist:
                assert not markdown_folder.exists()
        else:
            # Should exist (created or already existed)
            assert markdown_folder.exists()

    def test_errors_for_invalid_theme(self, tmp_path, capsys):
        os.chdir(tmp_path)

        cli_command_new(
            full_name="John Doe",
            theme="invalid_theme",
            dont_create_typst_templates=False,
            dont_create_markdown_templates=False,
        )

        captured = capsys.readouterr()
        assert "invalid_theme" in captured.out
        assert "not available" in captured.out
