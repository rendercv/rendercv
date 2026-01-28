import importlib
import sys
from unittest.mock import patch

import pytest

from rendercv.cli import entry_point as entry_point_module
from rendercv.cli.entry_point import entry_point


class TestEntryPoint:
    """Test the CLI entry point that handles incorrect installation."""

    def test_entry_point_runs_when_installed_correctly(self):
        # Mock the CLI app to avoid actually running it
        with patch("rendercv.cli.app.app") as mock_cli_app:
            entry_point()
            mock_cli_app.assert_called_once()

    def test_entry_point_shows_error_when_import_fails(self, capsys):
        # Save the original module if it exists
        app_module = sys.modules.get("rendercv.cli.app")

        try:
            # Remove the app module from sys.modules so the import happens fresh
            if "rendercv.cli.app" in sys.modules:
                del sys.modules["rendercv.cli.app"]

            # Mock the import to fail and call entry_point
            with patch.dict("sys.modules", {"rendercv.cli.app": None}):
                # Reload entry_point module and call it
                importlib.reload(entry_point_module)
                with pytest.raises(SystemExit) as exc_info:
                    entry_point_module.entry_point()

            # Verify it exits with code 1
            assert exc_info.value.code == 1

            # Verify the error message
            captured = capsys.readouterr()
            assert "pip install rendercv" in captured.err
            assert 'pip install "rendercv[full]"' in captured.err
            assert "reinstall" in captured.err

        finally:
            # Restore the original module
            if app_module is not None:
                sys.modules["rendercv.cli.app"] = app_module
            # Reload entry_point to restore it to normal
            importlib.reload(entry_point_module)
