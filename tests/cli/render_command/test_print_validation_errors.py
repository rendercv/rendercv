import pytest

from rendercv.cli.render_command.print_validation_errors import print_validation_errors
from rendercv.exception import RenderCVInternalError
from rendercv.schema.pydantic_error_handling import RenderCVValidationError


class TestPrintValidationErrors:
    def test_prints_validation_error_details(self, capsys):
        errors: list[RenderCVValidationError] = [
            {
                "location": ("cv", "name"),
                "yaml_location": ((1, 1), (1, 1)),
                "input": "123",
                "message": "Invalid name",
            }
        ]

        print_validation_errors(errors)

        captured = capsys.readouterr()
        assert "cv.name" in captured.out
        assert "123" in captured.out
        assert "Invalid name" in captured.out

    def test_raises_error_when_called_with_empty_list(self):
        with pytest.raises(RenderCVInternalError):
            print_validation_errors([])
