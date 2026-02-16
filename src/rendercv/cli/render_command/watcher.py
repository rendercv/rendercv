import contextlib
import pathlib
import time
from collections.abc import Callable

import typer
import watchdog.events
import watchdog.observers


class EventHandler(watchdog.events.FileSystemEventHandler):
    """Trigger a callback when a watched file is modified.

    Args:
        function: Callback to invoke on modification.
        watched_files: Absolute path strings of files to monitor.
    """

    def __init__(self, function: Callable[[], None], watched_files: set[str]) -> None:
        super().__init__()
        self.function = function
        self.watched_files = watched_files

    def on_modified(
        self,
        event: watchdog.events.DirModifiedEvent | watchdog.events.FileModifiedEvent,
    ) -> None:
        if event.src_path not in self.watched_files:
            return
        with contextlib.suppress(typer.Exit):
            self.function()


def run_function_if_files_change(
    file_paths: list[pathlib.Path],
    function: Callable[[], None],
) -> None:
    """Watch files and re-run function when any is modified.

    Why:
        Watch mode lets users edit CV YAML and see results instantly.
        All config files (main input, design, locale, settings) must be
        monitored so edits to any trigger a re-render.

    Args:
        file_paths: File paths to watch.
        function: Zero-argument callback to invoke on file change.
    """
    watched_files = {str(fp.absolute()) for fp in file_paths}

    # Watch parent directories (file-level watching is unreliable across platforms)
    dirs_to_schedule = {str(fp.absolute().parent) for fp in file_paths}

    event_handler = EventHandler(function, watched_files)

    observer = watchdog.observers.Observer()
    for directory in dirs_to_schedule:
        observer.schedule(event_handler, directory, recursive=False)
    observer.start()

    # Run immediately for the first render:
    with contextlib.suppress(typer.Exit):
        function()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
