from rendercv.schema.models.design.classic_theme import FontFamily, Typography


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
