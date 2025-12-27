import json
import pathlib
import time
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from rendercv import __version__
from rendercv.cli.app import (
    _fetch_and_cache_latest_version,
    _read_version_cache,
    app,
    warn_if_new_version_is_available,
)


def test_all_commands_are_registered():
    cli_folder = (
        pathlib.Path(__file__).parent.parent.parent / "src" / "rendercv" / "cli"
    )
    command_files = list(cli_folder.rglob("*_command.py"))

    registered_commands = app.registered_commands

    assert len(registered_commands) == len(command_files)


class TestCliCommandNoArgs:
    @patch("rendercv.cli.app.warn_if_new_version_is_available")
    def test_prints_version_when_requested(self, mock_warn):
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert f"RenderCV v{__version__}" in result.output
        mock_warn.assert_called_once()

    @patch("rendercv.cli.app.warn_if_new_version_is_available")
    def test_prints_version_with_short_flag(self, mock_warn):
        runner = CliRunner()
        result = runner.invoke(app, ["-v"])

        assert result.exit_code == 0
        assert f"RenderCV v{__version__}" in result.output
        mock_warn.assert_called_once()

    @patch("rendercv.cli.app.warn_if_new_version_is_available")
    def test_shows_help_when_no_args(self, mock_warn):
        runner = CliRunner()
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "RenderCV is a command-line tool" in result.output
        mock_warn.assert_called_once()


class TestWarnIfNewVersionIsAvailable:
    @pytest.fixture(autouse=True)
    def clean_cache(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "version_check.json"
        monkeypatch.setattr("rendercv.cli.app._VERSION_CACHE_FILE", cache_file)
        yield cache_file
        if cache_file.exists():
            cache_file.unlink()

    @pytest.mark.parametrize(
        ("version", "should_warn"),
        [
            ("99.0.0", True),
            ("0.0.1", False),
            (__version__, False),
        ],
    )
    def test_warns_when_cached_version_is_newer(
        self, clean_cache, version, should_warn, capsys
    ):
        cache_data = {"latest_version": version, "timestamp": time.time()}
        clean_cache.parent.mkdir(parents=True, exist_ok=True)
        clean_cache.write_text(json.dumps(cache_data), encoding="utf-8")

        warn_if_new_version_is_available()

        captured = capsys.readouterr()
        if should_warn:
            assert "new version" in captured.out.lower()
        else:
            assert "new version" not in captured.out.lower()

    def test_spawns_background_thread_on_cache_miss(self):
        with patch("rendercv.cli.app.threading.Thread") as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            warn_if_new_version_is_available()

            mock_thread.assert_called_once()
            assert mock_thread.call_args.kwargs["daemon"] is True
            mock_thread_instance.start.assert_called_once()

    def test_spawns_background_thread_on_stale_cache(self, clean_cache):
        stale_time = time.time() - 86401
        cache_data = {"latest_version": "99.0.0", "timestamp": stale_time}
        clean_cache.parent.mkdir(parents=True, exist_ok=True)
        clean_cache.write_text(json.dumps(cache_data), encoding="utf-8")

        with patch("rendercv.cli.app.threading.Thread") as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            warn_if_new_version_is_available()

            mock_thread.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_fetch_and_cache_writes_cache_file(self, mock_urlopen, clean_cache):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(
            {"info": {"version": "99.0.0"}}
        ).encode("utf-8")
        mock_response.info.return_value.get_content_charset.return_value = "utf-8"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        _fetch_and_cache_latest_version()

        assert clean_cache.exists()
        cache_data = json.loads(clean_cache.read_text(encoding="utf-8"))
        assert cache_data["latest_version"] == "99.0.0"
        assert "timestamp" in cache_data

    @patch("urllib.request.urlopen")
    def test_handles_network_errors_gracefully(self, mock_urlopen, clean_cache, capsys):
        mock_urlopen.side_effect = Exception("Network error")

        _fetch_and_cache_latest_version()

        assert not clean_cache.exists()
        captured = capsys.readouterr()
        assert "new version" not in captured.out.lower()

    def test_read_version_cache_returns_none_for_missing_file(self):
        result = _read_version_cache()
        assert result is None

    def test_read_version_cache_returns_none_for_stale_cache(self, clean_cache):
        stale_time = time.time() - 86401
        cache_data = {"latest_version": "99.0.0", "timestamp": stale_time}
        clean_cache.parent.mkdir(parents=True, exist_ok=True)
        clean_cache.write_text(json.dumps(cache_data), encoding="utf-8")

        result = _read_version_cache()
        assert result is None
