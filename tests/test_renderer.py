import copy
import math
import os
import pathlib
import shutil

import jinja2
import pytest
import time_machine

from rendercv import data_models as dm
from rendercv import renderer as r

folder_name_dictionary = {
    "rendercv_empty_curriculum_vitae_data_model": "empty",
    "rendercv_filled_curriculum_vitae_data_model": "filled",
}


def test_latex_file_class(tmp_path, rendercv_data_model, jinja2_environment):
    latex_file = r.LaTeXFile(rendercv_data_model, jinja2_environment)
    latex_file.get_latex_code()
    latex_file.generate_latex_file(tmp_path / "test.tex")


@pytest.mark.parametrize(
    "string, expected_string",
    [
        (
            "\\textit{This is a \\textit{nested} italic text.}",
            "\\textit{This is a \\textnormal{nested} italic text.}",
        ),
        (
            "\\underline{This is a \\underline{nested} underlined text.}",
            "\\underline{This is a \\textnormal{nested} underlined text.}",
        ),
        (
            "\\textbf{This is a \\textit{nested} bold text.}",
            "\\textbf{This is a \\textit{nested} bold text.}",
        ),
        (
            "\\textbf{This is not} a \\textbf{nested bold text.}",
            "\\textbf{This is not} a \\textbf{nested bold text.}",
        ),
        (
            (
                "\\textbf{This is not} \\textbf{a nested bold text. But it \\textbf{is}"
                " now.}"
            ),
            (
                "\\textbf{This is not} \\textbf{a nested bold text. But it"
                " \\textnormal{is} now.}"
            ),
        ),
        (
            "\\textit{This is a \\underline{nested} italic text.}",
            "\\textit{This is a \\underline{nested} italic text.}",
        ),
        # The two scenarios below doesn't work. I couldn't find a way to implement it:
        # (
        #     "\\textbf{This is a \\textbf{nested} bold \\textbf{text}.}",
        #     (
        #         "\\textbf{This is a \\textnormal{nested} bold"
        #         " \\textnormal{text}.}"
        #     ),
        # ),
        # (
        #     (
        #         "\\textit{This \\textit{is} a \\textbf{n\\textit{ested}} underlined"
        #         " \\textit{text}.}"
        #     ),
        #     (
        #         "\\textit{This \\textnormal{is} a \\textbf{n\\textnormal{ested}}"
        #         " underlined \\textnormal{text}.}"
        #     ),
        # ),
    ],
)
def test_latex_file_revert_nested_latex_style_commands_method(string, expected_string):
    assert r.revert_nested_latex_style_commands(string) == expected_string


def test_markdown_file_class(tmp_path, rendercv_data_model, jinja2_environment):
    latex_file = r.MarkdownFile(rendercv_data_model, jinja2_environment)
    latex_file.get_markdown_code()
    latex_file.generate_markdown_file(tmp_path / "test.tex")


@pytest.mark.parametrize(
    "string, expected_string",
    [
        ("My Text", "My Text"),
        ("My # Text", "My \\# Text"),
        ("My % Text", "My \\% Text"),
        ("My & Text", "My \\& Text"),
        ("My ~ Text", "My \\textasciitilde{} Text"),
        ("##%%&&~~", "\\#\\#\\%\\%\\&\\&\\textasciitilde{}\\textasciitilde{}"),
        (
            (
                "[link_test#](you shouldn't escape whatever is in here & % # ~) [second"
                " link](https://myurl.com)"
            ),
            (
                "[link\\_test\\#](you shouldn't escape whatever is in here & % # ~)"
                " [second link](https://myurl.com)"
            ),
        ),
        ("$a=5_4^3$", "$a=5_4^3$"),
    ],
)
def test_escape_latex_characters_not_strict(string, expected_string):
    assert r.escape_latex_characters(string, strict=False) == expected_string


def test_escape_latex_characters_strict():
    string = "$a=5_4^3$"
    expected_string = "\\$a=5\\_4\\textasciicircum{}3\\$"
    assert r.escape_latex_characters(string, strict=True) == expected_string


