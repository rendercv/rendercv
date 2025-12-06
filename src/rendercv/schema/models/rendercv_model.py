import pathlib

import pydantic

from .base import BaseModelWithExtraKeys
from .validation_context import get_input_file_path
from .cv.cv import Cv
from .design.classic_theme import ClassicTheme
from .design.design import Design
from .locale.locale import EnglishLocale, Locale
from .settings.settings import Settings


class RenderCVModel(BaseModelWithExtraKeys):
    # Technically, `cv` is a required field, but we don't pass it to the JSON Schema
    # so that the same schema can be used for standalone design, locale, and settings
    # files.
    model_config = pydantic.ConfigDict(json_schema_extra={"required": []})
    cv: Cv = pydantic.Field(
        title="CV",
        description="The content of the CV.",
    )
    design: Design = pydantic.Field(
        default_factory=ClassicTheme,
        title="Design",
        description=(
            "The design information of the CV. The default is the `classic` theme."
        ),
    )
    locale: Locale = pydantic.Field(
        default_factory=EnglishLocale,
        title="Locale Catalog",
        description=(
            "The locale catalog of the CV to allow the support of multiple languages."
        ),
    )
    settings: Settings = pydantic.Field(
        default_factory=Settings,
        title="RenderCV Settings",
        description="The settings of the RenderCV.",
    )

    _input_file_path: pathlib.Path | None = pydantic.PrivateAttr(default=None)

    @pydantic.model_validator(mode="after")
    def set_input_file_path(self, info: pydantic.ValidationInfo) -> "RenderCVModel":
        """Store input file path in private attribute for path resolution.

        Why:
            Photo paths and other relative references need input file location
            for resolution. Private attribute stores this after validation for
            downstream processing.

        Args:
            info: Validation context containing input file path.

        Returns:
            Model instance with _input_file_path set.
        """
        self._input_file_path = get_input_file_path(info)
        return self
