"""Font files bundled with RenderCV, available without network access."""

import pathlib
from urllib.parse import quote

__version__: str = "0.6.0"

package_folder_path: pathlib.Path = pathlib.Path(__file__).parent

# Make a list of all the folders (except __pycache__) in the package folder:
available_font_families: list[str] = [
    folder.name
    for folder in sorted(package_folder_path.iterdir())
    if folder.is_dir() and folder.name != "__pycache__"
]
path_of: dict[str, pathlib.Path] = {
    font_family: package_folder_path / font_family
    for font_family in available_font_families
}
paths_to_font_folders: list[pathlib.Path] = list(path_of.values())
paths_to_font_files: list[pathlib.Path] = [
    font_file
    for font_folder in paths_to_font_folders
    for font_file in sorted(font_folder.rglob("*"))
    if font_file.is_file() and font_file.suffix.lower() in {".otf", ".ttf"}
]
# The files of this version, at its release tag:
links_to_font_files: list[str] = [
    f"https://raw.githubusercontent.com/rendercv/rendercv/rendercv-fonts-v{__version__}/"
    "packages/rendercv-fonts/src/rendercv_fonts/"
    + quote(font_path.relative_to(package_folder_path).as_posix())
    for font_path in paths_to_font_files
]
