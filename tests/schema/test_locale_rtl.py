"""Tests for locale RTL support and cv_title_name localization."""

import pytest

from rendercv.schema.models.locale.english_locale import EnglishLocale


class TestLocaleRTLSupport:
    """Test RTL (Right-to-Left) language support in locale model."""

    def test_is_rtl_returns_false_for_english(self):
        """English locale should return is_rtl=False."""
        locale = EnglishLocale()
        assert locale.is_rtl is False

    def test_text_direction_returns_ltr_for_english(self):
        """English locale should return text_direction='ltr'."""
        locale = EnglishLocale()
        assert locale.text_direction == "ltr"

    def test_language_iso_639_1_for_english(self):
        """English locale should return ISO 639-1 code 'en'."""
        locale = EnglishLocale()
        assert locale.language_iso_639_1 == "en"

    def test_cv_title_name_default_value(self):
        """Default cv_title_name should contain {name} placeholder."""
        locale = EnglishLocale()
        assert "{name}" in locale.cv_title_name

    def test_cv_title_name_format_with_name(self):
        """cv_title_name should format correctly with a name."""
        locale = EnglishLocale()
        formatted = locale.cv_title_name.replace("{name}", "John Doe")
        assert "John Doe" in formatted
        assert "CV" in formatted


class TestRTLLanguageDetection:
    """Test that RTL languages are correctly detected."""

    @pytest.mark.parametrize(
        "language,expected_rtl",
        [
            ("arabic", True),
            ("hebrew", True),
            ("persian", True),
            ("urdu", True),
            ("english", False),
            ("french", False),
            ("german", False),
        ],
    )
    def test_is_rtl_for_various_languages(self, language: str, expected_rtl: bool):
        """Test is_rtl property for various languages."""
        locale = EnglishLocale()
        # Override the language for testing
        object.__setattr__(locale, "language", language)
        # Clear cached property
        if "is_rtl" in locale.__dict__:
            del locale.__dict__["is_rtl"]
        assert locale.is_rtl is expected_rtl

    @pytest.mark.parametrize(
        "language,expected_direction",
        [
            ("arabic", "rtl"),
            ("hebrew", "rtl"),
            ("english", "ltr"),
            ("french", "ltr"),
        ],
    )
    def test_text_direction_for_various_languages(
        self, language: str, expected_direction: str
    ):
        """Test text_direction property for various languages."""
        locale = EnglishLocale()
        object.__setattr__(locale, "language", language)
        # Clear cached properties
        if "is_rtl" in locale.__dict__:
            del locale.__dict__["is_rtl"]
        if "text_direction" in locale.__dict__:
            del locale.__dict__["text_direction"]
        assert locale.text_direction == expected_direction
