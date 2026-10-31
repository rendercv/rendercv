from unittest.mock import MagicMock

import pytest

from rendercv.cli.render_command.parse_override_arguments import (
    parse_override_arguments,
)
from rendercv.exception import RenderCVUserError


class TestParseOverrideArguments:
    @pytest.mark.parametrize(
        ("args", "expected"),
        [
            (["--cv.name", "John"], {"cv.name": "John"}),
            (
                ["--cv.name", "John", "--cv.email", "john@example.com"],
                {"cv.name": "John", "cv.email": "john@example.com"},
            ),
            ([], {}),
        ],
    )
    def test_parses_key_value_pairs_into_dictionary(self, args, expected):
        context = MagicMock()
        context.args = args

        result = parse_override_arguments(context)

        assert result == expected

    def test_raises_error_for_odd_number_of_arguments(self):
        context = MagicMock()
        context.args = ["--cv.name"]

        with pytest.raises(RenderCVUserError):
            parse_override_arguments(context)

    def test_raises_error_when_key_doesnt_start_with_dashes(self):
        context = MagicMock()
        context.args = ["cv.name", "John"]

        with pytest.raises(RenderCVUserError):
            parse_override_arguments(context)

    @pytest.mark.parametrize("field", ["pdf_path", "typst_path", "output_folder"])
    def test_dotted_output_paths_use_the_working_directory(
        self, tmp_path, monkeypatch, field
    ):
        monkeypatch.chdir(tmp_path)
        context = MagicMock()
        context.args = [f"--settings.render_command.{field}", "build/result"]
        result = parse_override_arguments(context)
        assert result[f"settings.render_command.{field}"] == str(
            tmp_path / "build" / "result"
        )

    @pytest.mark.parametrize(
        "photo", ["images/profile.png", "https://example.com/a.png"]
    )
    def test_photo_override_uses_cli_path_rules_without_changing_urls(
        self, tmp_path, monkeypatch, photo
    ):
        monkeypatch.chdir(tmp_path)
        context = MagicMock()
        context.args = ["--cv.photo", photo]
        result = parse_override_arguments(context)
        expected = photo if photo.startswith("https://") else str(tmp_path / photo)
        assert result["cv.photo"] == expected
