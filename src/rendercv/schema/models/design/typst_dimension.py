import re
from typing import Annotated

import pydantic
import pydantic_core

from ...pydantic_error_handling import CustomPydanticErrorTypes


def validate_typst_dimension(dimension: str) -> str:
    if not re.fullmatch(r"-?\d+(?:\.\d+)?(cm|in|pt|mm|ex|em)", dimension):
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "The value must be a number followed by a unit (cm, in, pt, mm, ex, em)."
            " For example, 0.1cm.",
        )
    return dimension


type TypstDimension = Annotated[str, pydantic.AfterValidator(validate_typst_dimension)]
