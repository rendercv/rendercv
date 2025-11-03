import re
from typing import Annotated

import pydantic
import pydantic_core


def validate_typst_dimension(dimension: str) -> str:
    """Check if the input string is a valid dimension for Typst.

    Args:
        dimension: The input string to be validated.

    Returns:
        The input string itself if it is a valid dimension.
    """
    if not re.fullmatch(r"\d+\.?\d*(cm|in|pt|mm|ex|em)", dimension):
        raise pydantic_core.PydanticCustomError(
            "rendercv_custom_error",
            "The value must be a number followed by a unit (cm, in, pt, mm, ex, em)."
            " For example, 0.1cm. The provided value is {dimension}.",
            {"dimension": dimension},
        )
    return dimension


type TypstDimension = Annotated[str, pydantic.AfterValidator(validate_typst_dimension)]
