"""
The `rendercv.api` package contains the functions to create a clean and simple API for
RenderCV.
"""

from .functions import (
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
    "create_contents_of_a_typst_file_from_a_yaml_string",
    "read_a_python_dictionary_and_return_a_data_model",
    "read_a_yaml_string_and_return_a_data_model",
]
