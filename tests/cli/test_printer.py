import json
from unittest.mock import MagicMock, patch

import pytest

from rendercv import __version__
from rendercv.cli import printer


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
    def test_warning_based_on_version(
        self, mock_urlopen, version, should_warn, capsys
    ):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"info": {"version": version}}
        ).encode("utf-8")
        mock_response.info.return_value.get_content_charset.return_value = "utf-8"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        printer.warn_if_new_version_is_available()

        captured = capsys.readouterr()
        if should_warn:
            assert "new version" in captured.out.lower()
        else:
            assert "new version" not in captured.out.lower()

    @patch("urllib.request.urlopen")
    def test_no_warning_when_request_fails(self, mock_urlopen, capsys):
        mock_urlopen.side_effect = Exception("Network error")

        printer.warn_if_new_version_is_available()

        captured = capsys.readouterr()
        assert "new version" not in captured.out.lower()


@pytest.mark.parametrize(
    "text",
    [
        "This is a warning",
        "Another warning message",
        "",
    ],
)
def test_warning(text, capsys):
    printer.warning(text)

    captured = capsys.readouterr()
    assert text in captured.out


@pytest.mark.parametrize(
    "text",
    [
        "This is an error",
        "Another error message",
        "",
    ],
)
def test_error(text, capsys):
    printer.error(text)

    captured = capsys.readouterr()
    assert text in captured.out
