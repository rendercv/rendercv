"""
The `rendercv.renderer.renderer` module contains the necessary functions for rendering
Typst, PDF, Markdown, HTML, and PNG files from the `RenderCVDataModel` object.
"""

import importlib.resources
import pathlib
import re
import shutil
import tempfile
from typing import Optional

import markdown
import rendercv_fonts
import typst

from .. import data
from . import templater


def copy_theme_files_to_output_directory(
    theme_name: str,
    output_directory_path: pathlib.Path,
):
    """Copy the auxiliary files (all the files that don't end with `.j2.typ` and `.py`)
    of the theme to the output directory.

    Args:
        theme_name: The name of the theme.
        output_directory_path: Path to the output directory.
    """
    if theme_name in data.available_themes:
        theme_directory_path = importlib.resources.files(
            f"rendercv.themes.{theme_name}"
        )
    else:
        # Then it means the theme is a custom theme. If theme_directory is not given
        # as an argument, then look for the theme in the current working directory.
        theme_directory_path = pathlib.Path.cwd() / theme_name

        if not theme_directory_path.is_dir():
            message = (
                f"The theme {theme_name} doesn't exist in the available themes and"
                " the current working directory!"
            )
            raise FileNotFoundError(message)

    dont_copy_files_with_these_extensions = [".py", ".j2.typ"]
    for theme_file in theme_directory_path.iterdir():
        # theme_file.suffix returns the latest part of the file name after the last dot.
        # But we need the latest part of the file name after the first dot:
        try:
            suffix = re.search(r"\..*", theme_file.name)[0]  # type: ignore
        except TypeError:
            suffix = ""

        if suffix not in dont_copy_files_with_these_extensions:
            if theme_file.is_dir():
                shutil.copytree(
                    str(theme_file),
                    output_directory_path / theme_file.name,
                    dirs_exist_ok=True,
                )
            else:
                shutil.copyfile(
                    str(theme_file), output_directory_path / theme_file.name
                )


def create_typst_contents(
    rendercv_data_model: data.RenderCVDataModel,
) -> str:
    """Create a Typst file with the given data model and return it as a string.

    Args:
        rendercv_data_model: The data model.

    Returns:
        The path to the generated Typst file.
    """
    jinja2_environment = templater.setup_jinja2_environment()

    file_object = templater.TypstFile(
        rendercv_data_model,
        jinja2_environment,
    )

    return file_object.get_full_code()


def create_a_typst_file(
    rendercv_data_model: data.RenderCVDataModel,
    output_directory: pathlib.Path,
) -> pathlib.Path:
    """Create a Typst file (depending on the theme) with the given data model and write
    it to the output directory.

    Args:
        rendercv_data_model: The data model.
        output_directory: Path to the output directory. If not given, the Typst file
            will be returned as a string.

    Returns:
        The path to the generated Typst file.
    """

    typst_contents = create_typst_contents(rendercv_data_model)

    # Create output directory if it doesn't exist:
    if not output_directory.is_dir():
        output_directory.mkdir(parents=True)

    file_name = f"{str(rendercv_data_model.cv.name).replace(' ', '_')}_CV.typ"
    file_path = output_directory / file_name
    file_path.write_text(typst_contents, encoding="utf-8")

    return file_path


def create_a_markdown_file(
    rendercv_data_model: data.RenderCVDataModel, output_directory: pathlib.Path
) -> pathlib.Path:
    """Render the Markdown file with the given data model and write it to the output
    directory.

    Args:
        rendercv_data_model: The data model.
        output_directory: Path to the output directory.

    Returns:
        The path to the rendered Markdown file.
    """
    # create output directory if it doesn't exist:
    if not output_directory.is_dir():
        output_directory.mkdir(parents=True)

    jinja2_environment = templater.setup_jinja2_environment()
    markdown_file_object = templater.MarkdownFile(
        rendercv_data_model,
        jinja2_environment,
    )

    markdown_file_name = f"{str(rendercv_data_model.cv.name).replace(' ', '_')}_CV.md"
    markdown_file_path = output_directory / markdown_file_name
    markdown_file_object.create_file(markdown_file_path)

    return markdown_file_path


