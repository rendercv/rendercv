import pytest

from rendercv import data


@pytest.mark.parametrize(
    ("path_name", "expected_value"),
    [
        ("NAME_IN_SNAKE_CASE", "John_Doe"),
        ("NAME_IN_LOWER_SNAKE_CASE", "john_doe"),
        ("NAME_IN_UPPER_SNAKE_CASE", "JOHN_DOE"),
        ("NAME_IN_KEBAB_CASE", "John-Doe"),
        ("NAME_IN_LOWER_KEBAB_CASE", "john-doe"),
        ("NAME_IN_UPPER_KEBAB_CASE", "JOHN-DOE"),
        ("NAME", "John Doe"),
        ("FULL_MONTH_NAME", "January"),
        ("MONTH_ABBREVIATION", "Jan"),
        ("MONTH", "1"),
        ("MONTH_IN_TWO_DIGITS", "01"),
        ("YEAR", "2024"),
        ("YEAR_IN_TWO_DIGITS", "24"),
    ],
)
def test_render_command_settings_placeholders(path_name, expected_value):
    data.RenderCVSettings(date="2024-01-01")  # type: ignore

    data.CurriculumVitae(name="John Doe")

    render_command_settings = data.RenderCommandSettings(
        pdf_path=path_name,
        typst_path=path_name,
        html_path=path_name,
        markdown_path=path_name,
        output_folder_name=path_name,
    )

    assert render_command_settings.pdf_path.name == expected_value  # type: ignore
    assert render_command_settings.typst_path.name == expected_value  # type: ignore
    assert render_command_settings.html_path.name == expected_value  # type: ignore
    assert render_command_settings.markdown_path.name == expected_value  # type: ignore
    assert render_command_settings.output_folder_name == expected_value


def test_bold_keywords():
    data_model_as_dict = {
        "cv": {
            "sections": {
                "test": ["test_keyword_1"],
                "test2": [
                    {
                        "institution": "Test Institution",
                        "area": "Test Area",
                        "degree": None,
                        "date": None,
                        "start_date": None,
                        "end_date": None,
                        "location": None,
                        "summary": "test_keyword_3 test_keyword_4",
                        "highlights": ["test_keyword_2"],
                    }
                ],
                "test3": [
                    {
                        "company": "Test Company",
                        "position": "Test Position",
                        "date": None,
                        "start_date": None,
                        "end_date": None,
                        "location": None,
                        "summary": "test_keyword_6 test_keyword_7",
                        "highlights": ["test_keyword_5", "test_keyword_6"],
                    }
                ],
                "test4": [
                    {
                        "name": "Test",
                        "date": None,
                        "start_date": None,
                        "end_date": None,
                        "location": None,
                        "summary": "test_keyword_3 test_keyword_4",
                        "highlights": ["test_keyword_2"],
                    }
                ],
                "test6": [{"bullet": "test_keyword_3 test_keyword_4"}],
                "test7": [
                    {
                        "label": "Test Institution",
                        "details": "test_keyword_3 test_keyword_4",
                    }
                ],
            },
        },
        "rendercv_settings": {
            "bold_keywords": [
                "test_keyword_1",
                "test_keyword_2",
                "test_keyword_3",
                "test_keyword_4",
                "test_keyword_5",
                "test_keyword_6",
                "test_keyword_7",
            ],
        },
    }

    data_model = data.validate_input_dictionary_and_return_the_data_model(
        data_model_as_dict
    )

    for section in data_model.cv.sections:
        for entry in section.entries:
            if section.title == "Test":
                assert "**test_keyword_1**" in entry
            elif section.title == "Test2":
                assert "**test_keyword_2**" in entry.highlights[0]
                assert "**test_keyword_3**" in entry.summary
                assert "**test_keyword_4**" in entry.summary
            elif section.title == "Test3":
                assert "**test_keyword_5**" in entry.highlights[0]
                assert "**test_keyword_6**" in entry.highlights[1]
                assert "**test_keyword_6**" in entry.summary
                assert "**test_keyword_7**" in entry.summary
            elif section.title == "Test4":
                assert "**test_keyword_2**" in entry.highlights[0]
                assert "**test_keyword_3**" in entry.summary
                assert "**test_keyword_4**" in entry.summary
            elif section.title == "Test6":
                assert "**test_keyword_3**" in entry.bullet
                assert "**test_keyword_4**" in entry.bullet
            elif section.title == "Test7":
                assert "**test_keyword_3**" in entry.details
                assert "**test_keyword_4**" in entry.details


