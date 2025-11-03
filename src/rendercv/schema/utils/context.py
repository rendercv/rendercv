import pathlib
from dataclasses import dataclass


@dataclass
class ValidationContext:
    input_file_path: pathlib.Path
