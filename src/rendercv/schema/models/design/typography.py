from typing import Literal

import pydantic

from rendercv.schema.models.base import BaseModelWithoutExtraKeys
from rendercv.schema.models.design.font_family import FontFamily as FontFamilyType
from rendercv.schema.models.design.typst_dimension import TypstDimension

type BodyAlignment = Literal["left", "justified", "justified-with-no-hyphenation"]
type Alignment = Literal["left", "center", "right"]


class FontFamily(BaseModelWithoutExtraKeys):
    body: FontFamilyType = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for body text. The default value is `Source Sans 3`."
        ),
    )
    name: FontFamilyType = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for the name. The default value is `Source Sans 3`."
        ),
    )
    headline: FontFamilyType = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for the headline. The default value is `Source Sans 3`."
        ),
    )
    connections: FontFamilyType = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for connections. The default value is `Source Sans 3`."
        ),
    )
    section_titles: FontFamilyType = pydantic.Field(
        default="Source Sans 3",
        description=(
            "The font family for section titles. The default value is `Source Sans 3`."
        ),
    )


class FontSize(BaseModelWithoutExtraKeys):
    body: TypstDimension = pydantic.Field(
        default="10pt",
        description="The font size for body text. The default value is `10pt`.",
    )
    name: TypstDimension = pydantic.Field(
        default="30pt",
        description="The font size for the name. The default value is `30pt`.",
    )
    headline: TypstDimension = pydantic.Field(
        default="10pt",
        description="The font size for the headline. The default value is `10pt`.",
    )
    connections: TypstDimension = pydantic.Field(
        default="10pt",
        description="The font size for connections. The default value is `10pt`.",
    )
    section_titles: TypstDimension = pydantic.Field(
        default="1.4em",
        description="The font size for section titles. The default value is `1.4em`.",
    )


class SmallCaps(BaseModelWithoutExtraKeys):
    name: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use small caps for the name. The default value is `false`."
        ),
    )
    headline: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use small caps for the headline. The default value is `false`."
        ),
    )
    connections: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use small caps for connections. The default value is `false`."
        ),
    )
    section_titles: bool = pydantic.Field(
        default=False,
        description=(
            "Whether to use small caps for section titles. The default value is"
            " `false`."
        ),
    )


class Bold(BaseModelWithoutExtraKeys):
    name: bool = pydantic.Field(
        default=True,
        description="Whether to make the name bold. The default value is `true`.",
    )
    headline: bool = pydantic.Field(
        default=False,
        description="Whether to make the headline bold. The default value is `false`.",
    )
    connections: bool = pydantic.Field(
        default=False,
        description="Whether to make connections bold. The default value is `false`.",
    )
    section_titles: bool = pydantic.Field(
        default=True,
        description="Whether to make section titles bold. The default value is `true`.",
    )


class Typography(BaseModelWithoutExtraKeys):
    line_spacing: TypstDimension = pydantic.Field(
        default="0.6em",
        description=(
            "Space between lines of text. Larger values create more vertical space. The"
            " default value is `0.6em`."
        ),
    )
    alignment: Literal["left", "justified", "justified-with-no-hyphenation"] = (
        pydantic.Field(
            default="justified",
            description=(
                "Text alignment. Options: 'left', 'justified' (spreads text across full"
                " width), 'justified-with-no-hyphenation' (justified without word"
                " breaks). The default value is `justified`."
            ),
        )
    )
    date_and_location_column_alignment: Alignment = pydantic.Field(
        default="right",
        description=(
            "Alignment for dates and locations in entries. Options: 'left', 'center',"
            " 'right'. The default value is `right`."
        ),
    )
    font_family: FontFamily | FontFamilyType = pydantic.Field(
        default_factory=FontFamily,
        description=(
            "The font family. You can provide a single font name as a string (applies"
            " to all elements), or a dictionary with keys 'body', 'name', 'headline',"
            " 'connections', and 'section_titles' to customize each element. Any system"
            " font can be used."
        ),
    )
    font_size: FontSize = pydantic.Field(
        default_factory=FontSize,
        description="Font sizes for different elements.",
    )
    small_caps: SmallCaps = pydantic.Field(
        default_factory=SmallCaps,
        description="Small caps styling for different elements.",
    )
    bold: Bold = pydantic.Field(
        default_factory=Bold,
        description="Bold styling for different elements.",
    )

    @pydantic.field_validator(
        "font_family", mode="plain", json_schema_input_type=FontFamily | FontFamilyType
    )
    @classmethod
    def validate_font_family(
        cls, font_family: FontFamily | FontFamilyType
    ) -> FontFamily:
        """Convert string font to FontFamily object with uniform styling.

        Why:
            Users can provide simple string "Latin Modern Roman" for all text,
            or specify per-element fonts via FontFamily dict. Validator accepts
            both, expanding strings to full FontFamily objects.

        Args:
            font_family: String font name or FontFamily object.

        Returns:
            FontFamily object with all fields populated.
        """
        if isinstance(font_family, str):
            return FontFamily(
                body=font_family,
                name=font_family,
                headline=font_family,
                connections=font_family,
                section_titles=font_family,
            )

        return FontFamily.model_validate(font_family)
