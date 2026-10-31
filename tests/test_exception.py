import pytest

from rendercv.exception import (
    RenderCVInternalError,
    RenderCVUserError,
    RenderCVUserValidationError,
    RenderCVValidationError,
)


@pytest.mark.parametrize("error_type", [RenderCVUserError, RenderCVInternalError])
@pytest.mark.parametrize("keyword", [False, True])
def test_exception_message(error_type, keyword):
    error = error_type(message="message") if keyword else error_type("message")
    assert str(error) == "message"
    assert error.args == ("message",)


def test_validation_exception_message():
    errors = [RenderCVValidationError(None, None, "main_yaml_file", "Bad YAML", "...")]
    error = RenderCVUserValidationError(validation_errors=errors)
    assert error.validation_errors is errors
    assert error.args == ("Bad YAML",)
    assert str(error) == "Bad YAML"
