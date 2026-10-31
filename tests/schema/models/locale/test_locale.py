from pathlib import Path

import pydantic
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


@pytest.mark.parametrize("language", available_locales)
def test_flag_emoji_defined_for_all_locales(language: str):
    """Every locale must have a flag_emoji mapping."""
    locale = locale_adapter.validate_python({"language": language})
    assert len(locale.flag_emoji) > 0


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("english", "\U0001f1ec\U0001f1e7"),  # 🇬🇧
        ("arabic", "\U0001f1f8\U0001f1e6"),  # 🇸🇦
        ("french", "\U0001f1eb\U0001f1f7"),  # 🇫🇷
        ("japanese", "\U0001f1ef\U0001f1f5"),  # 🇯🇵
    ],
)
def test_flag_emoji_values(language: str, expected: str):
    locale = locale_adapter.validate_python({"language": language})
    assert locale.flag_emoji == expected


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
    expected_fields = set(EnglishLocale.model_fields)
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


@pytest.mark.parametrize("language", available_locales)
@pytest.mark.parametrize(
    ("field", "length"),
    [("month_names", 12), ("month_abbreviations", 12), ("day_ordinals", 31)],
)
def test_every_locale_requires_complete_lists(language, field, length):
    # Rendering indexes these lists by month and day, so a short list must fail
    # validation instead of crashing the renderer:
    with pytest.raises(pydantic.ValidationError) as exc:
        locale_adapter.validate_python(
            {"language": language, field: ["x"] * (length - 1)}
        )
    assert exc.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize(
    "value", [{}, {"language": "engilsh"}, {"language": 3}, {"language": []}]
)
def test_invalid_selector_points_to_language(value):
    with pytest.raises(pydantic.ValidationError) as exc:
        locale_adapter.validate_python(value)
    assert exc.value.errors()[0]["loc"] == ("language",)


@pytest.mark.parametrize("language", available_locales)
def test_selected_locale_errors_have_no_branch_label(language):
    with pytest.raises(pydantic.ValidationError) as exc:
        locale_adapter.validate_python({"language": language, "present": 3})
    assert exc.value.errors()[0]["loc"] == ("present",)


@pytest.mark.parametrize(
    ("language", "iso", "flag", "present", "names", "abbreviations"),
    [
        (
            "swedish",
            "sv",
            "🇸🇪",
            "nu",
            (
                "januari februari mars april maj"
                " juni juli augusti september"  # codespell:ignore juni,juli
                " oktober november december"  # codespell:ignore oktober
            ),
            (
                "jan. feb. mars apr. maj"
                " juni juli aug. sep. okt. nov. dec."  # codespell:ignore juni,juli
            ),
        ),
        (
            "polish",
            "pl",
            "🇵🇱",
            "obecnie",
            (
                "styczeń luty marzec kwiecień maj czerwiec lipiec sierpień wrzesień"
                " październik listopad grudzień"
            ),
            "sty lut mar kwi maj cze lip sie wrz paź lis gru",  # codespell:ignore sie
        ),
        (
            "catalan",
            "ca",
            "🇪🇸",
            "actualitat",
            (
                "gener febrer març abril maig juny juliol agost setembre octubre"
                " novembre desembre"
            ),
            "gen. febr. març abr. maig juny jul. ag. set. oct. nov. des.",
        ),
    ],
)
def test_new_locale_cldr_standalone_months(
    language: str, iso: str, flag: str, present: str, names: str, abbreviations: str
) -> None:
    locale = locale_adapter.validate_python({"language": language})
    assert locale.language_iso_639_1 == iso
    assert locale.flag_emoji == flag
    assert locale.present == present
    assert locale.month_names == names.split()
    assert locale.month_abbreviations == abbreviations.split()
    assert (
        locale_adapter.validate_json(locale.model_dump_json(warnings="error")) == locale
    )
