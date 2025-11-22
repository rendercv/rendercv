from dataclasses import dataclass


@dataclass
class RenderCVCliUserError(Exception):
    message: str
