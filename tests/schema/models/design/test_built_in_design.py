from pathlib import Path

from rendercv.schema.models.design.built_in_design import available_themes


def test_available_themes_count_matches_yaml_files():
    """Test that available_themes includes all theme YAML files + ClassicTheme."""
    other_themes_dir = (
        Path(__file__).parent.parent.parent.parent.parent
        / "src"
        / "rendercv"
        / "schema"
        / "models"
        / "design"
        / "other_themes"
    )

    yaml_files_count = len(list(other_themes_dir.glob("*.yaml")))
    expected_theme_count = yaml_files_count + 1  # +1 for ClassicTheme

    assert len(available_themes) == expected_theme_count
