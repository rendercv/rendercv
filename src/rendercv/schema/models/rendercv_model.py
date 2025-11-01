import pydantic

from ...themes import ClassicThemeOptions
from .base import BaseModelWithoutExtraKeys
from .cv.cv import Cv
from .design.design import Design
from .locale.locale import Locale
from .rendercv_settings.rendercv_settings import RenderCVSettings


class RenderCVModel(BaseModelWithoutExtraKeys):
    model_config = pydantic.ConfigDict(json_schema_extra={"required": []})
    cv: Cv = pydantic.Field(
        title="CV",
        description="The content of the CV.",
    )
    design: Design = pydantic.Field(
        default=ClassicThemeOptions(theme="classic"),
        title="Design",
        description=(
            "The design information of the CV. The default is the `classic` theme."
        ),
    )
    locale: Locale = pydantic.Field(
        default=Locale(),
        title="Locale Catalog",
        description=(
            "The locale catalog of the CV to allow the support of multiple languages."
        ),
    )
    rendercv_settings: RenderCVSettings = pydantic.Field(
        default=RenderCVSettings(),
        title="RenderCV Settings",
        description="The settings of the RenderCV.",
    )

    @pydantic.model_validator(mode="before")
    @classmethod
    def update_paths(
        cls, model, info: pydantic.ValidationInfo
    ) -> RenderCVSettings | None:
        """Update the paths in the RenderCV settings."""
        global INPUT_FILE_DIRECTORY  # NOQA: PLW0603

        context = info.context
        if context:
            input_file_directory = context.get("input_file_directory", None)
            INPUT_FILE_DIRECTORY = input_file_directory
        else:
            INPUT_FILE_DIRECTORY = None

        return model

    @pydantic.field_validator("locale", mode="before")
    @classmethod
    def update_locale(cls, value) -> Locale:
        """Update the output folder name in the RenderCV settings."""
        # Somehow, we need this for `test_if_local_catalog_resets` to pass.
        if value is None:
            return Locale()

        return value
