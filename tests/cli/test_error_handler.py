from unittest.mock import patch

import pytest

from rendercv.cli.error_handler import handle_user_errors
from rendercv.exception import RenderCVUserError


class TestHandleUserErrors:
    def test_returns_value_when_no_exception(self):
        @handle_user_errors
        def successful_function():
            return None

        successful_function()

    @patch("rendercv.cli.error_handler.printer.error")
    def test_catches_user_error_and_prints_message(self, mock_error):
        @handle_user_errors
        def failing_function():
            raise RenderCVUserError("Something went wrong")

        failing_function()

        mock_error.assert_called_once_with("Something went wrong")

    def test_propagates_non_user_errors(self):
        @handle_user_errors
        def failing_function():
            raise ValueError("Unexpected error")

        with pytest.raises(ValueError, match="Unexpected error"):
            failing_function()
