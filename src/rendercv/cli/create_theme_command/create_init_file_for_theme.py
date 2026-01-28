import pathlib

from rendercv.exception import RenderCVUserError
from rendercv.schema.models.design.design import custom_theme_name_pattern


def create_init_file_for_theme(theme_name: str, init_file_path: pathlib.Path) -> None:
    """Generate `__init__.py` for custom theme by templating from ClassicTheme.

    Why:
        Custom themes need Pydantic models defining design options. Generating
        from ClassicTheme provides working example with all standard fields
        users can modify or extend.

    Args:
        theme_name: Snake_case theme identifier.
        init_file_path: Destination path for __init__.py.
    """
    if not custom_theme_name_pattern.match(theme_name):
        message = (
            "The custom theme name should only contain lowercase letters and digits."
            f" The provided value is `{theme_name}`."
        )
        raise RenderCVUserError(message)

    classic_theme_file = (
        pathlib.Path(__file__).parent.parent.parent
        / "schema"
        / "models"
        / "design"
        / "classic_theme.py"
    )
    new_init_file_contents = classic_theme_file.read_text(encoding="utf-8")

    new_init_file_contents = new_init_file_contents.replace(
        "class ClassicTheme(BaseModelWithoutExtraKeys):",
        f"class {theme_name.capitalize()}Theme(BaseModelWithoutExtraKeys):",
    )
    new_init_file_contents = new_init_file_contents.replace(
        'theme: Literal["classic"] = "classic"',
        f'theme: Literal["{theme_name}"] = "{theme_name}"',
    )
    init_file_path.write_text(new_init_file_contents, encoding="utf-8")
