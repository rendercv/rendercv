"""Theme listing endpoint support: names and per-theme design defaults.

Why:
    Reuses the core's own theme registry (`available_themes`) and pydantic
    design models so the web app never hand-maintains a duplicate theme list
    or default values that could drift from the core.
"""

from rendercv.schema.models.design.built_in_design import (
    available_themes,
    built_in_design_adapter,
)

from .models import ThemeInfo


def list_theme_defaults() -> list[ThemeInfo]:
    """Build the default design options for every built-in theme.

    Why:
        Instantiating each theme's pydantic design model with only the
        `theme` discriminator set produces exactly the defaults the core
        would apply, without reimplementing any theme's option values.

    Returns:
        One `ThemeInfo` per built-in theme, in the core's declared order.
    """
    themes: list[ThemeInfo] = []
    for theme_name in available_themes:
        design_model = built_in_design_adapter.validate_python({"theme": theme_name})
        themes.append(
            ThemeInfo(
                name=theme_name,
                design_defaults=design_model.model_dump(mode="json"),
            )
        )
    return themes
