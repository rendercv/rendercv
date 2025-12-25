import pathlib
import sys

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

        # Use pathlib for cross-platform path comparison
        pdf_path_str = str(render_command.pdf_path)
        # Check that 'build' and 'en' are in the path (works on both Windows and Unix)
        assert "build" in pdf_path_str
        assert "en" in pdf_path_str
        assert "build" in str(render_command.typst_path)
        assert "build" in str(render_command.markdown_path)
        assert "build" in str(render_command.html_path)
        assert "build" in str(render_command.png_path)
        # Ensure default folder is NOT present
        assert DEFAULT_OUTPUT_FOLDER not in pdf_path_str
        assert DEFAULT_OUTPUT_FOLDER not in str(render_command.typst_path)

    def test_output_folder_with_trailing_slash(self):
        """output_folder with trailing slash works correctly."""
        render_command = RenderCommand(output_folder=pathlib.Path("build/en/"))

        pdf_path_str = str(render_command.pdf_path)
        assert "build" in pdf_path_str
        assert "en" in pdf_path_str
        assert DEFAULT_OUTPUT_FOLDER not in pdf_path_str

    def test_output_folder_placeholder_in_custom_path(self):
        """OUTPUT_FOLDER placeholder is replaced in custom paths."""
        render_command = RenderCommand(
            output_folder=pathlib.Path("dist"),
            pdf_path=pathlib.Path("OUTPUT_FOLDER/custom_resume.pdf"),
        )

        pdf_path_str = str(render_command.pdf_path)
        assert "dist" in pdf_path_str
        assert "custom_resume.pdf" in pdf_path_str
        assert "OUTPUT_FOLDER" not in pdf_path_str

    def test_output_folder_placeholder_with_subdirectory(self):
        """OUTPUT_FOLDER placeholder works with subdirectories."""
        render_command = RenderCommand(
            output_folder=pathlib.Path("build"),
            html_path=pathlib.Path("OUTPUT_FOLDER/web/index.html"),
        )

        html_path_str = str(render_command.html_path)
        assert "build" in html_path_str
        assert "web" in html_path_str
        assert "index.html" in html_path_str
        assert "OUTPUT_FOLDER" not in html_path_str

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-style absolute paths")
    def test_custom_absolute_path_not_modified_unix(self):
        """Custom absolute paths are not modified by output_folder (Unix)."""
        custom_path = pathlib.Path("/absolute/path/resume.pdf")
        render_command = RenderCommand(
            output_folder=pathlib.Path("build"),
            pdf_path=custom_path,
        )

        # Custom absolute path should remain unchanged
        assert str(render_command.pdf_path) == "/absolute/path/resume.pdf"

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-style absolute paths")
    def test_custom_absolute_path_not_modified_windows(self):
        """Custom absolute paths are not modified by output_folder (Windows)."""
        custom_path = pathlib.Path("C:/absolute/path/resume.pdf")
        render_command = RenderCommand(
            output_folder=pathlib.Path("build"),
            pdf_path=custom_path,
        )

        # Custom absolute path should remain unchanged
        assert "absolute" in str(render_command.pdf_path)
        assert "resume.pdf" in str(render_command.pdf_path)

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-style absolute paths")
    def test_mixed_custom_and_default_paths_unix(self):
        """Some paths can use defaults while others are customized (Unix)."""
        render_command = RenderCommand(
            output_folder=pathlib.Path("build/en"),
            pdf_path=pathlib.Path("/absolute/my_cv.pdf"),
        )

        # Custom absolute path unchanged
        assert str(render_command.pdf_path) == "/absolute/my_cv.pdf"
        # Default paths get output_folder applied
        assert "build" in str(render_command.typst_path)
        assert "build" in str(render_command.html_path)
        assert DEFAULT_OUTPUT_FOLDER not in str(render_command.typst_path)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-style absolute paths")
    def test_mixed_custom_and_default_paths_windows(self):
        """Some paths can use defaults while others are customized (Windows)."""
        render_command = RenderCommand(
            output_folder=pathlib.Path("build/en"),
            pdf_path=pathlib.Path("C:/absolute/my_cv.pdf"),
        )

        # Custom absolute path should contain original components
        assert "my_cv.pdf" in str(render_command.pdf_path)
        # Default paths get output_folder applied
        assert "build" in str(render_command.typst_path)
        assert "build" in str(render_command.html_path)
        assert DEFAULT_OUTPUT_FOLDER not in str(render_command.typst_path)

    def test_output_folder_none_preserves_defaults(self):
        """When output_folder is None, default paths remain unchanged."""
        render_command = RenderCommand(output_folder=None)

        assert DEFAULT_OUTPUT_FOLDER in str(render_command.pdf_path)

    def test_simple_output_folder(self):
        """Simple output folder name works correctly."""
        render_command = RenderCommand(output_folder=pathlib.Path("simple_folder"))

        assert "simple_folder" in str(render_command.pdf_path)
        assert DEFAULT_OUTPUT_FOLDER not in str(render_command.pdf_path)

    def test_nested_output_folder(self):
        """Nested output folder path works correctly."""
        render_command = RenderCommand(output_folder=pathlib.Path("nested/folder/path"))

        pdf_path_str = str(render_command.pdf_path)
        assert "nested" in pdf_path_str
        assert "folder" in pdf_path_str
        assert "path" in pdf_path_str
        assert DEFAULT_OUTPUT_FOLDER not in pdf_path_str

    def test_output_folder_preserves_filename_placeholders(self):
        """output_folder replacement preserves NAME and other placeholders."""
        render_command = RenderCommand(output_folder=pathlib.Path("output"))

        # The NAME_IN_SNAKE_CASE placeholder should still be in the path
        assert "NAME_IN_SNAKE_CASE_CV" in str(render_command.pdf_path)
        assert "output" in str(render_command.pdf_path)
