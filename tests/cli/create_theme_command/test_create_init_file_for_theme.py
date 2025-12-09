import pytest

from rendercv.cli.create_theme_command.create_init_file_for_theme import (
    create_init_file_for_theme,
)
from rendercv.exception import RenderCVUserError


class TestCreateInitFileForTheme:
    @pytest.mark.parametrize(
        "theme_name",
        [
            "mytheme",
            "theme123",
            "custom",
        ],
    )
    def test_creates_init_file_with_valid_theme_name(self, tmp_path, theme_name):
        init_file_path = tmp_path / "__init__.py"

        create_init_file_for_theme(theme_name, init_file_path)

        assert init_file_path.exists()
        content = init_file_path.read_text(encoding="utf-8")
        assert f'theme: Literal["{theme_name}"]' in content
        assert f"{theme_name.capitalize()}Theme" in content

    @pytest.mark.parametrize(
        "theme_name",
        [
            "MyTheme",
            "my-theme",
            "my_theme",
            "theme!",
            "UPPERCASE",
        ],
    )
    def test_raises_error_for_invalid_theme_name(self, tmp_path, theme_name):
        init_file_path = tmp_path / "__init__.py"

        with pytest.raises(RenderCVUserError):
            create_init_file_for_theme(theme_name, init_file_path)
