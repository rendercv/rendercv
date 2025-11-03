"""Validation context for resolving paths and dates during model validation."""

import pathlib
from dataclasses import dataclass
from datetime import date as Date
from typing import cast

import pydantic


@dataclass
class ValidationContext:
    """Context passed to validators for path resolution and date calculations."""

    input_file_path: pathlib.Path
    date_today: Date


def get_input_file_path(info: pydantic.ValidationInfo) -> pathlib.Path:
    """Get input file path from context, or cwd if not available."""
    if isinstance(info.context, dict):
        context = cast(ValidationContext, info.context["context"])
        return context.input_file_path
    return pathlib.Path.cwd()


def get_todays_date(info: pydantic.ValidationInfo) -> Date:
    """Get reference date from context, or actual today if not available."""
    if isinstance(info.context, dict):
        context = cast(ValidationContext, info.context["context"])
        return context.date_today
    return Date.today()
