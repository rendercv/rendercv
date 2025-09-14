import copy
import os
import pathlib
import shutil

import jinja2
import pytest

from rendercv import data, renderer
from rendercv.renderer import renderer as renderer_module
from rendercv.renderer import templater

folder_name_dictionary = {
    "rendercv_empty_curriculum_vitae_data_model": "empty",
    "rendercv_filled_curriculum_vitae_data_model": "filled",
}


def test_typst_file_class(tmp_path, rendercv_data_model, jinja2_environment):
    typst_file = templater.TypstFile(rendercv_data_model, jinja2_environment)
    typst_file.get_full_code()
    typst_file.create_file(tmp_path / "test.typ")


def test_markdown_file_class(tmp_path, rendercv_data_model, jinja2_environment):
    typst_file = templater.MarkdownFile(rendercv_data_model, jinja2_environment)
    typst_file.get_full_code()
    typst_file.create_file(tmp_path / "test.typ")


@pytest.mark.parametrize(
    ("string", "expected_string"),
    [
        ("My Text", "My Text"),
        ("My # Text", "My \\# Text"),
        ("My % Text", "My \\% Text"),
        ("My ~ Text", "My \\~ Text"),
        ("My _ Text", "My \\_ Text"),
        ("My $ Text", "My \\$ Text"),
        ("My [ Text", "My \\[ Text"),
        ("My ] Text", "My \\] Text"),
        ("My ( Text", "My \\( Text"),
        ("My ) Text", "My \\) Text"),
        ("My \\ Text", "My \\\\ Text"),
        ('My " Text', 'My \\" Text'),
        ("My @ Text", "My \\@ Text"),
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
        (
            "$$a=5_4^3 % & #$$ # $$aaaa ___ &&$$",
            "$a=5_4^3 % & #$ \\# $aaaa ___ &&$",
        ),
        (
            "$###$////",
            "\\$\\#\\#\\#\\$\\/\\/\\/\\/",
        ),
        (
            "#test-typst-command[argument]",
            "#test-typst-command[argument]",
        ),
    ],
)
def test_escape_typst_characters(string, expected_string):
    assert templater.escape_typst_characters(string) == expected_string


@pytest.mark.parametrize(
    ("markdown_string", "expected_typst_string"),
    [
        ("My Text", "My Text"),
        ("**My** Text", "#strong[My] Text"),
        ("*My* Text", "#emph[My] Text"),
        ("***My*** Text", "#strong[#emph[My]] Text"),
        ("[My](https://myurl.com) Text", '#link("https://myurl.com")[My] Text'),
        ("`My` Text", "`My` Text"),
        (
            "[**My** *Text* ***Is*** `Here`](https://myurl.com)",
            (
                '#link("https://myurl.com")[#strong[My] #emph[Text] #strong[#emph[Is]]'
                " `Here`]"
            ),
        ),
        (
            "Some other *** tests, which should be tricky* to parse!**",
            "Some other #strong[#emph[ tests, which should be tricky] to parse!]",
        ),
        (
            "One asterisk does not a quote* maketh",
            "One asterisk does not a quote#sym.ast.basic maketh",
        ),
        (
            "We can put asteri*sks in the middle of words",
            (
                "We can put asteri#sym.ast.basic#h(0pt, weak: true) sks in the middle"
                " of words"
            ),
        ),
        (
            (
                "If we want to escape \\*'s such that they don't become bold, we use a"
                " backslash: \\*"
            ),
            (
                "If we want to escape #sym.ast.basic#h(0pt, weak: true) 's such that"
                " they don't become bold, we use a backslash: #sym.ast.basic#h(0pt,"
                " weak: true) "
            ),
        ),
        (
            "Asterisk with a space after it does not need a zero-width space: * test",
            (
                "Asterisk with a space after it does not need a zero-width space:"
                " #sym.ast.basic test"
            ),
        ),
        (
            "Asterisk with a space after it does not need a zero-width space: *test",
            (
                "Asterisk with a space after it does not need a zero-width space:"
                " #sym.ast.basic#h(0pt, weak: true) test"
            ),
        ),
        (
            "\\* Asterisk should not be escaped\\*.Hey?",
            (
                "#sym.ast.basic Asterisk should not be escaped#sym.ast.basic#h(0pt,"
                " weak: true) .Hey?"
            ),
        ),
        (
            "I would like to not have any \\*\\*bold\\*\\* text",
            (
                "I would like to not have any #sym.ast.basic#h(0pt, weak: true)"
                " #sym.ast.basic#h(0pt, weak: true) bold#sym.ast.basic#h(0pt,"
                " weak: true) #sym.ast.basic text"
            ),
        ),
        (
            "Keep Typst commands #test-typst-command[argument] as they are.",
            "Keep Typst commands #test-typst-command[argument] as they are.",
        ),
    ],
)
def test_markdown_to_typst(markdown_string, expected_typst_string):
    assert templater.markdown_to_typst(markdown_string) == expected_typst_string


