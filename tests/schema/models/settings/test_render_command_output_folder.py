import pathlib

import pytest

from rendercv.schema.models.settings.render_command import (
    DEFAULT_OUTPUT_FOLDER,
    RenderCommand,
)


class TestRenderCommandOutputFolder:
    """Tests for the output_folder feature in RenderCommand."""

    def test_default_paths_without_output_folder(self):
        """When output_folder is not set, paths use default rendercv_output."""
        render_command = RenderCommand()

        # Paths are converted to absolute, but should contain the default folder name
        assert DEFAULT_OUTPUT_FOLDER in str(render_command.pdf_path)
        assert DEFAULT_OUTPUT_FOLDER in str(render_command.typst_path)
        assert DEFAULT_OUTPUT_FOLDER in str(render_command.markdown_path)
        assert DEFAULT_OUTPUT_FOLDER in str(render_command.html_path)
        assert DEFAULT_OUTPUT_FOLDER in str(render_command.png_path)

    def test_output_folder_replaces_default_in_all_paths(self):
        """When output_folder is set, it replaces rendercv_output in all paths."""
        render_command = RenderCommand(output_folder=pathlib.Path("build/en"))

        # Should contain new folder, not the default
        assert "build/en" in str(render_command.pdf_path)
        assert "build/en" in str(render_command.typst_path)
        assert "build/en" in str(render_command.markdown_path)
        assert "build/en" in str(render_command.html_path)
        assert "build/en" in str(render_command.png_path)
        # Ensure default folder is NOT present
        assert DEFAULT_OUTPUT_FOLDER not in str(render_command.pdf_path)
        assert DEFAULT_OUTPUT_FOLDER not in str(render_command.typst_path)

    def test_output_folder_with_trailing_slash(self):
        """output_folder with trailing slash works correctly."""
        render_command = RenderCommand(output_folder=pathlib.Path("build/en/"))

        assert "build/en" in str(render_command.pdf_path)
        assert DEFAULT_OUTPUT_FOLDER not in str(render_command.pdf_path)

    def test_output_folder_placeholder_in_custom_path(self):
        """OUTPUT_FOLDER placeholder is replaced in custom paths."""
        render_command = RenderCommand(
            output_folder=pathlib.Path("dist"),
            pdf_path=pathlib.Path("OUTPUT_FOLDER/custom_resume.pdf"),
        )

        assert "dist/custom_resume.pdf" in str(render_command.pdf_path)
        assert "OUTPUT_FOLDER" not in str(render_command.pdf_path)

    def test_output_folder_placeholder_with_subdirectory(self):
        """OUTPUT_FOLDER placeholder works with subdirectories."""
        render_command = RenderCommand(
            output_folder=pathlib.Path("build"),
            html_path=pathlib.Path("OUTPUT_FOLDER/web/index.html"),
        )

        assert "build/web/index.html" in str(render_command.html_path)
        assert "OUTPUT_FOLDER" not in str(render_command.html_path)

    def test_custom_absolute_path_not_modified(self):
        """Custom absolute paths are not modified by output_folder."""
        custom_path = pathlib.Path("/absolute/path/resume.pdf")
        render_command = RenderCommand(
            output_folder=pathlib.Path("build"),
            pdf_path=custom_path,
        )

        # Custom absolute path should remain unchanged
        assert str(render_command.pdf_path) == "/absolute/path/resume.pdf"

    def test_mixed_custom_and_default_paths(self):
        """Some paths can use defaults while others are customized."""
        render_command = RenderCommand(
            output_folder=pathlib.Path("build/en"),
            pdf_path=pathlib.Path("/absolute/my_cv.pdf"),
            # Other paths use defaults and should get output_folder applied
        )

        # Custom absolute path unchanged
        assert str(render_command.pdf_path) == "/absolute/my_cv.pdf"
        # Default paths get output_folder applied
        assert "build/en" in str(render_command.typst_path)
        assert "build/en" in str(render_command.html_path)
        assert DEFAULT_OUTPUT_FOLDER not in str(render_command.typst_path)

    def test_output_folder_none_preserves_defaults(self):
        """When output_folder is None, default paths remain unchanged."""
        render_command = RenderCommand(output_folder=None)

        assert DEFAULT_OUTPUT_FOLDER in str(render_command.pdf_path)

    @pytest.mark.parametrize(
        "output_folder",
        [
            "simple_folder",
            "nested/folder/path",
            "build/2024/en",
        ],
    )
    def test_various_output_folder_formats(self, output_folder: str):
        """Various output folder path formats work correctly."""
        render_command = RenderCommand(output_folder=pathlib.Path(output_folder))

        assert output_folder in str(render_command.pdf_path)
        assert DEFAULT_OUTPUT_FOLDER not in str(render_command.pdf_path)

    def test_output_folder_preserves_filename_placeholders(self):
        """output_folder replacement preserves NAME and other placeholders."""
        render_command = RenderCommand(output_folder=pathlib.Path("output"))

        # The NAME_IN_SNAKE_CASE placeholder should still be in the path
        assert "NAME_IN_SNAKE_CASE_CV" in str(render_command.pdf_path)
        assert "output" in str(render_command.pdf_path)
