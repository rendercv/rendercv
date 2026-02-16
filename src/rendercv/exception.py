from dataclasses import dataclass, field
from typing import Literal


@dataclass
class RenderCVValidationError:
    location: tuple[str, ...]
    yaml_location: tuple[tuple[int, int], tuple[int, int]] | None
    yaml_source: Literal["design", "locale", "settings"] | None
    message: str
    input: str


@dataclass
class RenderCVUserError(ValueError):
    message: str | None = field(default=None)


@dataclass
class RenderCVUserValidationError(ValueError):
    validation_errors: list[RenderCVValidationError]


@dataclass
class RenderCVInternalError(RuntimeError):
    message: str