def test_transform_markdown_sections_to_typst_sections(rendercv_data_model):
    new_data_model = copy.deepcopy(rendercv_data_model)
    new_sections_input = templater.transform_markdown_sections_to_typst_sections(
        new_data_model.cv.sections_input
    )
    new_data_model.cv.sections_input = new_sections_input

    assert isinstance(new_data_model, data.RenderCVDataModel)
    assert new_data_model.cv.name == rendercv_data_model.cv.name
    assert new_data_model.design == rendercv_data_model.design
    assert new_data_model.cv.sections != rendercv_data_model.cv.sections


@pytest.mark.parametrize(
    ("string", "placeholders", "expected_string"),
    [
        ("Hello, {name}!", {"{name}": None}, "Hello, !"),
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
    result = templater.replace_placeholders_with_actual_values(string, placeholders)
    assert result == expected_string


def test_setup_jinja2_environment():
    env = templater.Jinja2Environment().environment

    # Check if the returned object is a jinja2.Environment instance
    assert isinstance(env, jinja2.Environment)

    # Check if the custom delimiters are correctly set
    assert env.block_start_string == "((*"
    assert env.block_end_string == "*))"
    assert env.variable_start_string == "<<"
    assert env.variable_end_string == ">>"
    assert env.comment_start_string == "((#"
    assert env.comment_end_string == "#))"


@pytest.mark.parametrize(
    "theme_name",
    data.available_themes,
)
@pytest.mark.parametrize(
    "curriculum_vitae_data_model",
    [
        "rendercv_empty_curriculum_vitae_data_model",
        "rendercv_filled_curriculum_vitae_data_model",
    ],
)
def test_create_a_typst_file(
    run_a_function_and_check_if_output_is_the_same_as_reference,
    request: pytest.FixtureRequest,
    theme_name,
    curriculum_vitae_data_model,
):
    cv_data_model = request.getfixturevalue(curriculum_vitae_data_model)
    data_model = data.RenderCVDataModel(
        cv=cv_data_model,
        design={"theme": theme_name},
        rendercv_settings=data.RenderCVSettings(date="2024-01-01"),  # type: ignore
    )
    output_file_name = f"{str(cv_data_model.name).replace(' ', '_')}_CV.typ"
    reference_file_name = (
        f"{theme_name}_{folder_name_dictionary[curriculum_vitae_data_model]}.typ"
    )
    if theme_name in data.available_themes:
        output_file_name = output_file_name.replace(".typ", ".typ")
        reference_file_name = reference_file_name.replace(".typ", ".typ")

    def create_a_typst_file(output_directory_path, _):
        renderer.create_a_typst_file(data_model, output_directory_path)

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        create_a_typst_file,
        reference_file_name,
        output_file_name,
    )


def test_if_create_a_typst_file_can_create_a_new_directory(
    tmp_path, rendercv_data_model
):
    new_directory = tmp_path / "new_directory"

    typst_file_path = renderer.create_a_typst_file(rendercv_data_model, new_directory)

    assert typst_file_path.exists()


@pytest.mark.parametrize(
    "theme_name",
    data.available_themes,
)
@pytest.mark.parametrize(
    "curriculum_vitae_data_model",
    [
        "rendercv_empty_curriculum_vitae_data_model",
        "rendercv_filled_curriculum_vitae_data_model",
    ],
)
def test_create_a_markdown_file(
    run_a_function_and_check_if_output_is_the_same_as_reference,
    request: pytest.FixtureRequest,
    theme_name,
    curriculum_vitae_data_model,
):
    data.RenderCVSettings(date="2024-01-01")  # type: ignore
    cv_data_model = request.getfixturevalue(curriculum_vitae_data_model)
    data_model = data.RenderCVDataModel(
        cv=cv_data_model,
        design={"theme": theme_name},
    )

    output_file_name = f"{str(cv_data_model.name).replace(' ', '_')}_CV.md"
    reference_file_name = (
        f"{theme_name}_{folder_name_dictionary[curriculum_vitae_data_model]}.md"
    )

    def create_a_markdown_file(output_directory_path, _):
        renderer.create_a_markdown_file(data_model, output_directory_path)

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        create_a_markdown_file,
        reference_file_name,
        output_file_name,
    )


