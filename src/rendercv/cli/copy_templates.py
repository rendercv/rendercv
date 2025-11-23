import pathlib
import shutil
from typing import Literal


def copy_templates(
    template_type: Literal["markdown", "typst"], copy_templates_to: pathlib.Path
) -> None:
    """Copy one of the folders found in `rendercv.templates` to `copy_to`.

    Args:
        folder_name: The name of the folder to be copied.
        copy_to: The path to copy the folder to.

    Returns:
        The path to the copied folder.
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
