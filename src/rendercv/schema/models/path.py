import pathlib
from typing import Annotated

import pydantic
import pydantic_core

from ..pydantic_error_handling import CustomPydanticErrorTypes
from .context import get_input_file_path


def resolve_relative_path(
    path: pathlib.Path, info: pydantic.ValidationInfo, must_exist: bool = True
) -> pathlib.Path:
    if path:
        if not path.is_absolute():
            input_file_path = get_input_file_path(info)
            path = input_file_path.parent / path

        if must_exist and not path.exists():
            raise pydantic_core.PydanticCustomError(
                CustomPydanticErrorTypes.other.value,
                "The photo file `{photo_file}` does not exist.",
                {"photo_file": path.absolute()},
            )

    return path


type ExistingInputRelativePath = Annotated[
    pathlib.Path,
    pydantic.AfterValidator(lambda path, info: resolve_relative_path(path, info, True)),
]

type PlannedInputRelativePath = Annotated[
    pathlib.Path,
    pydantic.AfterValidator(
        lambda path, info: resolve_relative_path(path, info, False)
    ),
]
