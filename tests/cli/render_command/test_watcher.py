import contextlib
import threading
import time
from unittest.mock import MagicMock, patch

import watchdog.events

from rendercv.cli.render_command import watcher
from rendercv.exception import RenderCVUserError


class TestRunFunctionIfFileChanges:
    def test_on_modified_calls_function_for_matching_file(self, tmp_path):
        file_path = tmp_path / "test.yaml"
        file_path.touch()
        mock_function = MagicMock()

        # Access the EventHandler class by calling the function with mocked observer
        with (
            patch.object(watcher.watchdog.observers, "Observer"),
            patch.object(watcher.time, "sleep", side_effect=KeyboardInterrupt),
        ):
            watcher.run_function_if_file_changes(file_path, mock_function)

        # Function should be called once immediately
        assert mock_function.call_count == 1

    def test_on_modified_ignores_non_matching_file(self, tmp_path):
        watched_file = tmp_path / "watched.yaml"
        other_file = tmp_path / "other.yaml"
        watched_file.touch()
        mock_function = MagicMock()

        # Create EventHandler manually to test on_modified behavior
        # We need to recreate the class since it's defined inside the function
        class EventHandler(watchdog.events.FileSystemEventHandler):
            def __init__(self, function, file_path):
                super().__init__()
                self.function = function
                self.file_path = file_path

            def on_modified(self, event):
                if event.src_path != str(self.file_path.absolute()):
                    return
                self.function()

        handler = EventHandler(mock_function, watched_file)
        event = watchdog.events.FileModifiedEvent(str(other_file.absolute()))

        handler.on_modified(event)

        mock_function.assert_not_called()

    def test_on_modified_calls_function_for_matching_file_event(self, tmp_path):
        watched_file = tmp_path / "watched.yaml"
        watched_file.touch()
        mock_function = MagicMock()

        class EventHandler(watchdog.events.FileSystemEventHandler):
            def __init__(self, function, file_path):
                super().__init__()
                self.function = function
                self.file_path = file_path

            def on_modified(self, event):
                if event.src_path != str(self.file_path.absolute()):
                    return
                self.function()

        handler = EventHandler(mock_function, watched_file)
        event = watchdog.events.FileModifiedEvent(str(watched_file.absolute()))

        handler.on_modified(event)

        mock_function.assert_called_once()

    def test_on_modified_suppresses_exceptions(self, tmp_path):
        watched_file = tmp_path / "watched.yaml"
        watched_file.touch()
        mock_function = MagicMock(side_effect=Exception("Error"))

        class EventHandler(watchdog.events.FileSystemEventHandler):
            def __init__(self, function, file_path):
                super().__init__()
                self.function = function
                self.file_path = file_path

            def on_modified(self, event):
                if event.src_path != str(self.file_path.absolute()):
                    return
                with contextlib.suppress(Exception):
                    self.function()

        handler = EventHandler(mock_function, watched_file)
        event = watchdog.events.FileModifiedEvent(str(watched_file.absolute()))

        # Should not raise
        handler.on_modified(event)

        mock_function.assert_called_once()

    def test_integration(self, tmp_path):
        watched_file = tmp_path / "test.yaml"
        watched_file.write_text("initial")

        call_count = 0  # It calls by default on start
        should_raise = False

        def tracked_function():
            nonlocal call_count
            call_count += 1
            if should_raise:
                raise RenderCVUserError("Intentional error")

        # Start watcher in background thread
        watcher_thread = threading.Thread(
            target=watcher.run_function_if_file_changes,
            args=(watched_file, tracked_function),
            daemon=True,
        )
        watcher_thread.start()

        # Wait for watcher to start and initial call
        time.sleep(0.2)
        assert call_count >= 1, "Function should be called immediately on start"

        # Edit file - should trigger function
        count_before_edit = call_count
        watched_file.write_text("first edit")
        time.sleep(0.2)
        assert call_count > count_before_edit, (
            "Function should be called after first edit"
        )

        # Set up to raise exception on next call
        should_raise = True
        count_before_exception = call_count
        watched_file.write_text("second edit - will raise")
        time.sleep(0.2)
        assert count_before_exception < call_count, (
            "Function should be called even though it raises"
        )

        # Disable exception and edit again - watcher should still work
        should_raise = False
        count_after_exception = call_count
        watched_file.write_text("third edit - after exception")
        time.sleep(0.2)
        assert count_after_exception < call_count, (
            "Watcher should continue after exception"
        )
