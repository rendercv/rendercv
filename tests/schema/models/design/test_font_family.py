import pydantic
import pytest

from rendercv.schema.models.context import ValidationContext
from rendercv.schema.models.design.font_family import (
    FontFamily,
    available_font_families,
)

font_family_adapter = pydantic.TypeAdapter(FontFamily)


@pytest.fixture
def context_without_fonts_dir(tmp_path):
    """Context where no fonts/ directory exists next to input file."""
    input_file = tmp_path / "input.yaml"
    input_file.touch()
    return {"context": ValidationContext(input_file_path=input_file)}


@pytest.fixture
def context_with_fonts_dir(tmp_path):
    """Context where fonts/ directory exists next to input file."""
    input_file = tmp_path / "input.yaml"
    input_file.touch()
    fonts_dir = tmp_path / "fonts"
    fonts_dir.mkdir()
    return {"context": ValidationContext(input_file_path=input_file)}


class TestFontFamilyValidation:
    @pytest.mark.parametrize(
        "valid_font",
        [
            "Source Sans 3",
            "Open Sans",
            "Libertinus Serif",
            "Arial",
            "Times New Roman",
        ],
    )
    def test_valid_font_families_from_list(self, valid_font, context_without_fonts_dir):
        result = font_family_adapter.validate_python(
            valid_font, context=context_without_fonts_dir
        )
        assert result == valid_font

    @pytest.mark.parametrize(
        "invalid_font",
        [
            "Comic Sans",
            "NonExistentFont",
            "Random Font Name",
        ],
    )
    def test_invalid_font_families_raise_error(
        self, invalid_font, context_without_fonts_dir
    ):
        with pytest.raises(
            pydantic.ValidationError, match="font family must be one of the following"
        ):
            font_family_adapter.validate_python(
                invalid_font, context=context_without_fonts_dir
            )

    @pytest.mark.parametrize(
        "any_font",
        [
            "Custom Font",
            "My Special Font",
            "Comic Sans",
            "Literally Anything",
        ],
    )
    def test_any_font_accepted_when_fonts_dir_exists(
        self, any_font, context_with_fonts_dir
    ):
        result = font_family_adapter.validate_python(
            any_font, context=context_with_fonts_dir
        )
        assert result == any_font

    def test_font_from_list_also_works_with_fonts_dir(self, context_with_fonts_dir):
        result = font_family_adapter.validate_python(
            "Source Sans 3", context=context_with_fonts_dir
        )
        assert result == "Source Sans 3"


def test_all_available_fonts_are_valid(context_without_fonts_dir):
    for font in available_font_families:
        result = font_family_adapter.validate_python(
            font, context=context_without_fonts_dir
        )
        assert result == font
