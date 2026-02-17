from dataclasses import dataclass, field
from typing import Literal

type YamlSource = Literal[
    "main_yaml_file",
    "design_yaml_file",
    "locale_yaml_file",
    "settings_yaml_file",
]
type OverlaySourceKey = Literal["design", "locale", "settings"]
type YamlLocation = tuple[tuple[int, int], tuple[int, int]]

OVERLAY_SOURCE_TO_YAML_SOURCE: dict[OverlaySourceKey, YamlSource] = {
    "design": "design_yaml_file",
    "locale": "locale_yaml_file",
    "settings": "settings_yaml_file",
}


@dataclass
class RenderCVValidationError:
    schema_location: tuple[str, ...] | None
    yaml_location: YamlLocation | None
    yaml_source: YamlSource
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
