import pathlib
from datetime import date as Date

import pydantic

from rendercv.schema.models.validation_context import (
    ValidationContext,
    get_current_date,
    get_input_file_path,
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
    def capture_current_date(cls, _value: str, info: pydantic.ValidationInfo) -> str:
        resolved_date = get_current_date(info)
        return resolved_date.isoformat()


class TestValidationContext:
    def test_provides_input_file_path_and_current_date(self):
        test_path = pathlib.Path("/test/input/file.yaml")
        context_date = Date(2008, 1, 15)
        context = ValidationContext(input_file_path=test_path, current_date=context_date)

        model = DummyModel.model_validate(
            {"name": "test", "path_field": "dummy", "date_field": "dummy"},
            context={"context": context},
        )

        assert model.path_field == str(test_path)
        assert model.date_field == context_date.isoformat()

    def test_uses_defaults_without_context(self):
        model = DummyModel.model_validate(
            {"name": "test", "path_field": "dummy", "date_field": "dummy"}
        )

        expected_date = Date.today()
        assert model.path_field == "None"
        assert model.date_field == expected_date.isoformat()
