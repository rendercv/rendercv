from typing import Annotated

import pydantic
import pytest

from rendercv.schema.models.custom_error_types import invalid_input
from rendercv.schema.models.cv.entries.bases.entry_with_complex_fields import (
    BaseEntryWithComplexFields,
)
from rendercv.schema.models.settings.settings import Settings


@pytest.mark.parametrize(
    ("model", "field", "code", "hint"),
    [
        (Settings, "current_date", "rendercv_current_date", '"today"'),
        (BaseEntryWithComplexFields, "end_date", "rendercv_end_date", '"present"'),
    ],
)
def test_semantic_errors_follow_types_when_fields_are_renamed(model, field, code, hint):
    info = model.model_fields[field]
    renamed = pydantic.create_model("Renamed", unrelated_name=(info.annotation, info))
    with pytest.raises(pydantic.ValidationError) as exc:
        renamed.model_validate({"unrelated_name": "invalid"})
    assert len(exc.value.errors()) == 1
    error = exc.value.errors()[0]
    assert error["loc"] == ("unrelated_name",)
    assert error["type"] == code
    assert hint in error["msg"]


def test_custom_error_metadata_preserves_validation_and_json_schema():
    adapter = pydantic.TypeAdapter(
        Annotated[int, invalid_input("domain_integer", "An integer is required.")]
    )
    assert adapter.validate_python("12") == 12
    assert adapter.json_schema() == {"type": "integer"}
    with pytest.raises(pydantic.ValidationError) as exc:
        adapter.validate_python("no")
    assert exc.value.errors()[0]["type"] == "domain_integer"
