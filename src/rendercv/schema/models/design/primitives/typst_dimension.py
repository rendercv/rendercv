"""Typst dimension validation (e.g., "1.5cm", "10pt")."""

import re
from typing import Annotated

import pydantic
import pydantic_core

from ....utils.custom_pydantic_error_types import CustomPydanticErrorTypes


def validate_typst_dimension(dimension: str) -> str:
    """Validate format: number + unit (cm, in, pt, mm, em, ex)."""
    if not re.fullmatch(r"\d+\.?\d*(cm|in|pt|mm|ex|em)", dimension):
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "The value must be a number followed by a unit (cm, in, pt, mm, ex, em)."
            " For example, 0.1cm. The provided value is `{dimension}`.",
            {"dimension": dimension},
        )
    return dimension


type TypstDimension = Annotated[str, pydantic.AfterValidator(validate_typst_dimension)]
