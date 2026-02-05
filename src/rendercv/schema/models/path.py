import contextlib
import pathlib
from typing import Annotated

import pydantic
import pydantic_core

from ..pydantic_error_handling import CustomPydanticErrorTypes
from .validation_context import get_input_file_path


def resolve_relative_path(
    path: pathlib.Path, info: pydantic.ValidationInfo, *, must_exist: bool = True
) -> pathlib.Path:
    """Convert relative path to absolute path based on input file location.

    Why:
        Users reference files like `photo: profile.jpg` relative to their CV
        YAML. This validator resolves such paths to absolute form and validates
        existence, enabling file access during rendering.

    Example:
        ```py
        # In validators: photo_path = resolve_relative_path(photo, info)
        # Input: "photo.jpg" in /home/user/cv.yaml
        # Output: /home/user/photo.jpg (absolute, validated to exist)
        ```

    Args:
        path: Path to resolve (may be relative or absolute).
        info: Validation context containing input file path.
        must_exist: Whether to raise error if path doesn't exist.

    Returns:
        Absolute path.
    """
    if path:
        input_file_path = get_input_file_path(info)
        relative_to = input_file_path.parent if input_file_path else pathlib.Path.cwd()
        if not path.is_absolute():
            path = relative_to / path

        if must_exist:
            if not path.exists():
                raise pydantic_core.PydanticCustomError(
                    CustomPydanticErrorTypes.other.value,
                    "The file `{file_path}` does not exist.",
                    {"file_path": path.relative_to(relative_to)},
                )
            if not path.is_file():
                raise pydantic_core.PydanticCustomError(
                    CustomPydanticErrorTypes.other.value,
                    "The path `{path}` is not a file.",
                    {"path": path.relative_to(relative_to)},
                )

    return path


def serialize_path(path: pathlib.Path) -> str:
    with contextlib.suppress(ValueError):
        return str(path.relative_to(pathlib.Path.cwd()))

    return str(path)


type ExistingPathRelativeToInput = Annotated[
    pathlib.Path,
    pydantic.AfterValidator(
        lambda path, info: resolve_relative_path(path, info, must_exist=True)
    ),
]

type PlannedPathRelativeToInput = Annotated[
    pathlib.Path,
    pydantic.AfterValidator(
        lambda path, info: resolve_relative_path(path, info, must_exist=False)
    ),
    pydantic.PlainSerializer(serialize_path),
]
