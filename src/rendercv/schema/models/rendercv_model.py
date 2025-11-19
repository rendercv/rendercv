import pydantic

from .base import BaseModelWithoutExtraKeys
from .cv.cv import Cv
from .design.classic_theme import ClassicTheme
from .design.design import Design
from .locale.locale import EnglishLocale, Locale
from .settings.settings import Settings


class RenderCVModel(BaseModelWithoutExtraKeys):
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
