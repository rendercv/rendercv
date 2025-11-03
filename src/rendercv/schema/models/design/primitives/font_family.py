import pathlib
from typing import Annotated, Literal

import pydantic
import pydantic_core

available_font_families = sorted(
    [
        # Typst fonts:
        "Libertinus Serif",
        "New Computer Modern",
        "DejaVu Sans Mono",
        # Rendercv fonts:
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
        # Common system fonts:
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


def validate_font_family(font_family: str) -> str:
    """Check if the input string is a valid font family.

    Args:
        font_family: The input string to be validated.

    Returns:
        The input string itself if it is a valid font family.
    """
    # TODO: CONTEXT
    if (pathlib.Path("fonts")).exists():
        # Then allow any font family.
        return font_family

    if font_family not in available_font_families:
        raise pydantic_core.PydanticCustomError(
            "rendercv_custom_error",
            "The font family must be one of the following: {available_font_families}."
            " The provided value is {font_family}.",
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
