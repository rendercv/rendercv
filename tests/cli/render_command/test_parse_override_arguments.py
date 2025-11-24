from unittest.mock import MagicMock

import pytest

from rendercv.cli.render_command.parse_override_arguments import (
    parse_override_arguments,
)
from rendercv.exception import RenderCVUserError


class TestParseOverrideArguments:
    @pytest.mark.parametrize(
        ("args", "expected"),
        [
            (["--cv.name", "John"], {"cv.name": "John"}),
            (
                ["--cv.name", "John", "--cv.email", "john@example.com"],
                {"cv.name": "John", "cv.email": "john@example.com"},
            ),
            ([], {}),
        ],
    )
    def test_parses_valid_arguments(self, args, expected):
        context = MagicMock()
        context.args = args

        result = parse_override_arguments(context)

        assert result == expected

    def test_errors_on_odd_number_of_arguments(self):
        context = MagicMock()
        context.args = ["--cv.name"]

        with pytest.raises(RenderCVUserError):
            parse_override_arguments(context)

    def test_errors_when_key_missing_dashes(self):
        context = MagicMock()
        context.args = ["cv.name", "John"]

        with pytest.raises(RenderCVUserError):
            parse_override_arguments(context)
