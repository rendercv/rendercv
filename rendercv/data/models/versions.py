"""The `rendercv.models.versions` module contains the data model of the `versions`
field of the input file.
"""
  
import datetime
import pathlib
from typing import Optional

import pydantic

from .base import RenderCVBaseModelWithoutExtraKeys
from .computers import convert_string_to_path

DATE_INPUT = datetime.date.today()


class Versions(RenderCVBaseModelWithoutExtraKeys):
    """This class is the data model of the `versions` field. Between the include and exclude fields, one of them must be provided. If both are provided, the exclude field will take precedence over the include field."""
    
    name: str = pydantic.Field(
      ...,
      title="`name` Field",
      description="The name of the version."
    )
    
    include: Optional[list[str]] = pydantic.Field(
      default=None,
      title="`include` Field",
      description="The list of tags to include in the output."
    )
    
    exclude: Optional[list[str]] = pydantic.Field(
      default=None,
      title="`exclude` Field",
      description="The list of tags to exclude from the output."
    )