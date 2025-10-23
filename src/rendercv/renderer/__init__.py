"""
The `rendercv.renderer` package contains the necessary classes and functions for
generating Typst, PDF, Markdown, HTML, and PNG files from the `RenderCVDataModel`
object.

The Typst and Markdown files are generated with
[Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) templates. Then, the Typst
file is rendered into a PDF and PNGs with
[`typst` package](https://github.com/messense/typst-py). The Markdown file is rendered
into an HTML file with
[`markdown` package](https://github.com/Python-Markdown/markdown).
"""

from .renderer import (
    create_a_markdown_file,
    create_a_typst_file,
    create_a_typst_file_and_copy_theme_files,
    create_contents_of_a_markdown_file,
    create_contents_of_a_typst_file,
    render_a_pdf_from_typst,
    render_an_html_from_markdown,
    render_pngs_from_typst,
)

__all__ = [
    "create_a_markdown_file",
    "create_a_typst_file",
    "create_a_typst_file_and_copy_theme_files",
    "create_contents_of_a_markdown_file",
    "create_contents_of_a_typst_file",
    "render_a_pdf_from_typst",
    "render_an_html_from_markdown",
    "render_pngs_from_typst",
]
