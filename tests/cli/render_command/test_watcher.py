import threading
import time
from unittest.mock import MagicMock, patch

import typer

from rendercv.cli.render_command import watcher


class TestRunFunctionIfFilesChange:
    def test_runs_function_immediately_on_start(self, tmp_path):
        file_path = tmp_path / "test.yaml"
        file_path.touch()
        mock_function = MagicMock()

        with (
            patch.object(watcher.watchdog.observers, "Observer"),
            patch.object(watcher.time, "sleep", side_effect=KeyboardInterrupt),
        ):
            watcher.run_function_if_files_change([file_path], mock_function)

        mock_function.assert_called_once()

    def test_reruns_function_when_file_is_modified(self, tmp_path):
        watched_file = tmp_path / "test.yaml"
        watched_file.write_text("initial", encoding="utf-8")

        call_count = 0

        def tracked_function():
            nonlocal call_count
            call_count += 1

        watcher_thread = threading.Thread(
            target=watcher.run_function_if_files_change,
            args=([watched_file], tracked_function),
            daemon=True,
        )
        watcher_thread.start()

        time.sleep(0.2)
        initial_count = call_count

        watched_file.write_text("first edit", encoding="utf-8")
        time.sleep(0.2)

        assert call_count > initial_count

    def test_reruns_function_when_secondary_file_is_modified(self, tmp_path):
        main_file = tmp_path / "cv.yaml"
        main_file.write_text("main content", encoding="utf-8")
        design_file = tmp_path / "design.yaml"
        design_file.write_text("initial design", encoding="utf-8")

        call_count = 0

        def tracked_function():
            nonlocal call_count
            call_count += 1

        watcher_thread = threading.Thread(
            target=watcher.run_function_if_files_change,
            args=([main_file, design_file], tracked_function),
            daemon=True,
        )
        watcher_thread.start()

        time.sleep(0.2)
        count_before_edit = call_count

        # Edit the design file (not the main file)
        design_file.write_text("updated design", encoding="utf-8")
        time.sleep(0.2)

        assert call_count > count_before_edit

    def test_continues_watching_after_typer_exit(self, tmp_path):
        watched_file = tmp_path / "test.yaml"
        watched_file.write_text("initial", encoding="utf-8")

        call_count = 0
        should_raise = False

        def tracked_function():
            nonlocal call_count
            call_count += 1
            if should_raise:
                raise typer.Exit(code=1)

        watcher_thread = threading.Thread(
            target=watcher.run_function_if_files_change,
            args=([watched_file], tracked_function),
            daemon=True,
        )
        watcher_thread.start()

        time.sleep(0.2)
        should_raise = True
        count_before_exit = call_count
        watched_file.write_text("edit that raises exit", encoding="utf-8")
        time.sleep(0.2)

        assert call_count > count_before_exit

        should_raise = False
        count_after_exit = call_count
        watched_file.write_text("edit after exit", encoding="utf-8")
        time.sleep(0.2)

        assert call_count > count_after_exit
