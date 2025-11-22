import pathlib
import shutil


def copy_templates(
    folder_name: str,
    copy_to: pathlib.Path,
    new_folder_name: str | None = None,
) -> pathlib.Path | None:
    """Copy one of the folders found in `rendercv.templates` to `copy_to`.

    Args:
        folder_name: The name of the folder to be copied.
        copy_to: The path to copy the folder to.

    Returns:
        The path to the copied folder.
    """
    # copy the package's theme files to the current directory
    template_directory = pathlib.Path(__file__).parent.parent / "themes" / folder_name
    if new_folder_name:
        destination = copy_to / new_folder_name
    else:
        destination = copy_to / folder_name

    if destination.exists():
        return None
    # copy the folder but don't include __init__.py:
    shutil.copytree(
        template_directory,
        destination,
        ignore=shutil.ignore_patterns("__init__.py", "__pycache__"),
    )

    return destination
