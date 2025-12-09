import os

import pytest

from rendercv.cli.create_theme_command.create_theme_command import (
    cli_command_create_theme,
)
from rendercv.exception import RenderCVUserError


class TestCliCommandCreateTheme:
    def test_creates_theme_folder(self, tmp_path):
        os.chdir(tmp_path)
        theme_name = "mytheme"

        cli_command_create_theme(theme_name)

        theme_folder = tmp_path / theme_name
        assert theme_folder.exists()
        assert (theme_folder / "__init__.py").exists()
        assert (theme_folder / "Preamble.j2.typ").exists()

        init_content = (theme_folder / "__init__.py").read_text(encoding="utf-8")
        assert f'theme: Literal["{theme_name}"]' in init_content

    def test_raises_error_if_folder_exists(self, tmp_path):
        os.chdir(tmp_path)
        theme_name = "mytheme"
        (tmp_path / theme_name).mkdir()

        with pytest.raises(RenderCVUserError, match="already exists"):
            cli_command_create_theme(theme_name)

    def test_raises_error_for_invalid_theme_name(self, tmp_path):
        os.chdir(tmp_path)

        with pytest.raises(RenderCVUserError):
            cli_command_create_theme("Invalid-Theme")
