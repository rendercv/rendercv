"""
The `rendercv.data.models.base` module contains the parent classes of all the data
models in RenderCV.
"""

from typing import Any

import pydantic


def convert_empty_strings_to_none(data: Any) -> Any:
    """Convert all empty string values to None in a dictionary."""
    if isinstance(data, dict):
        return {
            key: None if value == "" else value
            for key, value in data.items()
        }
    return data


class RenderCVBaseModelWithoutExtraKeys(pydantic.BaseModel):
    """This class is the parent class of the data models that do not allow extra keys.
    It has only one difference from the default `pydantic.BaseModel`: It raises an error
    if an unknown key is provided in the input file.
    """

    model_config = pydantic.ConfigDict(extra="forbid", validate_default=True)

    @pydantic.model_validator(mode="before")
    @classmethod
    def empty_strings_to_none(cls, data: Any) -> Any:
        return convert_empty_strings_to_none(data)


class RenderCVBaseModelWithExtraKeys(pydantic.BaseModel):
    """This class is the parent class of the data models that allow extra keys. It has
    only one difference from the default `pydantic.BaseModel`: It allows extra keys in
    the input file.
    """

    model_config = pydantic.ConfigDict(extra="allow", validate_default=True)

    @pydantic.model_validator(mode="before")
    @classmethod
    def empty_strings_to_none(cls, data: Any) -> Any:
        return convert_empty_strings_to_none(data)
