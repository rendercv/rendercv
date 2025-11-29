import json
import pathlib
from unittest.mock import MagicMock, patch

import pytest

from rendercv import __version__
from rendercv.cli.app import app, warn_if_new_version_is_available


def test_all_commands_are_registered():
    cli_folder = (
        pathlib.Path(__file__).parent.parent.parent / "src" / "rendercv" / "cli"
    )
    command_files = list(cli_folder.rglob("*_command.py"))

    registered_commands = app.registered_commands

    assert len(registered_commands) == len(command_files)


class TestWarnIfNewVersionIsAvailable:
    @pytest.mark.parametrize(
        ("version", "should_warn"),
        [
            ("99.0.0", True),
            ("0.0.1", False),
            (__version__, False),
        ],
    )
    @patch("urllib.request.urlopen")
    def test_warns_when_newer_version_available(self, mock_urlopen, version, should_warn, capsys):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"info": {"version": version}}
        ).encode("utf-8")
        mock_response.info.return_value.get_content_charset.return_value = "utf-8"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        warn_if_new_version_is_available()

        captured = capsys.readouterr()
        if should_warn:
            assert "new version" in captured.out.lower()
        else:
            assert "new version" not in captured.out.lower()

    @patch("urllib.request.urlopen")
    def test_handles_network_errors_gracefully(self, mock_urlopen, capsys):
        mock_urlopen.side_effect = Exception("Network error")

        warn_if_new_version_is_available()

        captured = capsys.readouterr()
        assert "new version" not in captured.out.lower()
