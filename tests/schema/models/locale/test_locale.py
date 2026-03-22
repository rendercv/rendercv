from pathlib import Path

import pytest

from rendercv.schema.models.locale.english_locale import EnglishLocale, Phrases
from rendercv.schema.models.locale.locale import available_locales, locale_adapter
from rendercv.schema.yaml_reader import read_yaml

OTHER_LOCALES_DIR = (
    Path(__file__).parent.parent.parent.parent.parent
    / "src"
    / "rendercv"
    / "schema"
    / "models"
    / "locale"
    / "other_locales"
)


def test_available_locales():
    """Test that available_locales includes all locale YAML files + EnglishLocale."""
    yaml_files_count = len(list(OTHER_LOCALES_DIR.glob("*.yaml")))
    expected_locale_count = yaml_files_count + 1  # +1 for EnglishLocale

    assert len(available_locales) == expected_locale_count


@pytest.mark.parametrize(
    "language",
    [
        "arabic",
        "hebrew",
        "persian",
    ],
)
def test_locale_adapter_rtl_languages(language: str):
    locale = locale_adapter.validate_python({"language": language})
    assert locale.is_rtl is True


@pytest.mark.parametrize(
    "yaml_file",
    sorted(OTHER_LOCALES_DIR.glob("*.yaml")),
    ids=lambda p: p.stem,
)
def test_all_locales_override_all_fields(yaml_file: Path):
    """Test that each locale YAML defines every field from EnglishLocale.

    Why:
        Missing fields silently fall back to English defaults, which is
        incorrect for non-English locales (e.g., English "in" appearing in
        Arabic text). This test catches omissions early.
    """
    locale_data = read_yaml(yaml_file)["locale"]

    # Check top-level fields
    expected_fields = set(EnglishLocale.model_fields.keys())
    actual_fields = set(locale_data.keys())
    missing = expected_fields - actual_fields
    assert not missing, f"{yaml_file.stem}: missing top-level fields {sorted(missing)}"

    # Check nested Phrases fields
    phrases_data = locale_data.get("phrases", {})
    expected_phrases_fields = set(Phrases.model_fields.keys())
    actual_phrases_fields = set(phrases_data.keys())
    missing_phrases = expected_phrases_fields - actual_phrases_fields
    assert not missing_phrases, (
        f"{yaml_file.stem}: missing phrases fields {sorted(missing_phrases)}"
    )