def test_if_create_a_markdown_file_can_create_a_new_directory(
    tmp_path, rendercv_data_model
):
    new_directory = tmp_path / "new_directory"

    typst_file_path = renderer.create_a_markdown_file(
        rendercv_data_model, new_directory
    )

    assert typst_file_path.exists()


@pytest.mark.parametrize(
    "theme_name",
    data.available_themes,
)
def test_copy_theme_files_to_output_directory(
    run_a_function_and_check_if_output_is_the_same_as_reference, theme_name
):
    reference_directory_name = theme_name

    def copy_theme_files_to_output_directory(output_directory_path, _):
        renderer_module.copy_theme_files_to_output_directory(
            theme_name, output_directory_path
        )

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

        # create dummytheme:
        if not dummytheme_path.exists():
            dummytheme_path.mkdir(parents=True, exist_ok=True)

        # create a txt file called test.txt in the custom theme directory:
        for entry_type_name in data.available_entry_type_names:
            pathlib.Path(dummytheme_path / f"{entry_type_name}.j2.typ").touch()

        pathlib.Path(dummytheme_path / "Header.j2.typ").touch()
        pathlib.Path(dummytheme_path / "Preamble.j2.typ").touch()
        pathlib.Path(dummytheme_path / "SectionBeginning.j2.typ").touch()
        pathlib.Path(dummytheme_path / "SectionEnding.j2.typ").touch()
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
            ' Literal["dummytheme"]\n'
        )

        # create reference_directory_path:
        os.chdir(dummytheme_path.parent)
        renderer_module.copy_theme_files_to_output_directory(
            theme_name=theme_name,
            output_directory_path=reference_directory_path,
        )

    def copy_theme_files_to_output_directory(
        output_directory_path, reference_directory_path
    ):
        dummytheme_path = reference_directory_path.parent / theme_name

        # copy the auxiliary theme files to tmp_path:
        os.chdir(dummytheme_path.parent)
        renderer_module.copy_theme_files_to_output_directory(
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
        renderer_module.copy_theme_files_to_output_directory(
            "nonexistent_theme", pathlib.Path()
        )


@pytest.mark.parametrize(
    "theme_name",
    data.available_themes,
)
@pytest.mark.parametrize(
    "short_second_row",
    [True, False],
)
@pytest.mark.parametrize(
    "curriculum_vitae_data_model",
    [
        "rendercv_empty_curriculum_vitae_data_model",
        "rendercv_filled_curriculum_vitae_data_model",
    ],
)
def test_create_a_typst_file_and_copy_theme_files(
    run_a_function_and_check_if_output_is_the_same_as_reference,
    request: pytest.FixtureRequest,
    theme_name,
    curriculum_vitae_data_model,
    short_second_row,
):
    short_s_r = "short_second_row" if short_second_row else "long_second_row"
    reference_directory_name = f"{theme_name}_{folder_name_dictionary[curriculum_vitae_data_model]}_{short_s_r}"
    data_model = data.RenderCVDataModel(
        cv=request.getfixturevalue(curriculum_vitae_data_model),
        design={"theme": theme_name, "entries": {"short_second_row": short_second_row}},
        rendercv_settings=data.RenderCVSettings(date="2024-01-01"),  # type: ignore
    )

    def create_a_typst_file_and_copy_theme_files(output_directory_path, _):
        renderer.create_a_typst_file_and_copy_theme_files(
            data_model, output_directory_path
        )

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        create_a_typst_file_and_copy_theme_files,
        reference_directory_name,
    )


