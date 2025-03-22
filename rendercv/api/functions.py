"""
The `rendercv.api.functions` package contains the basic functions that are used to
interact with the RenderCV.
"""

import pathlib
import shutil
import tempfile
from collections.abc import Callable
from typing import Optional

import pydantic

from .. import data, renderer


def _create_contents_of_a_something_from_something(
    input: dict | str, parser: Callable, renderer: Callable
) -> str | list[dict]:
    """
    Validate the input, generate a file and return it as a string. If there are any
    validation errors, return them as a list of dictionaries.

    Args:
        input: The input file as a dictionary or a string.
        parser: The parser function.
        renderer: The renderer function.

    Returns:
        The file as a string or a list of dictionaries that contain the error messages,
            locations, and the input values.
    """
    try:
        data_model = parser(input)
    except pydantic.ValidationError as e:
        if isinstance(input, str):
            return data.parse_validation_errors(e, input)
        return data.parse_validation_errors(e)

    return renderer(data_model)


def _create_a_file_from_something(
    input: dict | str,
    parser: Callable,
    renderer: Callable,
    output_file_path: pathlib.Path,
) -> Optional[list[dict]]:
    """
    Validate the input, generate a file and save it to the output file path.

    Args:
        input: The input file as a dictionary or a string.
        parser: The parser function.
        renderer: The renderer function.
        output_file_path: The output file path.

    Returns:
        The output file path.
    """
    try:
        data_model = parser(input)
    except pydantic.ValidationError as e:
        return data.parse_validation_errors(e)

    with tempfile.TemporaryDirectory() as temp_dir:
        temporary_output_path = pathlib.Path(temp_dir)
        file = renderer(data_model, temporary_output_path)
        shutil.move(file, output_file_path)

    return None


def read_a_python_dictionary_and_return_a_data_model(
    input_file_as_a_dict: dict,
) -> data.RenderCVDataModel:
    """
    Validate the input dictionary and return the data model.

    Args:
        input_file_as_a_dict: The input file as a dictionary.

    Returns:
        The data model.
    """
    return data.validate_input_dictionary_and_return_the_data_model(
        input_file_as_a_dict,
    )


def read_a_yaml_string_and_return_a_data_model(
    yaml_file_as_string: str,
) -> data.RenderCVDataModel:
    """
    Validate the YAML input file given as a string and return the data model.

    Args:
        yaml_file_as_string: The input file as a string.

    Returns:
        The data model.
    """
    input_file_as_a_dict = data.read_a_yaml_file(yaml_file_as_string)
    return read_a_python_dictionary_and_return_a_data_model(input_file_as_a_dict)


def create_contents_of_a_typst_file_from_a_python_dictionary(
    input_file_as_a_dict: dict,
) -> str | list[dict]:
    """
    Validate the input dictionary, generate a Typst file and return it as a string. If
    there are any validation errors, return them as a list of dictionaries.

    Args:
        input_file_as_a_dict: The input file as a dictionary.

    Returns:
        The Typst file as a string or a list of dictionaries that contain the error
            messages, locations, and the input values.
    """
    return _create_contents_of_a_something_from_something(
        input_file_as_a_dict,
        read_a_python_dictionary_and_return_a_data_model,
        renderer.create_contents_of_a_typst_file,
    )


def create_contents_of_a_typst_file_from_a_yaml_string(
    yaml_file_as_string: str,
) -> str | list[dict]:
    """
    Validate the YAML input file given as a string, generate a Typst file and return it
    as a string. If there are any validation errors, return them as a list of
    dictionaries.

    Args:
        yaml_file_as_string: The input file as a string.

    Returns:
        The Typst file as a string or a list of dictionaries that contain the error
            messages, locations, and the input values.
    """
    return _create_contents_of_a_something_from_something(
        yaml_file_as_string,
        read_a_yaml_string_and_return_a_data_model,
        renderer.create_contents_of_a_typst_file,
    )


def create_contents_of_a_markdown_file_from_a_python_dictionary(
    input_file_as_a_dict: dict,
) -> str | list[dict]:
    """
    Validate the input dictionary, generate a Markdown file and return it as a string.
    If there are any validation errors, return them as a list of dictionaries.

    Args:
        input_file_as_a_dict: The input file as a dictionary.

    Returns:
        The Markdown file as a string or a list of dictionaries that contain the error
            messages, locations, and the input values.
    """
    return _create_contents_of_a_something_from_something(
        input_file_as_a_dict,
        read_a_python_dictionary_and_return_a_data_model,
        renderer.create_contents_of_a_markdown_file,
    )


def create_contents_of_a_markdown_file_from_a_yaml_string(
    yaml_file_as_string: str,
) -> str | list[dict]:
    """
    Validate the input file given as a string, generate a Markdown file and return it as
    a string. If there are any validation errors, return them as a list of dictionaries.

    Args:
        yaml_file_as_string: The input file as a string.

    Returns:
        The Markdown file as a string or a list of dictionaries that contain the error
            messages, locations, and the input values.
    """
    return _create_contents_of_a_something_from_something(
        yaml_file_as_string,
        read_a_yaml_string_and_return_a_data_model,
        renderer.create_contents_of_a_markdown_file,
    )


