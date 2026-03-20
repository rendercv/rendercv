import os
import pathlib
import shutil
import stat
from typing import Literal


def copy_templates(
    template_type: Literal["markdown", "typst"], copy_templates_to: pathlib.Path
) -> None:
    """Copy built-in template directory to user location for customization.

    Why:
        Users creating custom themes need starting templates to modify.

    Args:
        template_type: Which template set to copy.
        copy_templates_to: Destination directory path.
    """
    # copy the package's theme files to the current directory
    template_directory = (
        pathlib.Path(__file__).parent.parent
        / "renderer"
        / "templater"
        / "templates"
        / template_type
    )
    # copy the folder but don't include __init__.py:
    shutil.copytree(
        template_directory,
        copy_templates_to,
        ignore=shutil.ignore_patterns("__init__.py", "__pycache__"),
    )
    make_tree_writable(copy_templates_to)


def make_tree_writable(path: pathlib.Path) -> None:
    """Add user-write permission to all files and directories in a tree.

    Why:
        On immutable distributions like NixOS, package files are read-only.
        shutil.copytree preserves source permissions, so copied files remain
        read-only. Users need write access to customize templates.

    Args:
        path: Root directory to make writable.
    """
    for dirpath, _, filenames in os.walk(path):
        dp = pathlib.Path(dirpath)
        dp.chmod(dp.stat().st_mode | stat.S_IWUSR)
        for filename in filenames:
            fp = dp / filename
            fp.chmod(fp.stat().st_mode | stat.S_IWUSR)
