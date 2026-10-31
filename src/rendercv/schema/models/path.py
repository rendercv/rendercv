import atexit
import contextlib
import pathlib
import re
import shutil
import tempfile
import urllib.error
import urllib.parse
import urllib.request
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
            shown = (
                path.relative_to(relative_to)
                if path.is_relative_to(relative_to)
                else path
            )
            if not path.exists():
                raise pydantic_core.PydanticCustomError(
                    CustomPydanticErrorTypes.other.value,
                    "The file `{file_path}` does not exist.",
                    {"file_path": shown},
                )
            if not path.is_file():
                raise pydantic_core.PydanticCustomError(
                    CustomPydanticErrorTypes.other.value,
                    "The path `{path}` is not a file.",
                    {"path": shown},
                )

    return path


def serialize_path(path: pathlib.Path) -> str:
    with contextlib.suppress(ValueError):
        return path.relative_to(pathlib.Path.cwd()).as_posix()

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


# The beginnings of the image files that Typst can embed:
image_signatures = (
    re.compile(rb"\x89PNG\r\n\x1a\n"),
    re.compile(rb"\xff\xd8\xff"),  # JPEG
    re.compile(rb"GIF8[79]a"),
    re.compile(rb"RIFF.{4}WEBP", re.DOTALL),
    re.compile(rb"%PDF-"),
    # SVG is XML, whose root element may follow a declaration and comments:
    re.compile(rb"(?:\xef\xbb\xbf)?\s*(?:<[?!][^>]*>\s*)*<svg[\s>]"),
)


def validate_image(path: pathlib.Path) -> pathlib.Path:
    """Check that a file is an image that Typst can embed.

    Why:
        A photo is copied next to the Typst file and embedded in the CV. Checking
        signature gives a clear error for a wrong file. This identifies the format;
        it does not validate every byte or make an untrusted input safe to render.

    Args:
        path: Absolute path of an existing file.

    Returns:
        The path.
    """
    with path.open("rb") as file:
        beginning = file.read(4096)
    if not any(signature.match(beginning) for signature in image_signatures):
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "The file `{file_name}` is not a PNG, JPEG, GIF, WebP, SVG, or PDF image.",
            {"file_name": path.name},
        )
    return path


type ExistingImagePathRelativeToInput = Annotated[
    ExistingPathRelativeToInput, pydantic.AfterValidator(validate_image)
]


def resolve_photo(photo: pathlib.Path | pydantic.HttpUrl | None) -> pathlib.Path | None:
    """Download a remote photo and check its format during input validation.

    Downloads stay in a temporary directory until the process exits. Each validation
    fetches the URL again, so an old output file cannot substitute for a new photo.

    Args:
        photo: Validated local image path, HTTP URL, or no photo.

    Returns:
        A local image path, or None.

    Raises:
        ValueError: The URL could not be read or its response is not an image.
    """
    if not isinstance(photo, pydantic.HttpUrl):
        return photo
    directory = pathlib.Path(tempfile.mkdtemp(prefix="rendercv-photo-"))
    suffix = pathlib.PurePosixPath(urllib.parse.urlsplit(str(photo)).path).suffix
    path = directory / f"photo{suffix or '.img'}"
    try:
        with urllib.request.urlopen(str(photo), timeout=30) as response:
            path.write_bytes(response.read())
        validate_image(path)
    except (urllib.error.URLError, OSError) as error:
        shutil.rmtree(directory)
        message = f"Failed to download photo from {photo}: {error}"
        raise ValueError(message) from error
    except ValueError:
        shutil.rmtree(directory)
        raise
    atexit.register(shutil.rmtree, directory, True)
    return path
