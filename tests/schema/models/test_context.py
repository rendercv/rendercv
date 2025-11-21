import pathlib
from datetime import date as Date

import pydantic

from rendercv.schema.models.context import (
    ValidationContext,
    get_input_file_path,
    get_todays_date,
)


class DummyModel(pydantic.BaseModel):
    name: str
    path_field: str
    date_field: str

    @pydantic.field_validator("path_field")
    @classmethod
    def capture_input_file_path(cls, _value: str, info: pydantic.ValidationInfo) -> str:
        resolved_path = get_input_file_path(info)
        return str(resolved_path)

    @pydantic.field_validator("date_field")
    @classmethod
    def capture_todays_date(cls, _value: str, info: pydantic.ValidationInfo) -> str:
        resolved_date = get_todays_date(info)
        return resolved_date.isoformat()


def test_model_validation_with_context():
    test_path = pathlib.Path("/test/input/file.yaml")
    context_date = Date(2008, 1, 15)
    context = ValidationContext(input_file_path=test_path, date_today=context_date)

    model = DummyModel.model_validate(
        {"name": "test", "path_field": "dummy", "date_field": "dummy"},
        context={"context": context},
    )

    assert model.path_field == str(test_path)
    assert model.date_field == context_date.isoformat()


def test_get_input_file_path_without_context():
    model = DummyModel.model_validate(
        {"name": "test", "path_field": "dummy", "date_field": "dummy"}
    )

    expected_path = pathlib.Path.cwd()
    expected_date = Date.today()
    assert model.path_field == str(expected_path)
    assert model.date_field == expected_date.isoformat()
