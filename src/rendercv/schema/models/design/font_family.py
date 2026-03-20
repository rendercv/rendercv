from typing import Literal

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
    ]
)


type FontFamily = str | Literal[*tuple(available_font_families)]  # ty: ignore[invalid-type-form]
