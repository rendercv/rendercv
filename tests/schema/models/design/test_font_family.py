import pytest
import rendercv_fonts

from rendercv.schema.json_schema_generator import generate_json_schema
from rendercv.schema.models.design.font_family import available_font_families

icon_font_families = {"Font Awesome 7"}
typst_built_in_font_families = {
    "Libertinus Serif",
    "New Computer Modern",
    "DejaVu Sans Mono",
}


@pytest.mark.parametrize(
    "font_family",
    [f for f in rendercv_fonts.available_font_families if f not in icon_font_families],
)
def test_bundled_fonts_are_in_available_font_families(font_family):
    assert font_family in available_font_families


@pytest.mark.parametrize(
    "font_family",
    [f for f in available_font_families if f not in typst_built_in_font_families],
)
def test_no_extra_fonts_in_available_font_families(font_family):
    assert font_family in rendercv_fonts.available_font_families


def test_json_schema_accepts_arbitrary_font_names():
    schema = generate_json_schema()
    font_schema = schema["$defs"][
        "rendercv__schema__models__design__font_family__FontFamily"
    ]
    # Schema should use anyOf to accept both known fonts (enum) and arbitrary strings
    assert "anyOf" in font_schema
    types = [option.get("type") for option in font_schema["anyOf"]]
    assert "string" in types
    # The enum with known fonts should still be present
    enum_options = [option for option in font_schema["anyOf"] if "enum" in option]
    assert len(enum_options) == 1
    assert "Source Sans 3" in enum_options[0]["enum"]