@pytest.mark.parametrize(
    "markdown_string, expected_latex_string",
    [
        ("My Text", "My Text"),
        ("**My** Text", "\\textbf{My} Text"),
        ("*My* Text", "\\textit{My} Text"),
        ("***My*** Text", "\\textbf{\\textit{My}} Text"),
        ("[My](https://myurl.com) Text", "\\href{https://myurl.com}{My} Text"),
        ("`My` Text", "`My` Text"),
        (
            "[**My** *Text* ***Is*** `Here`](https://myurl.com)",
            (
                "\\href{https://myurl.com}{\\textbf{My} \\textit{Text}"
                " \\textbf{\\textit{Is}} `Here`}"
            ),
        ),
        (
            "Some other *** tests, which should be tricky* to parse!**",
            "Some other \\textbf{\\textit{ tests, which should be tricky} to parse!}",
        ),
    ],
)
def test_markdown_to_latex(markdown_string, expected_latex_string):
    assert r.markdown_to_latex(markdown_string) == expected_latex_string


def test_transform_markdown_sections_to_latex_sections(rendercv_data_model):
    new_data_model = copy.deepcopy(rendercv_data_model)
    new_sections_input = r.transform_markdown_sections_to_latex_sections(
        new_data_model.cv.sections_input
    )
    new_data_model.cv.sections_input = new_sections_input

    assert isinstance(new_data_model, dm.RenderCVDataModel)
    assert new_data_model.cv.name == rendercv_data_model.cv.name
    assert new_data_model.design == rendercv_data_model.design
    assert new_data_model.cv.sections != rendercv_data_model.cv.sections


@pytest.mark.parametrize(
    "string, placeholders, expected_string",
    [
        ("Hello, {name}!", {"{name}": None}, "Hello, None!"),
        (
            "{greeting}, {name}!",
            {"{greeting}": "Hello", "{name}": "World"},
            "Hello, World!",
        ),
        ("No placeholders here.", {}, "No placeholders here."),
        (
            "{missing} placeholder.",
            {"{not_missing}": "value"},
            "{missing} placeholder.",
        ),
        ("", {"{placeholder}": "value"}, ""),
    ],
)
def test_replace_placeholders_with_actual_values(string, placeholders, expected_string):
    result = r.replace_placeholders_with_actual_values(string, placeholders)
    assert result == expected_string


@pytest.mark.parametrize(
    "value, something, match_str, expected",
    [
        ("Hello World", "textbf", None, "\\textbf{Hello World}"),
        ("Hello World", "textbf", "World", "Hello \\textbf{World}"),
        ("Hello World", "textbf", "Universe", "Hello World"),
        ("", "textbf", "Universe", ""),
        ("Hello World", "textbf", "", "Hello World"),
    ],
)
def test_make_matched_part_something(value, something, match_str, expected):
    result = r.make_matched_part_something(value, something, match_str)
    assert result == expected


@pytest.mark.parametrize(
    "value, match_str, expected",
    [
        ("Hello World", None, "\\textbf{Hello World}"),
        ("Hello World", "World", "Hello \\textbf{World}"),
        ("Hello World", "Universe", "Hello World"),
        ("", "Universe", ""),
        ("Hello World", "", "Hello World"),
    ],
)
def test_make_matched_part_bold(value, match_str, expected):
    result = r.make_matched_part_bold(value, match_str)
    assert result == expected


@pytest.mark.parametrize(
    "value, match_str, expected",
    [
        ("Hello World", None, "\\underline{Hello World}"),
        ("Hello World", "World", "Hello \\underline{World}"),
        ("Hello World", "Universe", "Hello World"),
        ("", "Universe", ""),
        ("Hello World", "", "Hello World"),
    ],
)
def test_make_matched_part_underlined(value, match_str, expected):
    result = r.make_matched_part_underlined(value, match_str)
    assert result == expected