def _create_sorting_data_model(order: str) -> data.RenderCVDataModel:
    entries = [
        {
            "company": "A",
            "position": "P",
            "start_date": "2020-01-01",
        },
        {
            "company": "B",
            "position": "P",
            "start_date": "2022-01-01",
        },
        {
            "company": "C",
            "position": "P",
            "date": "2021-05-01",
        },
        {
            "company": "D",
            "position": "P",
            "date": "2022-01-01",
        },
    ]

    cv = data.CurriculumVitae(
        name="John Doe",
        sections={"exp": entries},
    )

    settings = data.RenderCVSettings(date="2024-01-01", sort_entries=order)

    return data.RenderCVDataModel(cv=cv, rendercv_settings=settings)


@pytest.mark.parametrize(
    ("order", "expected"),
    [
        (
            "reverse-chronological",
            ["B", "A", "D", "C"],
        ),
        (
            "chronological",
            ["C", "D", "A", "B"],
        ),
        (
            "none",
            ["A", "B", "C", "D"],
        ),
    ],
)
def test_sort_entries(order, expected):
    data_model = _create_sorting_data_model(order)
    entries = data_model.cv.sections[0].entries
    companies = [e.company for e in entries]
    assert companies == expected


def _create_sorting_data_model_with_ranges(order: str) -> data.RenderCVDataModel:
    entries = [
        {
            "company": "A",
            "position": "P",
            "start_date": "2020-01-01",
            "end_date": "2021-06-01",
        },
        {
            "company": "B",
            "position": "P",
            "start_date": "2019-01-01",
            "end_date": "2022-06-01",
        },
        {
            "company": "C",
            "position": "P",
            "start_date": "2021-01-01",
            "end_date": "2022-06-01",
        },
        {
            "company": "D",
            "position": "P",
            "date": "2020-05-01",
        },
    ]

    cv = data.CurriculumVitae(
        name="John Doe",
        sections={"exp": entries},
    )

    settings = data.RenderCVSettings(date="2024-01-01", sort_entries=order)

    return data.RenderCVDataModel(cv=cv, rendercv_settings=settings)


@pytest.mark.parametrize(
    ("order", "expected"),
    [
        (
            "reverse-chronological",
            ["C", "B", "A", "D"],
        ),
        (
            "chronological",
            ["D", "A", "B", "C"],
        ),
    ],
)
def test_sort_entries_with_ranges(order, expected):
    data_model = _create_sorting_data_model_with_ranges(order)
    entries = data_model.cv.sections[0].entries
    companies = [e.company for e in entries]
    assert companies == expected


def _create_sorting_data_model_with_ties(order: str) -> data.RenderCVDataModel:
    entries = [
        {
            "company": "A",
            "position": "P",
            "date": "2020-01-01",
        },
        {
            "company": "B",
            "position": "P",
            "date": "2020-01-01",
        },
        {
            "company": "C",
            "position": "P",
            "date": "2020-01-02",
        },
    ]

    cv = data.CurriculumVitae(
        name="John Doe",
        sections={"exp": entries},
    )

    settings = data.RenderCVSettings(date="2024-01-01", sort_entries=order)

    return data.RenderCVDataModel(cv=cv, rendercv_settings=settings)


@pytest.mark.parametrize("order", ["reverse-chronological", "chronological"])
def test_sort_entries_tie_keeps_order(order):
    data_model = _create_sorting_data_model_with_ties(order)
    entries = data_model.cv.sections[0].entries
    companies = [e.company for e in entries]
    if order == "reverse-chronological":
        assert companies == ["C", "A", "B"]
    else:
        assert companies == ["A", "B", "C"]
