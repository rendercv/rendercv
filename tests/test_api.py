import rendercv
import rendercv.old_data


def test_create_contents_of_a_typst_file(input_file_path):
    yaml_string = input_file_path.read_text()
    assert isinstance(
        rendercv.create_contents_of_a_typst_file_from_a_yaml_string(yaml_string), str
    )


def test_create_contents_of_a_typst_file_with_errors(
    rendercv_data_as_python_dictionary,
):
    rendercv_data_as_python_dictionary["cv"]["email"] = "invalid-email"
    yaml_string = rendercv.old_data.generator.dictionary_to_yaml(
        rendercv_data_as_python_dictionary
    )
    assert isinstance(
        rendercv.create_contents_of_a_typst_file_from_a_yaml_string(yaml_string), list
    )


def test_create_a_typst_file_from_a_yaml_string(input_file_path, tmp_path):
    yaml_string = input_file_path.read_text()
    output_file_path = tmp_path / "output.typ"
    errors = rendercv.create_a_typst_file_from_a_yaml_string(
        yaml_string, output_file_path
    )
    assert errors is None
    assert output_file_path.exists()


def test_create_a_typst_file_from_a_python_dictionary(
    rendercv_data_as_python_dictionary, tmp_path
):
    output_file_path = tmp_path / "output.typ"
    errors = rendercv.create_a_typst_file_from_a_python_dictionary(
        rendercv_data_as_python_dictionary, output_file_path
    )
    assert errors is None
    assert output_file_path.exists()


def test_create_contents_of_a_markdown_file_from_a_yaml_string(input_file_path):
    yaml_string = input_file_path.read_text()
    result = rendercv.create_contents_of_a_markdown_file_from_a_yaml_string(yaml_string)
    assert isinstance(result, str)


def test_create_contents_of_a_markdown_file_from_a_python_dictionary(
    rendercv_data_as_python_dictionary,
):
    result = rendercv.create_contents_of_a_markdown_file_from_a_python_dictionary(
        rendercv_data_as_python_dictionary
    )
    assert isinstance(result, str)


def test_create_a_markdown_file_from_a_yaml_string(input_file_path, tmp_path):
    yaml_string = input_file_path.read_text()
    output_file_path = tmp_path / "output.md"
    errors = rendercv.create_a_markdown_file_from_a_yaml_string(
        yaml_string, output_file_path
    )
    assert errors is None
    assert output_file_path.exists()


def test_create_a_markdown_file_from_a_python_dictionary(
    rendercv_data_as_python_dictionary, tmp_path
):
    output_file_path = tmp_path / "output.md"
    errors = rendercv.create_a_markdown_file_from_a_python_dictionary(
        rendercv_data_as_python_dictionary, output_file_path
    )
    assert errors is None
    assert output_file_path.exists()


def test_create_an_html_file_from_a_yaml_string(input_file_path, tmp_path):
    yaml_string = input_file_path.read_text()
    output_file_path = tmp_path / "output.html"
    errors = rendercv.create_an_html_file_from_a_yaml_string(
        yaml_string, output_file_path
    )
    assert errors is None
    assert output_file_path.exists()


def test_create_an_html_file_from_a_python_dictionary(
    rendercv_data_as_python_dictionary, tmp_path
):
    output_file_path = tmp_path / "output.html"
    errors = rendercv.create_an_html_file_from_a_python_dictionary(
        rendercv_data_as_python_dictionary, output_file_path
    )
    assert errors is None
    assert output_file_path.exists()


def test_create_a_pdf_from_a_yaml_string(input_file_path, tmp_path):
    yaml_string = input_file_path.read_text()
    output_file_path = tmp_path / "output.pdf"
    errors = rendercv.create_a_pdf_from_a_yaml_string(yaml_string, output_file_path)
    assert errors is None
    assert output_file_path.exists()


def test_create_a_pdf_from_a_python_dictionary(
    rendercv_data_as_python_dictionary, tmp_path
):
    output_file_path = tmp_path / "output.pdf"
    errors = rendercv.create_a_pdf_from_a_python_dictionary(
        rendercv_data_as_python_dictionary, output_file_path
    )
    assert errors is None
    assert output_file_path.exists()


def test_read_a_python_dictionary_and_return_a_data_model(
    rendercv_data_as_python_dictionary,
):
    result = rendercv.read_a_python_dictionary_and_return_a_data_model(
        rendercv_data_as_python_dictionary
    )
    assert isinstance(result, rendercv.old_data.RenderCVDataModel)


def test_read_a_yaml_string_and_return_a_data_model(input_file_path):
    yaml_string = input_file_path.read_text()
    result = rendercv.read_a_yaml_string_and_return_a_data_model(yaml_string)
    assert isinstance(result, rendercv.old_data.RenderCVDataModel)
