from dataclasses import dataclass


@dataclass
class RenderCVUserError(Exception):
    message: str
