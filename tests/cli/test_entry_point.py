from unittest.mock import patch

import pytest

from rendercv.cli.entry_point import entry_point


def test_entry_point_runs_when_installed_correctly():
    with patch("rendercv.cli.app.app") as cli_app:
        entry_point()
        cli_app.assert_called_once()


def test_missing_optional_dependency(capsys):
    with (
        patch(
            "rendercv.cli.entry_point.importlib.import_module",
            side_effect=ModuleNotFoundError(name="typst"),
        ),
        pytest.raises(SystemExit) as error,
    ):
        entry_point()
    assert error.value.code == 1
    assert 'pip install "rendercv[full]"' in capsys.readouterr().err


@pytest.mark.parametrize(
    "error",
    [
        ImportError("broken import"),
        ModuleNotFoundError(name="rendercv.bug"),
        ModuleNotFoundError(name="rich.bug"),
    ],
)
def test_unexpected_import_errors_propagate(error, capsys):
    with (
        patch("rendercv.cli.entry_point.importlib.import_module", side_effect=error),
        pytest.raises(type(error)) as raised,
    ):
        entry_point()
    assert raised.value is error
    assert capsys.readouterr().err == ""
