import pathlib
from typing import Annotated

import pydantic
import pydantic_core

from ..pydantic_error_handling import CustomPydanticErrorTypes
from .validation_context import get_input_file_path

# Magic byte signatures for common image formats
# Format: (magic_bytes, offset, format_name)
IMAGE_SIGNATURES: list[tuple[bytes, int, str]] = [
    (b'\x89PNG\r\n\x1a\n', 0, 'PNG'),
    (b'\xff\xd8\xff', 0, 'JPEG'),
    (b'GIF87a', 0, 'GIF'),
    (b'GIF89a', 0, 'GIF'),
    (b'BM', 0, 'BMP'),
    (b'RIFF', 0, 'WebP'),  # WebP starts with RIFF, followed by file size, then WEBP
    (b'II*\x00', 0, 'TIFF'),  # Little-endian TIFF
    (b'MM\x00*', 0, 'TIFF'),  # Big-endian TIFF
]


def is_valid_image_file(path: pathlib.Path) -> bool:
    """Check if a file is a valid image by examining magic bytes.

    Why:
        Magic byte validation prevents arbitrary file access via photo fields.
        Checking file signatures is more reliable than extension-based checks
        and prevents attackers from referencing non-image files.

    Args:
        path: Path to the file to validate.

    Returns:
        True if the file has valid image magic bytes, False otherwise.
    """
    try:
        with path.open('rb') as f:
            # Read enough bytes to check all signatures (max 12 bytes needed for WebP)
            header = f.read(12)

        for magic, offset, _ in IMAGE_SIGNATURES:
            if header[offset:offset + len(magic)] == magic:
                # Special case for WebP: must also have 'WEBP' at offset 8
                if magic == b'RIFF' and header[8:12] != b'WEBP':
                    continue
                return True

        return False
    except (OSError, IOError):
        return False


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


def validate_image_path(
    path: pathlib.Path, info: pydantic.ValidationInfo
) -> pathlib.Path:
    """Validate that a path points to an existing image file.

    Why:
        Ensures photo fields reference actual image files, preventing
        arbitrary file access via crafted YAML inputs. Combines path
        resolution with image format validation.

    Args:
        path: Path to validate (may be relative or absolute).
        info: Validation context containing input file path.

    Returns:
        Resolved absolute path if valid image.

    Raises:
        PydanticCustomError: If path doesn't exist or isn't a valid image.
    """
    # First resolve the path and check existence
    resolved_path = resolve_relative_path(path, info, must_exist=True)

    # Then validate it's actually an image file
    if resolved_path and not is_valid_image_file(resolved_path):
        input_file_path = get_input_file_path(info)
        relative_to = input_file_path.parent if input_file_path else pathlib.Path.cwd()
        try:
            display_path = resolved_path.relative_to(relative_to)
        except ValueError:
            display_path = resolved_path
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "The file `{file_path}` is not a valid image file. "
            "Supported formats: PNG, JPEG, GIF, BMP, WebP, TIFF.",
            {"file_path": display_path},
        )

    return resolved_path


def serialize_path(path: pathlib.Path) -> str:
    return str(path.relative_to(pathlib.Path.cwd()))


type ExistingPathRelativeToInput = Annotated[
    pathlib.Path,
    pydantic.AfterValidator(
        lambda path, info: resolve_relative_path(path, info, must_exist=True)
    ),
]

type ExistingImagePathRelativeToInput = Annotated[
    pathlib.Path,
    pydantic.AfterValidator(validate_image_path),
]

type PlannedPathRelativeToInput = Annotated[
    pathlib.Path,
    pydantic.AfterValidator(
        lambda path, info: resolve_relative_path(path, info, must_exist=False)
    ),
    pydantic.PlainSerializer(serialize_path),
]
