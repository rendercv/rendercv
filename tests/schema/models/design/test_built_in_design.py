import json
from pathlib import Path

import pytest
import rendercv_fonts
import typst

from rendercv.schema.models.design.built_in_design import (
    available_themes,
    built_in_theme_models,
)
from rendercv.schema.models.rendercv_model import RenderCVModel


def test_available_themes():
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


@pytest.mark.parametrize("theme", available_themes)
def test_partial_font_override_preserves_theme_defaults(theme: str) -> None:
    model = built_in_theme_models[theme]
    default = model()
    customized = model.model_validate(
        {"typography": {"font_family": {"body": "Arial"}}}
    )
    assert customized.typography.font_family.body == "Arial"
    assert customized.typography.font_family.name == default.typography.font_family.name
    assert type(customized.typography.font_family) is type(
        default.typography.font_family
    )
    customized.model_dump_json(warnings="error")


@pytest.mark.parametrize("theme", available_themes)
def test_built_in_themes_use_fonts_with_native_small_capitals(theme):
    typography = RenderCVModel.model_validate(
        {"cv": {"name": "Jane Doe"}, "design": {"theme": theme}}
    ).design.typography
    for part, enabled in typography.small_caps.model_dump().items():
        if not enabled:
            continue
        family = getattr(typography.font_family, part)
        source = f"""#set text(font: {json.dumps(family)})
#context metadata((
  normal: measure([résumé]).width / 1pt,
  small: measure(smallcaps([résumé])).width / 1pt,
))"""
        widths = json.loads(
            typst.query(
                source.encode(),
                "metadata",
                field="value",
                one=True,
                font_paths=typst.Fonts(
                    font_paths=rendercv_fonts.paths_to_font_folders,
                    include_system_fonts=False,
                ),
            )
        )
        assert widths["small"] != pytest.approx(widths["normal"]), (theme, part, family)
