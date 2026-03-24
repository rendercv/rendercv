from typing import Literal

import pydantic

from rendercv.schema.models.base import BaseModelWithoutExtraKeys
from rendercv.schema.models.design.typography import Alignment
from rendercv.schema.models.design.typst_dimension import TypstDimension

type PhoneNumberFormatType = Literal["national", "international", "E164"]

length_common_description = (
    "It can be specified with units (cm, in, pt, mm, em). For example, `0.1cm`."
)


class Links(BaseModelWithoutExtraKeys):
    underline: bool = pydantic.Field(
        default=False,
        description="Underline hyperlinks. The default value is `false`.",
    )
    show_external_link_icon: bool = pydantic.Field(
        default=False,
        description=(
            "Show an external link icon next to URLs. The default value is `false`."
        ),
    )


class Connections(BaseModelWithoutExtraKeys):
    phone_number_format: PhoneNumberFormatType = pydantic.Field(
        default="national",
        description="Phone number format. The default value is `national`.",
    )
    hyperlink: bool = pydantic.Field(
        default=True,
        description=(
            "Make contact information clickable in the PDF. The default value is"
            " `true`."
        ),
    )
    show_icons: bool = pydantic.Field(
        default=True,
        description=(
            "Show icons next to contact information. The default value is `true`."
        ),
    )
    display_urls_instead_of_usernames: bool = pydantic.Field(
        default=False,
        description=(
            "Display full URLs instead of labels. The default value is `false`."
        ),
    )
    separator: str = pydantic.Field(
        default="",
        description=(
            "Character(s) to separate contact items (e.g., '|' or '•'). Leave empty for"
            " no separator. The default value is `''`."
        ),
    )
    space_between_connections: TypstDimension = pydantic.Field(
        default="0.5cm",
        description=(
            "Horizontal space between contact items. "
            + length_common_description
            + " The default value is `0.5cm`."
        ),
    )


class Header(BaseModelWithoutExtraKeys):
    alignment: Alignment = pydantic.Field(
        default="center",
        description=(
            "Header alignment. Options: 'left', 'center', 'right'. The default value is"
            " `center`."
        ),
    )
    photo_width: TypstDimension = pydantic.Field(
        default="3.5cm",
        description="Photo width. "
        + length_common_description
        + " The default value is `3.5cm`.",
    )
    photo_position: Literal["left", "right"] = pydantic.Field(
        default="left",
        description="Photo position (left or right). The default value is `left`.",
    )
    photo_space_left: TypstDimension = pydantic.Field(
        default="0.4cm",
        description=(
            "Space to the left of the photo. "
            + length_common_description
            + " The default value is `0.4cm`."
        ),
    )
    photo_space_right: TypstDimension = pydantic.Field(
        default="0.4cm",
        description=(
            "Space to the right of the photo. "
            + length_common_description
            + " The default value is `0.4cm`."
        ),
    )
    space_below_name: TypstDimension = pydantic.Field(
        default="0.7cm",
        description="Space below your name. "
        + length_common_description
        + " The default value is `0.7cm`.",
    )
    space_below_headline: TypstDimension = pydantic.Field(
        default="0.7cm",
        description="Space below the headline. "
        + length_common_description
        + " The default value is `0.7cm`.",
    )
    space_below_connections: TypstDimension = pydantic.Field(
        default="0.7cm",
        description="Space below contact information. "
        + length_common_description
        + " The default value is `0.7cm`.",
    )
    connections: Connections = pydantic.Field(
        default_factory=Connections,
        description="Contact information settings.",
    )
