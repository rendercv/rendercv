from pathlib import Path

from rendercv.schema.models.locale.locale import available_locales


def test_available_locales():
    """Test that available_locales includes all locale YAML files + EnglishLocale."""
    other_locales_dir = (
        Path(__file__).parent.parent.parent.parent.parent
        / "src"
        / "rendercv"
        / "schema"
        / "models"
        / "locale"
        / "other_locales"
    )

    yaml_files_count = len(list(other_locales_dir.glob("*.yaml")))
    expected_locale_count = yaml_files_count + 1  # +1 for EnglishLocale

    assert len(available_locales) == expected_locale_count
