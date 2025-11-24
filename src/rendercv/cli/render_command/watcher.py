import contextlib
import pathlib
import sys
import time
from collections.abc import Callable

import watchdog.events
import watchdog.observers

from rendercv.exception import RenderCVUserError


def run_function_if_file_changes(file_path: pathlib.Path, function: Callable):
    """Watch the file located at `file_path` and call the `function` when the file is
    modified. The function should not take any arguments.

    Args:
        file_path (pathlib.Path): The path of the file to watch for.
        function (Callable): The function to be called on file modification.
    """
    path_to_watch = str(file_path.absolute())
    if sys.platform == "win32":
        # Windows does not support single file watching, so we watch the directory
        path_to_watch = str(file_path.parent.absolute())

    class EventHandler(watchdog.events.FileSystemEventHandler):
        def __init__(self, function: Callable):
            super().__init__()
            self.function = function

        def on_modified(self, event: watchdog.events.FileModifiedEvent) -> None:
            if event.src_path != str(file_path.absolute()):
                return

            with contextlib.suppress(RenderCVUserError):
                # Exceptions in the watchdog event handler thread should not
                # crash the application. They are already handled by the
                # decorated function, but we add this defensive check to ensure
                # the watcher continues running even if an unexpected exception
                # occurs in a background thread.
                self.function()

    event_handler = EventHandler(function)

    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()
    # Run the function immediately for the first time:
    event_handler.on_modified(
        watchdog.events.FileModifiedEvent(str(file_path.absolute()))
    )
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
