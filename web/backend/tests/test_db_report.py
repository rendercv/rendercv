"""Reading the connection string a person pasted.

Why this has tests at all, for a one-off operator script: getting a
connection string from Render's dashboard into a terminal went wrong four
times in a row, and twice the recovery leaked a password. Every case below
is one that actually happened.

The script is not a package, so it is loaded from its path.
"""

import importlib.util
import pathlib
import sys
from types import ModuleType

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "db_report.py"


def load_script() -> ModuleType:
    """Import `scripts/db_report.py` as a module.

    Returns:
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location("db_report", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["db_report"] = module
    spec.loader.exec_module(module)
    return module


db_report = load_script()

URL = "postgresql://user:secret@host.example.com/db"


class TestWhatPeopleActuallyPaste:
    """Every one of these was pasted at a real prompt."""

    def test_the_url_itself_is_returned_unchanged(self) -> None:
        assert db_report.clean_pasted_url(URL) == URL

    def test_surrounding_whitespace_is_dropped(self) -> None:
        # Copying from a dashboard often brings a trailing newline.
        assert db_report.clean_pasted_url(f"  {URL}\n") == URL

    def test_quotes_are_dropped(self) -> None:
        assert db_report.clean_pasted_url(f'"{URL}"') == URL
        assert db_report.clean_pasted_url(f"'{URL}'") == URL

    def test_the_psql_command_row_is_accepted(self) -> None:
        # Render shows "PSQL Command" directly under "External Database URL",
        # and it is the same string with `psql ` in front. Copying the wrong
        # row is a one-line mistake that used to produce a stack trace.
        assert db_report.clean_pasted_url(f"psql {URL}") == URL

    def test_postgres_scheme_is_left_for_the_engine_to_normalise(self) -> None:
        # `postgres://` is what some providers hand out and SQLAlchemy
        # rejects; the application's own engine builder rewrites it, so this
        # must not refuse it here.
        legacy = "postgres://user:secret@host.example.com/db"
        assert db_report.clean_pasted_url(legacy) == legacy


class TestTheEnvironmentVariable:
    """The other way in, which is also usually a paste."""

    def test_a_trailing_newline_from_the_clipboard_is_stripped(
        self, monkeypatch
    ) -> None:
        # PowerShell's `Get-Clipboard -Raw` keeps the trailing newline, and
        # setting the variable from it is the way round `getpass` not
        # receiving a paste on Windows. Untrimmed it reaches SQLAlchemy as a
        # malformed URL.
        monkeypatch.setenv(db_report.DATABASE_URL_ENV_VAR, URL + "\r\n")

        assert db_report.resolve_database_url() == URL

    def test_a_psql_prefix_in_the_variable_is_stripped_too(self, monkeypatch) -> None:
        monkeypatch.setenv(db_report.DATABASE_URL_ENV_VAR, f"psql {URL}")

        assert db_report.resolve_database_url() == URL


class TestWhatItRefuses:
    """Refusals have to say which row to copy instead."""

    def test_an_empty_paste_is_refused(self) -> None:
        with pytest.raises(SystemExit):
            db_report.clean_pasted_url("   \n")

    def test_a_bare_hostname_is_refused(self, capsys) -> None:
        # The `Hostname` row on Render's Info page. On its own it is not a
        # connection string, and the internal form does not resolve outside
        # Render at all.
        with pytest.raises(SystemExit):
            db_report.clean_pasted_url("dpg-daen9if40ujc73fumqn0-a")

        message = capsys.readouterr().err
        assert "External Database URL" in message

    def test_a_row_of_mask_dots_is_named_for_what_it_is(self, capsys) -> None:
        # Render renders its four connection fields as password inputs whose
        # on-screen contents are 110 bullet characters -- verified in the
        # live dashboard. Selecting the text and copying it therefore yields
        # the mask, and the generic "not a connection string" answer would
        # send the reader looking at the wrong row.
        with pytest.raises(SystemExit):
            db_report.clean_pasted_url("•" * 110)

        message = capsys.readouterr().err
        assert "copy button" in message

    def test_the_refusal_never_echoes_what_was_pasted(self, capsys) -> None:
        # The string carries the password. A diagnostic that prints it back
        # puts it in the scrollback, which is how one was leaked already.
        with pytest.raises(SystemExit):
            db_report.clean_pasted_url("totally-not-a-url-but-secret")

        output = capsys.readouterr()
        assert "totally-not-a-url-but-secret" not in output.err
        assert "totally-not-a-url-but-secret" not in output.out
