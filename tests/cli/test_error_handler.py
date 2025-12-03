import pytest
import typer

from rendercv.cli.error_handler import handle_user_errors
from rendercv.exception import RenderCVUserError


class TestHandleUserErrors:
    def test_returns_function_result_on_success(self):
        @handle_user_errors
        def successful_function():
            return None

        successful_function()

    def test_catches_user_errors_and_prints_message(self):
        @handle_user_errors
        def failing_function():
            raise RenderCVUserError("Something went wrong")

        with pytest.raises(typer.Exit):
            failing_function()

    def test_propagates_non_user_errors(self):
        @handle_user_errors
        def failing_function():
            raise ValueError("Unexpected error")

        with pytest.raises(ValueError, match="Unexpected error"):
            failing_function()
