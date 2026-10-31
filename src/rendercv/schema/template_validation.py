import pathlib
import re

import jinja2

rendercv_1_syntax = re.compile(r"\(\(\*|<<[A-Za-z_][\w.]*(?:\|[^>\n]*)?>>")


def validate_templates(directory: pathlib.Path, theme: str, formats: set[str]) -> None:
    """Check the syntax of template overrides before rendering starts.

    Args:
        directory: Directory containing the input file and template overrides.
        theme: Selected theme's directory name.
        formats: Formats needed by the requested outputs.

    Raises:
        ValueError: A template uses obsolete delimiters or invalid Jinja syntax.
    """
    environment = jinja2.Environment()
    folders = {
        "typst": [(theme, "*.j2.typ"), ("typst", "*.j2.typ")],
        "markdown": [("markdown", "*.j2.md")],
    }
    paths = [
        path
        for format in sorted(formats & folders.keys())
        for folder, pattern in folders[format]
        for path in sorted((directory / folder).rglob(pattern))
    ]
    # `Full.html` is the only HTML template. Other files in an `html` folder next
    # to the input, like a personal website, aren't RenderCV's:
    if "html" in formats and (directory / "html" / "Full.html").is_file():
        paths.append(directory / "html" / "Full.html")
    for path in paths:
        source = path.read_text(encoding="utf-8")
        if rendercv_1_syntax.search(source):
            message = (
                f"The template `{path}` uses RenderCV 1 syntax. Templates now use"
                " Jinja's `{{ variable }}` and `{% block %}` delimiters. Remove the"
                " override to use the built-in template, or recreate it with"
                " `rendercv new --create-typst-templates` or"
                " `--create-markdown-templates`."
            )
            raise ValueError(message)
        try:
            environment.parse(source)
        except jinja2.TemplateSyntaxError as error:
            message = (
                f"The template `{path}` has an error at line {error.lineno}:"
                f" {error.message}"
            )
            raise ValueError(message) from error
