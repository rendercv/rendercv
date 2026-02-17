import pydantic
import pytest

from rendercv.schema.models.design.typst_dimension import TypstDimension


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
            "2ex",
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
        ["cm", "in", "pt", "mm", "ex", "em"],
    )
    def test_supports_all_units(self, unit):
        typst_dimension_adapter = pydantic.TypeAdapter[TypstDimension](TypstDimension)
        dimension = f"1.5{unit}"
        result = typst_dimension_adapter.validate_python(dimension)
        assert result == dimension
