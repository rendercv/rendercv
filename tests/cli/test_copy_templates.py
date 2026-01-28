import pytest

from rendercv.cli.copy_templates import copy_templates


@pytest.mark.parametrize("template_type", ["markdown", "typst"])
def test_copy_templates(template_type, tmp_path):
    destination = tmp_path / "templates"

    copy_templates(template_type, destination)

    assert destination.exists()
    assert not (destination / "__init__.py").exists()
    assert not (destination / "__pycache__").exists()
    # Check that at least some files were copied
    assert any(destination.iterdir())
