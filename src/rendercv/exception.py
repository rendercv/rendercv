from dataclasses import dataclass, field
from typing import TypedDict


class RenderCVValidationError(TypedDict):
    location: tuple[str, ...]
    yaml_location: tuple[tuple[int, int], tuple[int, int]]
    message: str
    input: str


@dataclass
class RenderCVUserError(Exception):
    message: str | None = field(default=None)


@dataclass
class RenderCVUserValidationError(Exception):
    validation_errors: list[RenderCVValidationError]


@dataclass
class RenderCVInternalError(Exception):
    message: str