@pytest.mark.parametrize(
    "value, match_str, expected",
    [
        ("Hello World", None, "\\textit{Hello World}"),
        ("Hello World", "World", "Hello \\textit{World}"),
        ("Hello World", "Universe", "Hello World"),
        ("", "Universe", ""),
        ("Hello World", "", "Hello World"),
    ],
)
def test_make_matched_part_italic(value, match_str, expected):
    result = r.make_matched_part_italic(value, match_str)
    assert result == expected


@pytest.mark.parametrize(
    "value, match_str, expected",
    [
        ("Hello World", None, "\\mbox{Hello World}"),
        ("Hello World", "World", "Hello \\mbox{World}"),
        ("Hello World", "Universe", "Hello World"),
        ("", "Universe", ""),
        ("Hello World", "", "Hello World"),
    ],
)
def test_make_matched_part_non_line_breakable(value, match_str, expected):
    result = r.make_matched_part_non_line_breakable(value, match_str)
    assert result == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("John Doe", "J. Doe"),
        ("John Jacob Jingleheimer Schmidt", "J. J. J. Schmidt"),
        ("SingleName", "SingleName"),
        ("", ""),
        (None, ""),
    ],
)
def test_abbreviate_name(name, expected):
    result = r.abbreviate_name(name)
    assert result == expected


@pytest.mark.parametrize(
    "length, divider, expected",
    [
        ("10pt", 2, "5.0pt"),
        ("15cm", 3, "5.0cm"),
        ("20mm", 4, "5.0mm"),
        ("25ex", 5, "5.0ex"),
        ("30em", 6, "5.0em"),
        ("10pt", 3, "3.33pt"),
        ("10pt", 4, "2.5pt"),
        ("0pt", 1, "0.0pt"),
    ],
)
def test_divide_length_by(length, divider, expected):
    result = r.divide_length_by(length, divider)
    assert math.isclose(
        float(result[:-2]), float(expected[:-2]), rel_tol=1e-2
    ), f"Expected {expected}, but got {result}"


@pytest.mark.parametrize(
    "length, divider",
    [("10pt", 0), ("10pt", -1), ("invalid", 4)],
)
def test_invalid_divide_length_by(length, divider):
    with pytest.raises(ValueError):
        r.divide_length_by(length, divider)


def test_get_an_item_with_a_specific_attribute_value():
    entry_objects = [
        dm.OneLineEntry(
            label="Test1",
            details="Test2",
        ),
        dm.OneLineEntry(
            label="Test3",
            details="Test4",
        ),
    ]
    result = r.get_an_item_with_a_specific_attribute_value(
        entry_objects, "label", "Test3"
    )
    assert result == entry_objects[1]
    result = r.get_an_item_with_a_specific_attribute_value(
        entry_objects, "label", "DoesntExist"
    )
    assert result is None

    with pytest.raises(AttributeError):
        r.get_an_item_with_a_specific_attribute_value(entry_objects, "invalid", "Test5")


def test_setup_jinja2_environment():
    env = r.setup_jinja2_environment()

    # Check if returned object is a jinja2.Environment instance
    assert isinstance(env, jinja2.Environment)

    # Check if custom delimiters are correctly set
    assert env.block_start_string == "((*"
    assert env.block_end_string == "*))"
    assert env.variable_start_string == "<<"
    assert env.variable_end_string == ">>"
    assert env.comment_start_string == "((#"
    assert env.comment_end_string == "#))"

    # Check if custom filters are correctly set
    assert "make_it_bold" in env.filters
    assert "make_it_underlined" in env.filters
    assert "make_it_italic" in env.filters
    assert "make_it_nolinebreak" in env.filters
    assert "make_it_something" in env.filters
    assert "divide_length_by" in env.filters
    assert "abbreviate_name" in env.filters
    assert "get_an_item_with_a_specific_attribute_value" in env.filters


