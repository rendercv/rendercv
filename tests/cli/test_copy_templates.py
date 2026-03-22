import os
import pathlib
import stat

import pytest

from rendercv.cli.copy_templates import copy_templates, make_tree_writable


@pytest.mark.parametrize("template_type", ["markdown", "typst"])
def test_copy_templates(template_type, tmp_path):
    destination = tmp_path / "templates"

    copy_templates(template_type, destination)

    assert destination.exists()
    assert not (destination / "__init__.py").exists()
    assert not (destination / "__pycache__").exists()
    # Check that at least some files were copied
    assert any(destination.iterdir())


def test_copy_templates_produces_writable_files(tmp_path):
    destination = tmp_path / "templates"

    copy_templates("typst", destination)

    for dirpath, _, filenames in os.walk(destination):
        dp = pathlib.Path(dirpath)
        assert dp.stat().st_mode & stat.S_IWUSR, f"Directory {dp} is not user-writable"
        for filename in filenames:
            fp = dp / filename
            assert fp.stat().st_mode & stat.S_IWUSR, f"File {fp} is not user-writable"


def test_make_tree_writable(tmp_path):
    # Create a tree with read-only files and directories
    subdir = tmp_path / "readonly_dir"
    subdir.mkdir()
    test_file = subdir / "test.txt"
    test_file.write_text("content")
    nested = subdir / "nested"
    nested.mkdir()
    nested_file = nested / "nested.txt"
    nested_file.write_text("nested content")

    # Make everything read-only
    nested_file.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    nested.chmod(stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IROTH)
    test_file.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    subdir.chmod(stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IROTH)

    make_tree_writable(subdir)

    # All should be user-writable now
    assert subdir.stat().st_mode & stat.S_IWUSR
    assert test_file.stat().st_mode & stat.S_IWUSR
    assert nested.stat().st_mode & stat.S_IWUSR
    assert nested_file.stat().st_mode & stat.S_IWUSR
