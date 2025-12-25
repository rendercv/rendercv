import re
from typing import Annotated, TypeAlias

import pydantic
import pydantic_core

from ...pydantic_error_handling import CustomPydanticErrorTypes


def validate_typst_dimension(dimension: str) -> str:
    """Validate Typst dimension format with unit.

    Why:
        Typst requires dimensions with explicit units (e.g., 1cm, 0.5in).
        Validation prevents compilation errors from missing or invalid units.

    Args:
        dimension: Dimension string to validate.

    Returns:
        Original dimension if valid.
    """
    if not re.fullmatch(r"-?\d+(?:\.\d+)?(cm|in|pt|mm|ex|em)", dimension):
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "The value must be a number followed by a unit (cm, in, pt, mm, ex, em)."
            " For example, 0.1cm.",
        )
    return dimension


TypstDimension: TypeAlias = Annotated[
    str, pydantic.AfterValidator(validate_typst_dimension)
]
