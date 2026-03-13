from rendercv.schema.models.design.classic_theme import (
    ClassicTheme,
    FontFamily,
    SubsectionTitles,
    Typography,
)


class TestTypography:
    def test_accepts_font_family_as_string(self):
        typography = Typography(font_family="Arial")

        assert isinstance(typography.font_family, FontFamily)
        assert typography.font_family.body == "Arial"
        assert typography.font_family.name == "Arial"
        assert typography.font_family.headline == "Arial"
        assert typography.font_family.connections == "Arial"
        assert typography.font_family.section_titles == "Arial"

    def test_accepts_font_family_as_dict(self):
        typography = Typography(
            font_family={
                "body": "Arial",
                "name": "Georgia",
                "headline": "Helvetica",
                "connections": "Verdana",
                "section_titles": "Tahoma",
            }
        )

        assert isinstance(typography.font_family, FontFamily)
        assert typography.font_family.body == "Arial"
        assert typography.font_family.name == "Georgia"
        assert typography.font_family.headline == "Helvetica"
        assert typography.font_family.connections == "Verdana"
        assert typography.font_family.section_titles == "Tahoma"


class TestSections:
    def test_accepts_subsection_title_spacing(self):
        theme = ClassicTheme(
            subsection_titles=SubsectionTitles(
                space_above="0.2cm",
                space_below="0.1cm",
            )
        )

        assert theme.subsection_titles.space_above == "0.2cm"
        assert theme.subsection_titles.space_below == "0.1cm"