@pytest.mark.parametrize(
    "theme_name",
    dm.available_themes,
)
@pytest.mark.parametrize(
    "curriculum_vitae_data_model",
    [
        "rendercv_empty_curriculum_vitae_data_model",
        "rendercv_filled_curriculum_vitae_data_model",
    ],
)
@time_machine.travel("2024-01-01")
def test_generate_latex_file(
    run_a_function_and_check_if_output_is_the_same_as_reference,
    request: pytest.FixtureRequest,
    theme_name,
    curriculum_vitae_data_model,
):
    cv_data_model = request.getfixturevalue(curriculum_vitae_data_model)
    data_model = dm.RenderCVDataModel(
        cv=cv_data_model,
        design={"theme": theme_name},
    )

    output_file_name = f"{str(cv_data_model.name).replace(' ', '_')}_CV.tex"
    reference_file_name = (
        f"{theme_name}_{folder_name_dictionary[curriculum_vitae_data_model]}.tex"
    )

    def generate_latex_file(output_directory_path, reference_file_or_directory_path):
        r.generate_latex_file(data_model, output_directory_path)

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        generate_latex_file,
        reference_file_name,
        output_file_name,
    )


def test_if_generate_latex_file_can_create_a_new_directory(
    tmp_path, rendercv_data_model
):
    new_directory = tmp_path / "new_directory"

    latex_file_path = r.generate_latex_file(rendercv_data_model, new_directory)

    assert latex_file_path.exists()


@pytest.mark.parametrize(
    "theme_name",
    dm.available_themes,
)
@pytest.mark.parametrize(
    "curriculum_vitae_data_model",
    [
        "rendercv_empty_curriculum_vitae_data_model",
        "rendercv_filled_curriculum_vitae_data_model",
    ],
)
@time_machine.travel("2024-01-01")
def test_generate_markdown_file(
    run_a_function_and_check_if_output_is_the_same_as_reference,
    request: pytest.FixtureRequest,
    theme_name,
    curriculum_vitae_data_model,
):
    cv_data_model = request.getfixturevalue(curriculum_vitae_data_model)
    data_model = dm.RenderCVDataModel(
        cv=cv_data_model,
        design={"theme": theme_name},
    )

    output_file_name = f"{str(cv_data_model.name).replace(' ', '_')}_CV.md"
    reference_file_name = (
        f"{theme_name}_{folder_name_dictionary[curriculum_vitae_data_model]}.md"
    )

    def generate_markdown_file(output_directory_path, reference_file_or_directory_path):
        r.generate_markdown_file(data_model, output_directory_path)

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        generate_markdown_file,
        reference_file_name,
        output_file_name,
    )


def test_if_generate_markdown_file_can_create_a_new_directory(
    tmp_path, rendercv_data_model
):
    new_directory = tmp_path / "new_directory"

    latex_file_path = r.generate_markdown_file(rendercv_data_model, new_directory)

    assert latex_file_path.exists()


@pytest.mark.parametrize(
    "theme_name",
    dm.available_themes,
)
def test_copy_theme_files_to_output_directory(
    run_a_function_and_check_if_output_is_the_same_as_reference, theme_name
):
    reference_directory_name = theme_name

    def copy_theme_files_to_output_directory(
        output_directory_path, reference_file_or_directory_path
    ):
        r.copy_theme_files_to_output_directory(theme_name, output_directory_path)

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        copy_theme_files_to_output_directory,
        reference_directory_name,
    )