def create_a_typst_file_and_copy_theme_files(
    rendercv_data_model: data.RenderCVDataModel, output_directory: pathlib.Path
) -> pathlib.Path:
    """Render the Typst file with the given data model in the output directory and
    copy the auxiliary theme files to the output directory.

    Args:
        rendercv_data_model: The data model.
        output_directory: Path to the output directory.

    Returns:
        The path to the rendered Typst file.
    """
    file_path = create_a_typst_file(rendercv_data_model, output_directory)
    copy_theme_files_to_output_directory(
        rendercv_data_model.design.theme, output_directory
    )

    # Copy the profile picture to the output directory, if it exists:
    if rendercv_data_model.cv.photo:
        shutil.copyfile(
            rendercv_data_model.cv.photo,
            output_directory / rendercv_data_model.cv.photo.name,
        )

    return file_path


typst_compiler: Optional[typst.Compiler] = None
typst_file_path: pathlib.Path


def setup_typst_compiler(file_path: pathlib.Path) -> typst.Compiler:
    global typst_compiler, typst_file_path  # NOQA: PLW0603
    if typst_compiler is None or typst_file_path != file_path:
        typst_compiler = typst.Compiler(
            file_path, font_paths=rendercv_fonts.paths_to_font_folders
        )
        typst_file_path = file_path

    return typst_compiler


def render_typst(typst_file_contents: str) -> bytes:
    """Render the given Typst file and return the rendered bytes.

    Args:
        typst_file_contents: The Typst file as a string.

    Returns:
        The rendered bytes.
    """
    # create a temporary folder:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = pathlib.Path(temp_dir)
        typst_file_path = temp_dir_path / "temp.typ"
        typst_file_path.write_text(typst_file_contents, encoding="utf-8")

        return typst.compile(typst_file_path, format="pdf")


def render_a_pdf_from_typst(file_path: pathlib.Path) -> pathlib.Path:
    """Run TinyTeX with the given Typst file to render the PDF.

    Args:
        typst_file_path: The path to the Typst file.

    Returns:
        The path to the rendered PDF file.
    """
    typst_compiler = setup_typst_compiler(file_path)

    pdf_output_path = file_path.with_suffix(".pdf")
    typst_compiler.compile(output=pdf_output_path, format="pdf")

    return pdf_output_path


def render_pngs_from_typst(
    file_path: pathlib.Path, ppi: float = 600
) -> list[pathlib.Path]:
    """Run Typst with the given Typst file to render the PNG files.

    Args:
        file_path: The path to the Typst file.
        output_directory: Path to the output directory.
        ppi: Pixels per inch for PNG output, defaults to 600.

    Returns:
        Paths to the rendered PNG files.
    """
    typst_compiler = setup_typst_compiler(file_path)
    output_path = file_path.parent / (file_path.stem + "_{p}.png")
    output = typst_compiler.compile(format="png", ppi=ppi, output=output_path)

    if isinstance(output, list):
        return [
            output_path.parent / output_path.name.format(p=i)
            for i in range(len(output))
        ]

    return [output_path.parent / output_path.name.format(p=1)]


def render_an_html_from_markdown(markdown_file_path: pathlib.Path) -> pathlib.Path:
    """Render an HTML file from a Markdown file with the same name and in the same
    directory. It uses `rendercv/themes/main.j2.html` as the Jinja2 template.

    Args:
        markdown_file_path: The path to the Markdown file.

    Returns:
        The path to the rendered HTML file.
    """
    # check if the file exists:
    if not markdown_file_path.is_file():
        message = f"The file {markdown_file_path} doesn't exist!"
        raise FileNotFoundError(message)

    # Convert the markdown file to HTML:
    markdown_text = markdown_file_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(markdown_text)

    # Get the title of the markdown content:
    title = re.search(r"# (.*)\n", markdown_text)
    title = title.group(1) if title else None

    jinja2_environment = templater.setup_jinja2_environment()
    html_template = jinja2_environment.get_template("main.j2.html")
    html = html_template.render(html_body=html_body, title=title)

    # Write html into a file:
    html_file_path = markdown_file_path.parent / f"{markdown_file_path.stem}.html"
    html_file_path.write_text(html, encoding="utf-8")

    return html_file_path
