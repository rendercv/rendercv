import os
import pathlib
import threading
from collections.abc import Callable

import watchdog.events
import watchdog.observers


class EventHandler(watchdog.events.FileSystemEventHandler):
    """Trigger a callback for edits, creation, deletion, and atomic saves.

    Args:
        function: Callback to invoke on changes.
        watched_files: Absolute path strings of files to monitor.
    """

    def __init__(self, function: Callable[[], object], watched_files: set[str]) -> None:
        super().__init__()
        self.function = function
        self.watched_files = {
            str(pathlib.Path(path).resolve()) for path in watched_files
        }

    def on_any_event(self, event: watchdog.events.FileSystemEvent) -> None:
        if event.event_type not in {
            "modified",
            "created",
            "deleted",
            "moved",
        }:
            return
        paths = {
            str(pathlib.Path(os.fsdecode(path)).resolve())
            for path in (event.src_path, event.dest_path)
            if path
        }
        if event.is_directory:
            relevant = event.event_type != "modified" and any(
                pathlib.Path(watched).is_relative_to(path)
                for watched in self.watched_files
                for path in paths
            )
        else:
            relevant = bool(paths & self.watched_files)
        if relevant:
            self.function()


def run_function_if_files_change(
    file_paths: Callable[[], list[pathlib.Path]],
    function: Callable[[], object],
) -> None:
    """Watch current dependencies and re-run a callback when they change.

    Why:
        References can change during editing. Refreshing subscriptions after each
        render also lets watch mode recover when missing input files are created.
        Render failures are callback results, never process exits to suppress.

    Args:
        file_paths: Callback discovering the current input paths.
        function: Callback to invoke on file changes and once on startup.
    """
    observer = watchdog.observers.Observer()
    scheduled: set[pathlib.Path] = set()
    lock = threading.Lock()

    def refresh_watches() -> None:
        paths = file_paths()
        event_handler.watched_files = {str(path.resolve()) for path in paths}
        for path in paths:
            directory = path.resolve().parent
            # Watching a missing folder is an error on Linux, so a file in a folder
            # that doesn't exist yet is watched through its closest existing parent:
            while not directory.is_dir():
                directory = directory.parent
            if directory not in scheduled:
                observer.schedule(event_handler, str(directory), recursive=False)
                scheduled.add(directory)

    def render_and_refresh() -> None:
        with lock:
            function()
            refresh_watches()

    event_handler = EventHandler(render_and_refresh, set())
    refresh_watches()
    try:
        render_and_refresh()
        observer.start()
        observer.join()
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        if observer.is_alive():
            observer.join()