def test_copy_theme_files_to_output_directory_custom_theme(
    run_a_function_and_check_if_output_is_the_same_as_reference,
):
    theme_name = "dummytheme"
    reference_directory_name = f"{theme_name}_auxiliary_files"

    # Update the auxiliary files if update_testdata is True
    def update_reference_files(reference_directory_path):
        dummytheme_path = reference_directory_path.parent / theme_name

        # Create dummytheme:
        if not dummytheme_path.exists():
            dummytheme_path.mkdir(parents=True, exist_ok=True)

        # Create txt file called test.txt in the custom theme directory:
        for entry_type_name in dm.entry_type_names:
            pathlib.Path(dummytheme_path / f"{entry_type_name}.j2.tex").touch()

        pathlib.Path(dummytheme_path / "Header.j2.tex").touch()
        pathlib.Path(dummytheme_path / "Preamble.j2.tex").touch()
        pathlib.Path(dummytheme_path / "SectionBeginning.j2.tex").touch()
        pathlib.Path(dummytheme_path / "SectionEnding.j2.tex").touch()
        pathlib.Path(dummytheme_path / "theme_auxiliary_file.cls").touch()
        pathlib.Path(dummytheme_path / "theme_auxiliary_dir").mkdir(exist_ok=True)
        pathlib.Path(
            dummytheme_path / "theme_auxiliary_dir" / "theme_auxiliary_file.txt"
        ).touch()
        init_file = pathlib.Path(dummytheme_path / "__init__.py")

        init_file.touch()
        init_file.write_text(
            "from typing import Literal\n\nimport pydantic\n\n\nclass"
            " DummythemeThemeOptions(pydantic.BaseModel):\n    theme:"
            " Literal['dummytheme']\n"
        )

        # Create reference_directory_path
        os.chdir(dummytheme_path.parent)
        r.copy_theme_files_to_output_directory(
            theme_name=theme_name,
            output_directory_path=reference_directory_path,
        )

    def copy_theme_files_to_output_directory(
        output_directory_path, reference_directory_path
    ):
        dummytheme_path = reference_directory_path.parent / theme_name

        # Copy auxiliary theme files to tmp_path
        os.chdir(dummytheme_path.parent)
        r.copy_theme_files_to_output_directory(
            theme_name=theme_name,
            output_directory_path=output_directory_path,
        )

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        function=copy_theme_files_to_output_directory,
        reference_file_or_directory_name=reference_directory_name,
        generate_reference_files_function=update_reference_files,
    )


def test_copy_theme_files_to_output_directory_nonexistent_theme():
    with pytest.raises(FileNotFoundError):
        r.copy_theme_files_to_output_directory("nonexistent_theme", pathlib.Path("."))


@pytest.mark.parametrize(
    "theme_name",
    dm.available_themes,
)
@pytest.mark.parametrize(
    "curriculum_vitae_data_model",
    [
        "rendercv_empty_curriculum_vitae_data_model",
        "rendercv_filled_curriculum_vitae_data_model",
    ],
)
@time_machine.travel("2024-01-01")
def test_generate_latex_file_and_copy_theme_files(
    run_a_function_and_check_if_output_is_the_same_as_reference,
    request: pytest.FixtureRequest,
    theme_name,
    curriculum_vitae_data_model,
):
    reference_directory_name = (
        f"{theme_name}_{folder_name_dictionary[curriculum_vitae_data_model]}"
    )

    data_model = dm.RenderCVDataModel(
        cv=request.getfixturevalue(curriculum_vitae_data_model),
        design={"theme": theme_name},
    )

    def generate_latex_file_and_copy_theme_files(
        output_directory_path, reference_file_or_directory_path
    ):
        r.generate_latex_file_and_copy_theme_files(data_model, output_directory_path)

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        generate_latex_file_and_copy_theme_files,
        reference_directory_name,
    )


@pytest.mark.parametrize(
    "theme_name",
    dm.available_themes,
)
@pytest.mark.parametrize(
    "curriculum_vitae_data_model",
    [
        "rendercv_empty_curriculum_vitae_data_model",
        "rendercv_filled_curriculum_vitae_data_model",
    ],
)
@time_machine.travel("2024-01-01")
def test_latex_to_pdf(
    request: pytest.FixtureRequest,
    run_a_function_and_check_if_output_is_the_same_as_reference,
    theme_name,
    curriculum_vitae_data_model,
):
    name = request.getfixturevalue(curriculum_vitae_data_model).name
    name = str(name).replace(" ", "_")

    output_file_name = f"{name}_CV.pdf"
    reference_name = (
        f"{theme_name}_{folder_name_dictionary[curriculum_vitae_data_model]}"
    )
    reference_file_name = f"{reference_name}.pdf"

    def generate_pdf_file(output_directory_path, reference_file_or_directory_path):
        latex_sources_path = (
            reference_file_or_directory_path.parent.parent
            / "test_generate_latex_file_and_copy_theme_files"
            / reference_name
        )

        # Copy LaTeX sources to output path
        shutil.copytree(latex_sources_path, output_directory_path, dirs_exist_ok=True)

        # Convert LaTeX code to PDF
        r.latex_to_pdf(output_directory_path / f"{name}_CV.tex")

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        function=generate_pdf_file,
        reference_file_or_directory_name=reference_file_name,
        output_file_name=output_file_name,
    )


