import pydantic_core
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rendercv.schema.models.design.typography import FontFamily, Typography
from rendercv.schema.models.design.typst_dimension import validate_typst_dimension
from tests.strategies import typst_dimensions


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


class TestTypstDimensionProperties:
    @settings(deadline=None)
    @given(dim=typst_dimensions())
    def test_valid_dimensions_accepted(self, dim: str) -> None:
        assert validate_typst_dimension(dim) == dim

    @settings(deadline=None)
    @given(number=st.from_regex(r"-?\d+(\.\d+)?", fullmatch=True))
    def test_missing_unit_rejected(self, number: str) -> None:
        with pytest.raises(pydantic_core.PydanticCustomError):
            validate_typst_dimension(number)

    @settings(deadline=None)
    @given(
        number=st.from_regex(r"\d+", fullmatch=True),
        unit=st.sampled_from(["px", "rem", "ex", "vh", "vw", "%"]),
    )
    def test_invalid_unit_rejected(self, number: str, unit: str) -> None:
        with pytest.raises(pydantic_core.PydanticCustomError):
            validate_typst_dimension(f"{number}{unit}")

    @settings(deadline=None)
    @given(
        number=st.integers(min_value=1, max_value=999),
        unit=st.sampled_from(["cm", "in", "pt", "mm", "em"]),
    )
    def test_negative_dimensions_allowed(self, number: int, unit: str) -> None:
        dim = f"-{number}{unit}"
        assert validate_typst_dimension(dim) == dim