@pytest.mark.parametrize(
    "theme_name",
    data.available_themes,
)
@pytest.mark.parametrize(
    "short_second_row",
    [True, False],
)
@pytest.mark.parametrize(
    "curriculum_vitae_data_model",
    [
        "rendercv_empty_curriculum_vitae_data_model",
        "rendercv_filled_curriculum_vitae_data_model",
    ],
)
def test_render_a_pdf_from_typst(
    request: pytest.FixtureRequest,
    run_a_function_and_check_if_output_is_the_same_as_reference,
    theme_name,
    curriculum_vitae_data_model,
    short_second_row,
):
    data.RenderCVSettings(date="2024-01-01")  # type: ignore
    name = request.getfixturevalue(curriculum_vitae_data_model).name
    name = str(name).replace(" ", "_")

    output_file_name = f"{name}_CV.pdf"
    short_s_r = "short_second_row" if short_second_row else "long_second_row"
    reference_name = f"{theme_name}_{folder_name_dictionary[curriculum_vitae_data_model]}_{short_s_r}"
    reference_file_name = f"{reference_name}.pdf"

    file_name = f"{name}_CV.typ"

    if theme_name in data.available_themes:
        file_name = file_name.replace(".typ", ".typ")

    def generate_pdf_file(output_directory_path, reference_file_or_directory_path):
        typst_sources_path = (
            reference_file_or_directory_path.parent.parent
            / "test_create_a_typst_file_and_copy_theme_files"
            / reference_name
        )

        shutil.copytree(typst_sources_path, output_directory_path, dirs_exist_ok=True)

        renderer.render_a_pdf_from_typst(output_directory_path / file_name)

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        function=generate_pdf_file,
        reference_file_or_directory_name=reference_file_name,
        output_file_name=output_file_name,
    )


def test_render_pdf_from_typst_nonexistent_typst_file():
    file_path = pathlib.Path("file_doesnt_exist.typ")
    with pytest.raises(FileNotFoundError):
        renderer.render_a_pdf_from_typst(file_path)


@pytest.mark.parametrize(
    "theme_name",
    data.available_themes,
)
@pytest.mark.parametrize(
    "curriculum_vitae_data_model",
    [
        "rendercv_empty_curriculum_vitae_data_model",
        "rendercv_filled_curriculum_vitae_data_model",
    ],
)
def test_render_an_html_from_markdown(
    run_a_function_and_check_if_output_is_the_same_as_reference,
    theme_name,
    curriculum_vitae_data_model,
):
    data.RenderCVSettings(date="2024-01-01")  # type: ignore
    reference_name = (
        f"{theme_name}_{folder_name_dictionary[curriculum_vitae_data_model]}"
    )
    output_file_name = f"{reference_name}.html"
    reference_file_name = f"{reference_name}.html"

    def render_html_from_markdown(
        output_directory_path, reference_file_or_directory_path
    ):
        markdown_file_name = f"{reference_name}.md"

        markdown_source_path = (
            reference_file_or_directory_path.parent.parent
            / "test_create_a_markdown_file"
            / markdown_file_name
        )

        # copy the markdown source to the output path
        shutil.copy(markdown_source_path, output_directory_path)

        # convert markdown to html
        renderer.render_an_html_from_markdown(
            output_directory_path / markdown_file_name
        )

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        function=render_html_from_markdown,
        reference_file_or_directory_name=reference_file_name,
        output_file_name=output_file_name,
    )


def test_render_html_from_markdown_nonexistent_markdown_file():
    file_path = pathlib.Path("file_doesnt_exist.md")
    with pytest.raises(FileNotFoundError):
        renderer.render_an_html_from_markdown(file_path)


def test_render_pngs_from_typst(
    run_a_function_and_check_if_output_is_the_same_as_reference,
):
    reference_directory_name = "pngs"

    def generate_pngs(output_directory_path, reference_file_or_directory_path):
        typst_folder_path = (
            reference_file_or_directory_path.parent.parent
            / "test_create_a_typst_file_and_copy_theme_files"
            / "classic_filled_long_second_row"
        )

        # copy typst folder to the output path
        shutil.copytree(typst_folder_path, output_directory_path, dirs_exist_ok=True)

        # convert pdf to pngs
        renderer.render_pngs_from_typst(
            output_directory_path / "John_Doe_CV.typ", ppi=20
        )

        # remove everything except the pngs
        for file in output_directory_path.glob("*"):
            if file.suffix == ".jpg" or file.suffix == ".typ":
                file.unlink()

    assert run_a_function_and_check_if_output_is_the_same_as_reference(
        generate_pngs, reference_directory_name
    )


def test_render_pdf_invalid_typst_file(tmp_path):
    typst_file_path = tmp_path / "invalid_typst_file.typ"
    typst_file_path.write_text("# Invalid Typst code")

    with pytest.raises(RuntimeError):
        renderer.render_a_pdf_from_typst(typst_file_path)


