import pathlib

from rendercv.cli.app import app


def test_all_commands_are_registered():
    cli_folder = pathlib.Path(__file__).parent.parent.parent / "src" / "rendercv" / "cli"
    command_files = list(cli_folder.rglob("*_command.py"))

    registered_commands = app.registered_commands

    assert len(registered_commands) == len(command_files)
