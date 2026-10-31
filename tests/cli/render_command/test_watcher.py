import pathlib
import threading
from unittest.mock import MagicMock, patch

import pytest
import typer
import watchdog.events
import watchdog.observers

from rendercv.cli.render_command import watcher
from rendercv.cli.render_command.watcher import EventHandler


def test_refreshes_dependencies_and_stops_observer(tmp_path):
    first = tmp_path / "cv.yaml"
    second = tmp_path / "other" / "design.yaml"
    second.parent.mkdir()
    paths = [first]
    observer = MagicMock()
    observer.join.side_effect = [KeyboardInterrupt, None]

    def render():
        paths.append(second)
        return False  # An unsuccessful render does not stop watching.

    with patch.object(watcher.watchdog.observers, "Observer", return_value=observer):
        watcher.run_function_if_files_change(lambda: paths, render)
    assert {call.args[1] for call in observer.schedule.call_args_list} == {
        str(first.parent),
        str(second.parent),
    }
    handler = observer.schedule.call_args.args[0]
    assert handler.watched_files == {str(first), str(second)}
    observer.stop.assert_called_once()


def test_watches_the_closest_existing_folder_of_a_missing_one(tmp_path):
    # A design file referenced before its folder is created:
    design = tmp_path / "designs" / "design.yaml"
    observer = MagicMock()
    observer.join.side_effect = [KeyboardInterrupt, None]

    with patch.object(watcher.watchdog.observers, "Observer", return_value=observer):
        watcher.run_function_if_files_change(lambda: [design], lambda: False)

    observer.schedule.assert_called_once()
    assert observer.schedule.call_args.args[1] == str(tmp_path)


def test_rerenders_after_real_file_changes(tmp_path):
    watched = tmp_path / "test.yaml"
    watched.write_text("initial", encoding="utf-8")
    rendered = threading.Event()
    observer = watchdog.observers.Observer()
    started = threading.Event()
    original_start = observer.start

    def start():
        original_start()
        started.set()

    thread = threading.Thread(
        target=watcher.run_function_if_files_change,
        args=(lambda: [watched], rendered.set),
    )
    with (
        patch.object(watcher.watchdog.observers, "Observer", return_value=observer),
        patch.object(observer, "start", side_effect=start),
    ):
        thread.start()
        try:
            assert rendered.wait(5)
            assert started.wait(5)
            rendered.clear()
            watched.write_text("changed", encoding="utf-8")
            assert rendered.wait(5)
        finally:
            observer.stop()
            thread.join(5)
    assert not thread.is_alive()


@pytest.mark.parametrize(
    "event",
    [
        watchdog.events.FileModifiedEvent("/watched/file.yaml"),
        watchdog.events.FileCreatedEvent("/watched/file.yaml"),
        watchdog.events.FileDeletedEvent("/watched/file.yaml"),
        watchdog.events.DirCreatedEvent("/watched"),
        watchdog.events.FileMovedEvent("/temp/file.yaml", "/watched/file.yaml"),
    ],
)
def test_calls_function_for_changes(event):
    callback = MagicMock()
    handler = EventHandler(callback, {"/watched/file.yaml"})
    handler.dispatch(event)
    callback.assert_called_once()


@pytest.mark.parametrize(
    "event",
    [
        watchdog.events.FileModifiedEvent("/other/file.yaml"),
        watchdog.events.FileOpenedEvent("/watched/file.yaml"),
        watchdog.events.DirModifiedEvent("/watched/file.yaml"),
    ],
)
def test_ignores_unrelated_events(event):
    callback = MagicMock()
    EventHandler(callback, {"/watched/file.yaml"}).dispatch(event)
    callback.assert_not_called()


def test_does_not_suppress_process_exits():
    callback = MagicMock(side_effect=typer.Exit(code=1))
    handler = EventHandler(callback, {"/watched/file.yaml"})
    with pytest.raises(typer.Exit):
        handler.dispatch(watchdog.events.FileModifiedEvent("/watched/file.yaml"))


def test_unexpected_startup_errors_stop_observer(tmp_path: pathlib.Path):
    observer = MagicMock()
    with (
        patch.object(watcher.watchdog.observers, "Observer", return_value=observer),
        pytest.raises(RuntimeError, match="bug"),
    ):
        watcher.run_function_if_files_change(
            lambda: [tmp_path / "cv.yaml"], MagicMock(side_effect=RuntimeError("bug"))
        )
    observer.stop.assert_called_once()
