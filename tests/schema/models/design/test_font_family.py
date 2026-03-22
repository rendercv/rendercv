import pytest
import rendercv_fonts

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
