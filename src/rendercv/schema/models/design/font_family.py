from typing import Literal

from pydantic.json_schema import SkipJsonSchema

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
        "Arial Rounded MT",
        "Arial Unicode MS",
        "Courier New",
        "Times New Roman",
        "Trebuchet MS",
        "Verdana",
        "Georgia",
        "Tahoma",
        "Impact",
        "Comic Sans MS",
        "Lucida Sans Unicode",
        "Helvetica",
        "Tahoma",
        "Times New Roman",
        "Verdana",
        "Georgia",
        "Aptos",
        "Inter",
        "Garamond",
        "Gill Sans",
        "Didot",
    ]
)


type FontFamily = SkipJsonSchema[str] | Literal[*tuple(available_font_families)]  # pyright: ignore[reportInvalidTypeForm]
