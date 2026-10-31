import pathlib

import pytest
from typer.testing import CliRunner

from rendercv import __version__
from rendercv.cli.app import app


def test_all_commands_are_registered():
    cli_folder = (
        pathlib.Path(__file__).parent.parent.parent / "src" / "rendercv" / "cli"
    )
    command_files = list(cli_folder.rglob("*_command.py"))

    registered_commands = app.registered_commands

    assert len(registered_commands) == len(command_files)


class TestCliCommandNoArgs:
    def test_prints_version_when_requested(self):
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert f"RenderCV v{__version__}" in result.output

    def test_prints_version_with_short_flag(self):
        runner = CliRunner()
        result = runner.invoke(app, ["-v"])

        assert result.exit_code == 0
        assert f"RenderCV v{__version__}" in result.output

    def test_shows_help_when_no_args(self):
        runner = CliRunner()
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "RenderCV is a command-line tool" in result.output


@pytest.mark.parametrize("quiet", ["--quiet", "-q"])
@pytest.mark.parametrize(
    ("command", "argument", "filename"),
    [
        ("new", "John Doe", "John_Doe_CV.yaml"),
        ("create-theme", "mytheme", "mytheme/__init__.py"),
    ],
)
def test_creation_commands_support_quiet(
    tmp_path, monkeypatch, quiet, command, argument, filename
):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, [command, argument, quiet])
    assert result.exit_code == 0, result.output
    assert result.output == ""
    assert (tmp_path / filename).is_file()


@pytest.mark.parametrize(
    ("command", "argument"), [("new", "John"), ("create-theme", "INVALID")]
)
def test_quiet_creation_errors(tmp_path, monkeypatch, command, argument):
    monkeypatch.chdir(tmp_path)
    args = [command, argument, "-q"]
    if command == "new":
        args.extend(["--theme", "INVALID"])
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 1
    assert result.output == ""


def test_quiet_policy_does_not_leak_to_the_next_invocation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    quiet = runner.invoke(app, ["new", "Quiet", "--quiet"])
    normal = runner.invoke(app, ["new", "Visible"])
    assert quiet.exit_code == normal.exit_code == 0
    assert quiet.output == ""
    assert "Visible" in normal.output
