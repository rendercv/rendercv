import pathlib
import shutil
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
