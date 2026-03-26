import pydantic
import pydantic_core
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rendercv.schema.models.design.typst_dimension import (
    TypstDimension,
    validate_typst_dimension,
)


@st.composite
def typst_dimensions(draw: st.DrawFn) -> str:
    """Generate valid Typst dimension strings."""
    sign = draw(st.sampled_from(["", "-"]))
    integer_part = draw(st.integers(min_value=0, max_value=999))
    has_decimal = draw(st.booleans())
    decimal_part = ""
    if has_decimal:
        decimal_part = "." + str(draw(st.integers(min_value=0, max_value=99)))
    unit = draw(st.sampled_from(["cm", "in", "pt", "mm", "em"]))
    return f"{sign}{integer_part}{decimal_part}{unit}"


class TestTypstDimension:
    @pytest.mark.parametrize(
        "valid_dimension",
        [
            "1cm",
            "2.5cm",
            "10mm",
            "0.5in",
            "12pt",
            "1.25em",
            "100pt",
            "0.1cm",
            "-1cm",
        ],
    )
    def test_accepts_valid_dimensions(self, valid_dimension):
        typst_dimension_adapter = pydantic.TypeAdapter[TypstDimension](TypstDimension)
        result = typst_dimension_adapter.validate_python(valid_dimension)
        assert result == valid_dimension

    @pytest.mark.parametrize(
        "invalid_dimension",
        [
            "1",
            "cm",
            "1.5",
            "1 cm",
            "1.5.5cm",
            "1px",
            "2ex",
            "1.em",
            "1.5rem",
            "cm1",
            "",
        ],
    )
    def test_rejects_invalid_dimensions(self, invalid_dimension):
        typst_dimension_adapter = pydantic.TypeAdapter[TypstDimension](TypstDimension)
        with pytest.raises(
            pydantic.ValidationError, match="must be a number followed by a unit"
        ):
            typst_dimension_adapter.validate_python(invalid_dimension)

    @pytest.mark.parametrize(
        "unit",
        ["cm", "in", "pt", "mm", "em"],
    )
    def test_supports_all_units(self, unit):
        typst_dimension_adapter = pydantic.TypeAdapter[TypstDimension](TypstDimension)
        dimension = f"1.5{unit}"
        result = typst_dimension_adapter.validate_python(dimension)
        assert result == dimension

    @settings(deadline=None)
    @given(dim=typst_dimensions())  # ty: ignore[missing-argument]
    def test_accepts_random_valid_dimensions(self, dim: str) -> None:
        assert validate_typst_dimension(dim) == dim

    @settings(deadline=None)
    @given(number=st.from_regex(r"-?\d+(\.\d+)?", fullmatch=True))
    def test_rejects_missing_unit(self, number: str) -> None:
        with pytest.raises(pydantic_core.PydanticCustomError):
            validate_typst_dimension(number)

    @settings(deadline=None)
    @given(
        number=st.from_regex(r"\d+", fullmatch=True),
        unit=st.sampled_from(["px", "rem", "ex", "vh", "vw", "%"]),
    )
    def test_rejects_unsupported_units(self, number: str, unit: str) -> None:
        with pytest.raises(pydantic_core.PydanticCustomError):
            validate_typst_dimension(f"{number}{unit}")

    @settings(deadline=None)
    @given(
        number=st.integers(min_value=1, max_value=999),
        unit=st.sampled_from(["cm", "in", "pt", "mm", "em"]),
    )
    def test_accepts_negative_dimensions(self, number: int, unit: str) -> None:
        dim = f"-{number}{unit}"
        assert validate_typst_dimension(dim) == dim
