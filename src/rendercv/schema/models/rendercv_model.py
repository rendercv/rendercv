import pathlib

import pydantic
import pydantic_core

from ..output_paths import OutputPlan, build_output_plan
from ..template_validation import validate_templates
from .base import BaseModelWithoutExtraKeys
from .cv.cv import Cv
from .design.classic_theme import ClassicTheme
from .design.design import Design
from .locale.locale import EnglishLocale, Locale
from .settings.settings import Settings
from .validation_context import ValidationContext, get_input_file_path


class RenderCVModel(BaseModelWithoutExtraKeys):
    """Top-level model representing a complete RenderCV configuration.

    Why:
        This is the root of the entire data model, combining CV content,
        design theme, locale translations, and rendering settings into a
        single validated structure. All rendering pipeline stages operate
        on this unified model.
    """

    # Technically, `cv` is a required field, but we don't pass it to the JSON Schema
    # so that the same schema can be used for standalone design, locale, and settings
    # files.
    model_config = pydantic.ConfigDict(json_schema_extra={"required": []})
    cv: Cv = pydantic.Field(
        default_factory=Cv,
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
    # Settings resolve their default paths from the input file, which only the
    # validation context knows, so their default is validated like an input:
    settings: Settings = pydantic.Field(
        default_factory=dict,
        title="RenderCV Settings",
        description="The settings of the RenderCV.",
    )

    _input_file_path: pathlib.Path | None = pydantic.PrivateAttr(default=None)
    _input_paths: tuple[pathlib.Path, ...] = pydantic.PrivateAttr(default=())

    @property
    def _output_plan(self) -> OutputPlan:
        """Derive paths from current values, including edits through the Python API."""
        return build_output_plan(self)

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
        if isinstance(info.context, dict) and isinstance(
            info.context.get("context"), ValidationContext
        ):
            self._input_paths = info.context["context"].input_paths
        return self

    @pydantic.model_validator(mode="after")
    def validate_document(self) -> "RenderCVModel":
        """Validate requirements that depend on more than one top-level field.

        Returns:
            The validated document.
        """
        build_output_plan(self)
        if (
            not self.settings.render_command.dont_generate_pdf
            and self.settings.pdf_profile != "standard"
            and not (self.cv.name and self.cv.name.strip())
        ):
            raise pydantic.ValidationError.from_exception_data(
                type(self).__name__,
                [
                    {
                        "type": pydantic_core.PydanticCustomError(
                            "rendercv_other_error",
                            "PDF/UA-1 requires a main heading. Add `cv.name`, or set"
                            " `settings.pdf_profile` to `standard` for an unnamed PDF.",
                        ),
                        "loc": ("cv", "name"),
                        "input": self.cv.name,
                    }
                ],
            )
        directory = (
            self._input_file_path.parent
            if self._input_file_path
            else pathlib.Path.cwd()
        )
        enabled = self.settings.render_command.enabled_outputs
        formats = enabled & {"markdown", "html"}
        if enabled & {"typst", "pdf", "png", "svg"}:
            formats.add("typst")
        validate_templates(directory, self.design.theme, formats)
        return self