@pytest.mark.parametrize(
    "theme_name",
    data.available_themes,
)
def test_locale(
    theme_name,
    tmp_path,
):
    data.RenderCVSettings(date="2024-01-01")  # type: ignore
    cv = data.CurriculumVitae(
        name="Test",
        sections={
            "Normal Entries": [
                data.NormalEntry(
                    name="Test",
                    start_date="2024-01-01",
                    end_date="present",
                ),
            ]
        },
    )

    # "The style of the date. The following placeholders can be"
    # " used:\n-FULL_MONTH_NAME: Full name of the month\n- MONTH_ABBREVIATION:"
    # " Abbreviation of the month\n- MONTH: Month as a number\n-"
    # " MONTH_IN_TWO_DIGITS: Month as a number in two digits\n- YEAR: Year as a"
    # " number\n- YEAR_IN_TWO_DIGITS: Year as a number in two digits\nThe"
    # ' default value is "MONTH_ABBREVIATION YEAR".'
    locale = data.Locale(
        abbreviations_for_months=[
            "Abbreviation of Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
        full_names_of_months=[
            "Full name of January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
        present="this is present",
        to="this is to",
        date_template=(
            "FULL_MONTH_NAME MONTH_ABBREVIATION MONTH MONTH_IN_TWO_DIGITS YEAR"
            " YEAR_IN_TWO_DIGITS"
        ),
    )

    data_model = data.RenderCVDataModel(
        cv=cv,
        design={"theme": theme_name},
        locale=locale,
    )

    file = renderer.create_a_typst_file(data_model, tmp_path)

    contents = file.read_text()

    assert "Full name of January" in contents
    assert "Abbreviation of Jan" in contents
    assert "this is present" in contents
    assert "this is to" in contents


@pytest.mark.parametrize(
    "theme_name",
    data.available_themes,
)
def test_are_all_the_theme_files_the_same(theme_name):
    source_of_truth_theme = "classic"

    # find the directory of rendercv.themes.classic:
    source_of_truth_theme_folder = (
        pathlib.Path(__file__).parent.parent
        / "rendercv"
        / "themes"
        / source_of_truth_theme
    )
    source_of_truth_file_contents = [
        file.read_text() for file in source_of_truth_theme_folder.rglob("*.j2.typ")
    ]

    # find the directory of rendercv.themes.{theme_name}:
    theme_folder = (
        pathlib.Path(__file__).parent.parent / "rendercv" / "themes" / theme_name
    )
    theme_file_contents = [file.read_text() for file in theme_folder.rglob("*.j2.typ")]

    assert source_of_truth_file_contents == theme_file_contents


@pytest.mark.parametrize(
    ("input_template", "placeholders", "expected_output"),
    [
        # ("Hello, {name}!", {"{name}": None}, "Hello, "), # currently does not work
        # ("Hello, {name}!", {"{name}": "World"}, "Hello, World!"), # currently does not work
        # ("No placeholders here.", {}, "No placeholders here."),  # currently does not work
        ("*[My](https://myurl.com)*", {}, '#link("https://myurl.com")[#emph[My]]'),
        ("**[My](https://myurl.com)**", {}, '#link("https://myurl.com")[#strong[My]]'),
        (
            "***[My](https://myurl.com)***",
            {},
            '#link("https://myurl.com")[#strong[#emph[My]]]',
        ),
        (
            "**GRADE**",
            {"GRADE": "GPA: 3.00/4.00"},
            '#strong[GPA: 3.00/4.00]'
        ),
    ],
)
def test_input_template_to_typst(
    input_template,
    placeholders,
    expected_output,
):
    output = templater.input_template_to_typst(
        input_template,
        placeholders,
    )

    assert output == expected_output


def test_render_a_typst_file_with_none_name(tmp_path):
    cv = data.CurriculumVitae(
        name=None,
        sections={
            "Normal Entries": [
                data.NormalEntry(
                    name="Test",
                    start_date="2024-01-01",
                    end_date="present",
                ),
            ]
        },
    )

    data_model = data.RenderCVDataModel(
        cv=cv,
        design={"theme": "classic"},
    )

    file = renderer.create_a_typst_file(data_model, tmp_path)

    contents = file.read_text()

    assert "Test" in contents
