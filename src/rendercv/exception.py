from dataclasses import dataclass


@dataclass
class RenderCVUserError(Exception):
    message: str


@dataclass
class RenderCVInternalError(Exception):
    message: str
