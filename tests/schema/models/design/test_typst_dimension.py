import pydantic
import pytest

from rendercv.schema.models.design.typst_dimension import TypstDimension

typst_dimension_adapter = pydantic.TypeAdapter(TypstDimension)


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
def test_valid_typst_dimensions(valid_dimension):
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
def test_invalid_typst_dimensions(invalid_dimension):
    with pytest.raises(
        pydantic.ValidationError, match="must be a number followed by a unit"
    ):
        typst_dimension_adapter.validate_python(invalid_dimension)


@pytest.mark.parametrize(
    "unit",
    ["cm", "in", "pt", "mm", "ex", "em"],
)
def test_all_supported_units(unit):
    dimension = f"1.5{unit}"
    result = typst_dimension_adapter.validate_python(dimension)
    assert result == dimension