def test_latex_to_pdf_nonexistent_latex_file():
    with pytest.raises(FileNotFoundError):
        file_path = pathlib.Path("file_doesnt_exist.tex")
        r.latex_to_pdf(file_path)


@pytest.mark.parametrize(
    "theme_name",
    dm.available_themes,
)
@pytest.mark.parametrize(
    "curriculum_vitae_data_model",
    [
        "rendercv_empty_curriculum_vitae_data_model",
        "rendercv_filled_curriculum_vitae_data_model",
    ],
)
@time_machine.travel("2024-01-01")
def test_markdown_to_html(
    run_a_function_and_check_if_output_is_the_same_as_reference,
    theme_name,
    curriculum_vitae_data_model,
):
    reference_name = (
        f"{theme_name}_{folder_name_dictionary[curriculum_vitae_data_model]}"
    )
    output_file_name = f"{reference_name}.html"
    reference_file_name = f"{reference_name}.html"

    def markdown_to_html(output_directory_path, reference_file_or_directory_path):
        markdown_file_name = f"{reference_name}.md"

        markdown_source_path = (
            reference_file_or_directory_path.parent.parent
            / "test_generate_markdown_file"
            / markdown_file_name
        )

        # Copy markdown source to output path
        shutil.copy(markdown_source_path, output_directory_path)

        # Convert markdown to html
        r.markdown_to_html(output_directory_path / markdown_file_name)

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        function=markdown_to_html,
        reference_file_or_directory_name=reference_file_name,
        output_file_name=output_file_name,
    )


def test_markdown_to_html_nonexistent_markdown_file():
    with pytest.raises(FileNotFoundError):
        file_path = pathlib.Path("file_doesnt_exist.md")
        r.markdown_to_html(file_path)


def test_pdf_to_pngs_single_page(
    run_a_function_and_check_if_output_is_the_same_as_reference,
):
    output_file_name = "classic_empty_1.png"
    reference_file_name = "classic_empty.png"

    def generate_pngs(output_directory_path, reference_file_or_directory_path):
        pdf_file_name = "classic_empty.pdf"

        pdf_path = (
            reference_file_or_directory_path.parent.parent
            / "test_latex_to_pdf"
            / pdf_file_name
        )

        # Copy markdown source to output path
        shutil.copy(pdf_path, output_directory_path)

        # Convert PDF to PNGs
        r.pdf_to_pngs(output_directory_path / pdf_file_name)

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        generate_pngs,
        reference_file_or_directory_name=reference_file_name,
        output_file_name=output_file_name,
    )


def test_pdf_to_pngs(
    run_a_function_and_check_if_output_is_the_same_as_reference,
):
    reference_directory_name = "pngs"

    def generate_pngs(output_directory_path, reference_file_or_directory_path):
        pdf_file_name = "classic_filled.pdf"

        pdf_path = (
            reference_file_or_directory_path.parent.parent
            / "test_latex_to_pdf"
            / pdf_file_name
        )

        # Copy markdown source to output path
        shutil.copy(pdf_path, output_directory_path)

        # Convert PDF to PNGs
        r.pdf_to_pngs(output_directory_path / pdf_file_name)

        # Remove PDF file
        (output_directory_path / pdf_file_name).unlink()

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        generate_pngs,
        reference_directory_name,
    )


def test_pdf_to_png_nonexistent_pdf_file():
    with pytest.raises(FileNotFoundError):
        file_path = pathlib.Path("file_doesnt_exist.pdf")
        r.pdf_to_pngs(file_path)
