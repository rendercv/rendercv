"""
RenderCV is a Typst-based Python package with a command-line interface (CLI) that allows
you to version-control your CV/resume as source code.
"""

__version__ = "2.3"

from .old_api import (
    create_a_markdown_file_from_a_python_dictionary,
    create_a_markdown_file_from_a_yaml_string,
    create_a_pdf_from_a_python_dictionary,
    create_a_pdf_from_a_yaml_string,
    create_a_typst_file_from_a_python_dictionary,
    create_a_typst_file_from_a_yaml_string,
    create_an_html_file_from_a_python_dictionary,
    create_an_html_file_from_a_yaml_string,
    create_contents_of_a_markdown_file_from_a_python_dictionary,
    create_contents_of_a_markdown_file_from_a_yaml_string,
    create_contents_of_a_typst_file_from_a_python_dictionary,
    create_contents_of_a_typst_file_from_a_yaml_string,
    read_a_python_dictionary_and_return_a_data_model,
    read_a_yaml_string_and_return_a_data_model,
)

__all__ = [
    "create_a_markdown_file_from_a_python_dictionary",
    "create_a_markdown_file_from_a_python_dictionary",
    "create_a_markdown_file_from_a_yaml_string",
    "create_a_pdf_from_a_python_dictionary",
    "create_a_pdf_from_a_yaml_string",
    "create_a_typst_file_from_a_python_dictionary",
    "create_a_typst_file_from_a_yaml_string",
    "create_an_html_file_from_a_python_dictionary",
    "create_an_html_file_from_a_yaml_string",
    "create_contents_of_a_markdown_file_from_a_python_dictionary",
    "create_contents_of_a_markdown_file_from_a_yaml_string",
    "create_contents_of_a_typst_file_from_a_python_dictionary",
    "create_contents_of_a_typst_file_from_a_python_dictionary",
    "create_contents_of_a_typst_file_from_a_yaml_string",
    "read_a_python_dictionary_and_return_a_data_model",
    "read_a_yaml_string_and_return_a_data_model",
]

_partial_install_error_message = (
    "It seems you have a partial installation of RenderCV, so this feature is"
    " unavailable. To enable full functionality, run:\n\npip install"
    ' "rendercv[full]"`'
)
