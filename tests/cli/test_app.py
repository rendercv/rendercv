import json
import pathlib
import sys
import time
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from rendercv import __version__
from rendercv.cli.app import (
    VERSION_CHECK_TTL_SECONDS,
    app,
    get_cache_dir,
    read_version_cache,
    warn_if_new_version_is_available,
    write_version_cache,
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


class TestGetCacheDir:
    def test_returns_platform_appropriate_path(self):
        cache_dir = get_cache_dir()

        assert cache_dir.name == "rendercv"
        if sys.platform == "darwin":
            assert "Library/Caches" in str(cache_dir)
        elif sys.platform == "win32":
            assert "Local" in str(cache_dir)

    def test_respects_xdg_cache_home_on_linux(self, tmp_path, monkeypatch):
        monkeypatch.setattr("rendercv.cli.app.sys.platform", "linux")
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))

        assert get_cache_dir() == tmp_path / "rendercv"


class TestReadVersionCache:
    def test_returns_none_for_missing_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rendercv.cli.app.get_version_cache_file",
            lambda: tmp_path / "nonexistent.json",
        )

        assert read_version_cache() is None

    def test_returns_none_for_corrupt_file(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "version_check.json"
        cache_file.write_text("not valid json!!!", encoding="utf-8")
        monkeypatch.setattr(
            "rendercv.cli.app.get_version_cache_file",
            lambda: cache_file,
        )

        assert read_version_cache() is None

    def test_returns_none_for_incomplete_data(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "version_check.json"
        cache_file.write_text(json.dumps({"latest_version": "1.0"}), encoding="utf-8")
        monkeypatch.setattr(
            "rendercv.cli.app.get_version_cache_file",
            lambda: cache_file,
        )

        assert read_version_cache() is None

    def test_returns_data_for_valid_cache(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "version_check.json"
        cache_data = {"last_check": time.time(), "latest_version": "2.0.0"}
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")
        monkeypatch.setattr(
            "rendercv.cli.app.get_version_cache_file",
            lambda: cache_file,
        )

        result = read_version_cache()

        assert result is not None
        assert result["latest_version"] == "2.0.0"


class TestWriteVersionCache:
    def test_creates_cache_file(self, tmp_path, monkeypatch):
        cache_file = tmp_path / "subdir" / "version_check.json"
        monkeypatch.setattr(
            "rendercv.cli.app.get_version_cache_file",
            lambda: cache_file,
        )

        write_version_cache("2.0.0")

        data = json.loads(cache_file.read_text(encoding="utf-8"))
        assert data["latest_version"] == "2.0.0"
        assert "last_check" in data


def write_cache(tmp_path, version, age_seconds=0):
    """Helper to write a version cache file for testing."""
    cache_file = tmp_path / "version_check.json"
    cache_file.write_text(
        json.dumps(
            {
                "last_check": time.time() - age_seconds,
                "latest_version": version,
            }
        ),
        encoding="utf-8",
    )
    return cache_file


class TestWarnIfNewVersionIsAvailable:
    @pytest.mark.parametrize(
        ("version", "should_warn"),
        [
            ("99.0.0", True),
            ("0.0.1", False),
            (__version__, False),
        ],
    )
    def test_warns_from_fresh_cache(
        self, version, should_warn, tmp_path, capsys, monkeypatch
    ):
        write_cache(tmp_path, version, age_seconds=0)
        monkeypatch.setattr(
            "rendercv.cli.app.get_version_cache_file",
            lambda: tmp_path / "version_check.json",
        )

        warn_if_new_version_is_available()

        captured = capsys.readouterr()
        if should_warn:
            assert "new version" in captured.out.lower()
        else:
            assert "new version" not in captured.out.lower()

    @patch("rendercv.cli.app.fetch_latest_version_from_pypi")
    def test_fresh_cache_does_not_fetch(self, mock_fetch, tmp_path, monkeypatch):
        write_cache(tmp_path, "99.0.0", age_seconds=0)
        monkeypatch.setattr(
            "rendercv.cli.app.get_version_cache_file",
            lambda: tmp_path / "version_check.json",
        )

        warn_if_new_version_is_available()

        mock_fetch.assert_not_called()

    @patch("rendercv.cli.app.fetch_latest_version_from_pypi", return_value="99.0.0")
    def test_stale_cache_warns_from_stale_data_and_refreshes(
        self, mock_fetch, tmp_path, capsys, monkeypatch
    ):
        write_cache(tmp_path, "98.0.0", age_seconds=VERSION_CHECK_TTL_SECONDS + 1)
        monkeypatch.setattr(
            "rendercv.cli.app.get_version_cache_file",
            lambda: tmp_path / "version_check.json",
        )

        warn_if_new_version_is_available()

        captured = capsys.readouterr()
        assert "new version" in captured.out.lower()
        mock_fetch.assert_called_once()

    @patch("rendercv.cli.app.fetch_latest_version_from_pypi", return_value="99.0.0")
    def test_missing_cache_shows_no_warning_and_refreshes(
        self,
        mock_fetch,
        tmp_path,
        capsys,
        monkeypatch,
    ):
        monkeypatch.setattr(
            "rendercv.cli.app.get_version_cache_file",
            lambda: tmp_path / "version_check.json",
        )

        warn_if_new_version_is_available()

        captured = capsys.readouterr()
        assert "new version" not in captured.out.lower()
        mock_fetch.assert_called_once()

    @patch("rendercv.cli.app.fetch_latest_version_from_pypi", return_value=None)
    def test_network_failure_preserves_existing_cache(
        self,
        mock_fetch,  # NOQA: ARG002
        tmp_path,
        monkeypatch,
    ):
        write_cache(tmp_path, "99.0.0", age_seconds=VERSION_CHECK_TTL_SECONDS + 1)
        cache_file = tmp_path / "version_check.json"
        monkeypatch.setattr(
            "rendercv.cli.app.get_version_cache_file",
            lambda: cache_file,
        )

        warn_if_new_version_is_available()

        data = json.loads(cache_file.read_text(encoding="utf-8"))
        assert data["latest_version"] == "99.0.0"
