import contextlib
import os

import pytest
import typer

from rendercv.cli.new_command.new_command import cli_command_new
from rendercv.schema.rendercv_model_builder import build_rendercv_dictionary_and_model


class TestCliCommandNew:
    @pytest.mark.parametrize("create_typst_templates", [True, False])
    @pytest.mark.parametrize("create_markdown_templates", [True, False])
    @pytest.mark.parametrize("input_file_exists", [True, False])
    @pytest.mark.parametrize("typst_templates_exist", [True, False])
    @pytest.mark.parametrize("markdown_templates_exist", [True, False])
    @pytest.mark.parametrize("cover", [False])
    def test_cli_command_new(
        self,
        tmp_path,
        create_typst_templates,
        create_markdown_templates,
        input_file_exists,
        typst_templates_exist,
        markdown_templates_exist,
        cover,
    ):
        os.chdir(tmp_path)

        full_name = "John Doe"
        suffix = "Cover" if cover else "CV"
        input_file_path = tmp_path / f"John_Doe_{suffix}.yaml"
        typst_folder = tmp_path / "classic"
        markdown_folder = tmp_path / "markdown"

        # Set up pre-existing files/folders
        if input_file_exists:
            input_file_path.write_text("existing content", encoding="utf-8")
        if typst_templates_exist:
            typst_folder.mkdir()
        if markdown_templates_exist:
            markdown_folder.mkdir()

        cli_command_new(
            full_name=full_name,
            theme="classic",
            create_typst_templates=create_typst_templates,
            create_markdown_templates=create_markdown_templates,
            cover=cover,
        )

        # Input file should always exist after command
        assert input_file_path.exists()

        # If input file existed before, content should be unchanged
        if input_file_exists:
            assert input_file_path.read_text(encoding="utf-8") == "existing content"
        else:
            # Make sure it's a valid YAML file
            yaml_content = input_file_path.read_text(encoding="utf-8")
            build_rendercv_dictionary_and_model(
                yaml_content, input_file_path=input_file_path
            )

        # Typst templates
        if not create_typst_templates:
            # Should not be created (unless already existed)
            if not typst_templates_exist:
                assert not typst_folder.exists()
        else:
            # Should exist (created or already existed)
            assert typst_folder.exists()
            if typst_templates_exist:
                assert not (typst_folder / "Header.j2.typ").exists()
            else:
                assert (typst_folder / "Header.j2.typ").exists()

        # Markdown templates
        if not create_markdown_templates:
            # Should not be created (unless already existed)
            if not markdown_templates_exist:
                assert not markdown_folder.exists()
        else:
            # Should exist (created or already existed)
            assert markdown_folder.exists()
            if markdown_templates_exist:
                assert not (markdown_folder / "Header.j2.md").exists()
            else:
                assert (markdown_folder / "Header.j2.md").exists()

    def test_errors_for_invalid_theme(self, capsys):
        with contextlib.suppress(typer.Exit):
            cli_command_new(
                full_name="John Doe",
                theme="invalid_theme",
                create_typst_templates=False,
                create_markdown_templates=False,
            )

            captured = capsys.readouterr()
            assert "Available themes are:" in captured.out

    def test_errors_for_invalid_locale(self, capsys):
        with contextlib.suppress(typer.Exit):
            cli_command_new(
                full_name="John Doe",
                locale="invalid_locale",
                create_typst_templates=False,
                create_markdown_templates=False,
            )

            captured = capsys.readouterr()
            assert "Available locales are:" in captured.out
