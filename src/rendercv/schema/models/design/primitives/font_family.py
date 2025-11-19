from typing import Annotated, Literal

import pydantic
import pydantic_core

from ....context import get_input_file_path
from ....pydantic_error_handling import CustomPydanticErrorTypes

available_font_families = sorted(
    [
        # Typst built-ins
        "Libertinus Serif",
        "New Computer Modern",
        "DejaVu Sans Mono",
        # RenderCV bundled
        "Mukta",
        "Open Sans",
        "Gentium Book Plus",
        "Noto Sans",
        "Lato",
        "Source Sans 3",
        "EB Garamond",
        "Open Sauce Sans",
        "Fontin",
        "Roboto",
        "Ubuntu",
        "Poppins",
        "Raleway",
        "XCharter",
        # Common system fonts
        "Arial",
        "Helvetica",
        "Tahoma",
        "Times New Roman",
        "Verdana",
        "Calibri",
        "Georgia",
        "Aptos",
        "Cambria",
        "Inter",
        "Garamond",
        "Montserrat",
        "Candara",
        "Gill Sans",
        "Didot",
        "Playfair Display",
    ]
)


def validate_font_family(font_family: str, info: pydantic.ValidationInfo) -> str:
    """Validate against available fonts. Skips validation if fonts/ dir exists."""
    input_file_path = get_input_file_path(info)
    if (input_file_path / "fonts").exists():
        return font_family

    if font_family not in available_font_families:
        raise pydantic_core.PydanticCustomError(
            CustomPydanticErrorTypes.other.value,
            "The font family must be one of the following: {available_font_families}."
            " The provided value is `{font_family}`.",
            {
                "font_family": font_family,
                "available_font_families": ", ".join(available_font_families),
            },
        )

    return font_family


type FontFamily = Annotated[
    str,
    pydantic.PlainValidator(
        validate_font_family,
        json_schema_input_type=Literal[tuple(available_font_families)],
    ),
]
