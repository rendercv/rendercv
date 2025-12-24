import contextlib
import pathlib
import sys
import time
from collections.abc import Callable

import typer
import watchdog.events
import watchdog.observers


def run_function_if_file_changes(
    file_paths: pathlib.Path | list[pathlib.Path],
    function: Callable,
):
    """Watch files and call the function when any of them is modified.

    Args:
        file_paths: Single file path or list of file paths to watch.
        function: The function to be called on file modification.
    """
    if isinstance(file_paths, pathlib.Path):
        file_paths = [file_paths]

    # Filter out None values and convert to absolute paths
    watched_files = {str(fp.absolute()) for fp in file_paths if fp is not None}

    if not watched_files:
        return

    # Determine directories to watch
    dirs_to_watch: set[str] = set()
    for file_path in file_paths:
        if file_path is None:
            continue
        if sys.platform == "win32":
            # Windows does not support single file watching, so we watch the directory
            dirs_to_watch.add(str(file_path.parent.absolute()))
        else:
            dirs_to_watch.add(str(file_path.absolute()))

    class EventHandler(watchdog.events.FileSystemEventHandler):
        def __init__(self, function: Callable, watched_files: set[str]):
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
                try:
                    self.function()
                except Exception as e:
                    # This means an unhandled error occurred in the function.
                    # Don't suppress it
                    raise e

    event_handler = EventHandler(function, watched_files)

    observer = watchdog.observers.Observer()
    for dir_path in dirs_to_watch:
        observer.schedule(event_handler, dir_path, recursive=True)
    observer.start()

    # Run the function immediately for the first time:
    first_file = next(iter(watched_files))
    event_handler.on_modified(watchdog.events.FileModifiedEvent(first_file))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