def create_a_typst_file_from_a_yaml_string(
    yaml_file_as_string: str,
    output_file_path: pathlib.Path,
) -> Optional[list[dict]]:
    """
    Validate the input file given as a string, generate a Typst file and save it to the
    output file path.

    Args:
        yaml_file_as_string: The input file as a string.
        output_file_path: The output file path.

    Returns:
        The output file path.
    """

    return _create_a_file_from_something(
        yaml_file_as_string,
        read_a_yaml_string_and_return_a_data_model,
        renderer.create_a_typst_file,
        output_file_path,
    )


def create_a_typst_file_from_a_python_dictionary(
    input_file_as_a_dict: dict,
    output_file_path: pathlib.Path,
) -> Optional[list[dict]]:
    """
    Validate the input dictionary, generate a Typst file and save it to the output file
    path.

    Args:
        input_file_as_a_dict: The input file as a dictionary.
        output_file_path: The output file path.

    Returns:
        The output file path.
    """
    return _create_a_file_from_something(
        input_file_as_a_dict,
        read_a_python_dictionary_and_return_a_data_model,
        renderer.create_a_typst_file,
        output_file_path,
    )


def create_a_markdown_file_from_a_python_dictionary(
    input_file_as_a_dict: dict,
    output_file_path: pathlib.Path,
) -> Optional[list[dict]]:
    """
    Validate the input dictionary, generate a Markdown file and save it to the output
    file path.

    Args:
        input_file_as_a_dict: The input file as a dictionary.
        output_file_path: The output file path.

    Returns:
        The output file path.
    """
    return _create_a_file_from_something(
        input_file_as_a_dict,
        read_a_python_dictionary_and_return_a_data_model,
        renderer.create_a_markdown_file,
        output_file_path,
    )


def create_a_markdown_file_from_a_yaml_string(
    yaml_file_as_string: str,
    output_file_path: pathlib.Path,
) -> Optional[list[dict]]:
    """
    Validate the input file given as a string, generate a Markdown file and save it to
    the output file path.

    Args:
        yaml_file_as_string: The input file as a string.
        output_file_path: The output file path.

    Returns:
        The output file path.
    """
    return _create_a_file_from_something(
        yaml_file_as_string,
        read_a_yaml_string_and_return_a_data_model,
        renderer.create_a_markdown_file,
        output_file_path,
    )


def create_an_html_file_from_a_python_dictionary(
    input_file_as_a_dict: dict,
    output_file_path: pathlib.Path,
) -> Optional[list[dict]]:
    """
    Validate the input dictionary, generate an HTML file and save it to the output file
    path.

    Args:
        input_file_as_a_dict: The input file as a dictionary.
        output_file_path: The output file path.

    Returns:
        The output file path.
    """
    return _create_a_file_from_something(
        input_file_as_a_dict,
        read_a_python_dictionary_and_return_a_data_model,
        lambda x, y: renderer.render_an_html_from_markdown(
            renderer.create_a_markdown_file(x, y),
        ),
        output_file_path,
    )


def create_an_html_file_from_a_yaml_string(
    yaml_file_as_string: str,
    output_file_path: pathlib.Path,
) -> Optional[list[dict]]:
    """
    Validate the input file given as a string, generate an HTML file and save it to the
    output file path.

    Args:
        yaml_file_as_string: The input file as a string.
        output_file_path: The output file path.

    Returns:
        The output file path.
    """
    return _create_a_file_from_something(
        yaml_file_as_string,
        read_a_yaml_string_and_return_a_data_model,
        lambda x, y: renderer.render_an_html_from_markdown(
            renderer.create_a_markdown_file(x, y),
        ),
        output_file_path,
    )


def create_a_pdf_from_a_yaml_string(
    yaml_file_as_string: str,
    output_file_path: pathlib.Path,
) -> Optional[list[dict]]:
    """
    Validate the input file given as a string, generate a PDF file and save it to the
    output file path.

    Args:
        yaml_file_as_string: The input file as a string.
        output_file_path: The output file path.

    Returns:
        The output file path.
    """
    return _create_a_file_from_something(
        yaml_file_as_string,
        read_a_yaml_string_and_return_a_data_model,
        lambda x, y: renderer.render_a_pdf_from_typst(
            renderer.create_a_typst_file(x, y)
        ),
        output_file_path,
    )


def create_a_pdf_from_a_python_dictionary(
    input_file_as_a_dict: dict,
    output_file_path: pathlib.Path,
) -> Optional[list[dict]]:
    """
    Validate the input dictionary, generate a PDF file and save it to the output file
    path.

    Args:
        input_file_as_a_dict: The input file as a dictionary.
        output_file_path: The output file path.

    Returns:
        The output file path.
    """
    return _create_a_file_from_something(
        input_file_as_a_dict,
        read_a_python_dictionary_and_return_a_data_model,
        lambda x, y: renderer.render_a_pdf_from_typst(
            renderer.create_a_typst_file(x, y),
        ),
        output_file_path,
    )
