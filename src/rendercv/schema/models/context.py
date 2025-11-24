import pathlib
from datetime import date as Date
from typing import cast

import pydantic


class ValidationContext(pydantic.BaseModel):
    input_file_path: pathlib.Path | None = None
    current_date: Date | None = None


def get_input_file_path(info: pydantic.ValidationInfo) -> pathlib.Path | None:
    if isinstance(info.context, dict):
        context = cast(ValidationContext, info.context["context"])
        if context.input_file_path:
            return context.input_file_path
    return None


def get_current_date(info: pydantic.ValidationInfo) -> Date:
    if isinstance(info.context, dict):
        context = cast(ValidationContext, info.context["context"])
        return context.current_date or Date.today()
    return Date.today()
