"""Tests that generated files describe the current source code.

Why:
    schema.json and the example YAMLs are derived from source code and committed.
    These tests fail when the committed files diverge from what the generation code
    produces, catching staleness on every PR instead of silently regenerating in
    CI. The AI agent skill is generated at release time, so its tests check what
    the generator writes.
"""

import pathlib
import runpy
import subprocess

import pytest

from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.sample_generator import create_sample_yaml_input_file

repository_root = pathlib.Path(__file__).parent.parent


def run_just(recipe: str) -> None:
    """Run a just recipe and raise on failure."""
    subprocess.run(
        ["just", recipe],
        cwd=repository_root,
        check=True,
        capture_output=True,
    )


def test_schema_json_is_up_to_date() -> None:
    schema_path = repository_root / "schema.json"
    before = schema_path.read_text(encoding="utf-8")

    run_just("update-schema")

    after = schema_path.read_text(encoding="utf-8")
    # Restore original content
    schema_path.write_text(before, encoding="utf-8")

    assert before == after, (
        "schema.json is stale. Run `just update-schema` to regenerate."
    )


@pytest.mark.parametrize("theme", available_themes)
def test_example_yaml_is_up_to_date(theme: str) -> None:
    yaml_path = (
        repository_root / "examples" / f"John_Doe_{theme.capitalize()}Theme_CV.yaml"
    )
    before = yaml_path.read_text(encoding="utf-8")

    expected = create_sample_yaml_input_file(
        file_path=None,
        name="John Doe",
        theme=theme,
        locale="english",
    )

    assert before == expected, (
        f"examples/John_Doe_{theme.capitalize()}Theme_CV.yaml is stale. "
        "Run `just update-examples` to regenerate."
    )


def build_skill_repository() -> dict[str, str]:
    generator = runpy.run_path(
        str(repository_root / "scripts" / "rendercv_skill" / "generate.py")
    )
    return generator["build_skill_repository"]()


def test_skill_lists_every_available_theme() -> None:
    files = build_skill_repository()

    for theme in available_themes:
        assert f"`{theme}`" in files["skills/rendercv/SKILL.md"]
        assert f"skills/rendercv/references/themes/{theme}.yaml" in files


def test_skill_has_no_repository_relative_schema_paths() -> None:
    for content in build_skill_repository().values():
        assert "$schema=../" not in content
