from datetime import date as Date

import pydantic
import pytest

from rendercv import data
from rendercv.data.models import (
    computers,
    curriculum_vitae,
    entry_types,
    locale,
)


@pytest.mark.parametrize(
    ("date", "expected_date_string"),
    [
        (Date(2020, 1, 1), "Jan 2020"),
        (Date(2020, 2, 1), "Feb 2020"),
        (Date(2020, 3, 1), "Mar 2020"),
        (Date(2020, 4, 1), "Apr 2020"),
        (Date(2020, 5, 1), "May 2020"),
        (Date(2020, 6, 1), "June 2020"),
        (Date(2020, 7, 1), "July 2020"),
        (Date(2020, 8, 1), "Aug 2020"),
        (Date(2020, 9, 1), "Sept 2020"),
        (Date(2020, 10, 1), "Oct 2020"),
        (Date(2020, 11, 1), "Nov 2020"),
        (Date(2020, 12, 1), "Dec 2020"),
    ],
)
def test_format_date(date, expected_date_string):
    assert data.format_date(date) == expected_date_string


@pytest.mark.parametrize(
    (
        "start_date",
        "end_date",
        "date",
        "expected_date_string",
        "expected_date_string_only_years",
        "expected_time_span",
    ),
    [
        (
            "2020-01-01",
            "2021-01-01",
            None,
            "Jan 2020 – Jan 2021",
            "2020 – 2021",
            "1 year 1 month",
        ),
        (
            "2020-01-01",
            "2022-01-01",
            None,
            "Jan 2020 – Jan 2022",
            "2020 – 2022",
            "2 years 1 month",
        ),
        (
            "2020-01-01",
            "2021-12-10",
            None,
            "Jan 2020 – Dec 2021",
            "2020 – 2021",
            "2 years",
        ),
        (
            Date(2020, 1, 1),
            Date(2021, 1, 1),
            None,
            "Jan 2020 – Jan 2021",
            "2020 – 2021",
            "1 year 1 month",
        ),
        (
            "2020-01",
            "2021-01",
            None,
            "Jan 2020 – Jan 2021",
            "2020 – 2021",
            "1 year 1 month",
        ),
        (
            "2020-01",
            "2021-02-01",
            None,
            "Jan 2020 – Feb 2021",
            "2020 – 2021",
            "1 year 2 months",
        ),
        (
            "2020-01-01",
            "2021-01",
            None,
            "Jan 2020 – Jan 2021",
            "2020 – 2021",
            "1 year 1 month",
        ),
        (
            "2020-01-01",
            None,
            None,
            "Jan 2020 – present",
            "2020 – present",
            "4 years 1 month",
        ),
        (
            "2020-02-01",
            "present",
            None,
            "Feb 2020 – present",
            "2020 – present",
            "4 years",
        ),
        ("2020-01-01", "2021-01-01", "2023-02-01", "Feb 2023", "2023", ""),
        ("2020", "2021", None, "2020 – 2021", "2020 – 2021", "1 year"),
        (
            "2020",
            None,
            None,
            "2020 – present",
            "2020 – present",
            "4 years",
        ),
        (
            "2020-10-10",
            "2022",
            None,
            "Oct 2020 – 2022",
            "2020 – 2022",
            "2 years",
        ),
        (
            "2020-10-10",
            "2020-11-05",
            None,
            "Oct 2020 – Nov 2020",
            "2020 – 2020",
            "1 month",
        ),
        (
            "2022",
            "2023-10-10",
            None,
            "2022 – Oct 2023",
            "2022 – 2023",
            "1 year",
        ),
        (
            "2020-01-01",
            "present",
            "My Custom Date",
            "My Custom Date",
            "My Custom Date",
            "",
        ),
        (
            "2020-01-01",
            None,
            "My Custom Date",
            "My Custom Date",
            "My Custom Date",
            "",
        ),
        (
            None,
            None,
            "My Custom Date",
            "My Custom Date",
            "My Custom Date",
            "",
        ),
        (
            None,
            "2020-01-01",
            "My Custom Date",
            "My Custom Date",
            "My Custom Date",
            "",
        ),
        (None, None, "2020-01-01", "Jan 2020", "2020", ""),
        (None, None, "2020-09", "Sept 2020", "2020", ""),
        (None, None, Date(2020, 1, 1), "Jan 2020", "2020", ""),
        (None, None, None, "", "", ""),
        (None, "2020-01-01", None, "Jan 2020", "2020", ""),
        (None, "present", None, "Jan 2024", "2024", ""),
        ("2002", "2020", "2024", "2024", "2024", ""),
    ],
)
def test_dates(
    start_date,
    end_date,
    date,
    expected_date_string,
    expected_date_string_only_years,
    expected_time_span,
):
    data.RenderCVSettings(date="2024-01-01")  # type: ignore
    entry_base = entry_types.EntryBase(
        start_date=start_date, end_date=end_date, date=date
    )

    assert entry_base.date_string == expected_date_string
    assert entry_base.date_string_only_years == expected_date_string_only_years
    assert entry_base.time_span_string == expected_time_span


def test_dates_style():
    assert data.format_date(Date(2020, 1, 1), "TEST") == "TEST"


@pytest.mark.parametrize(
    ("date", "expected_date_string"),
    [
        ("2020-01-01", "Jan 2020"),
        ("2020-01", "Jan 2020"),
        ("2020", "2020"),
    ],
)
def test_publication_dates(publication_entry, date, expected_date_string):
    publication_entry["date"] = date
    publication_entry = data.PublicationEntry(**publication_entry)
    assert publication_entry.date_string == expected_date_string


@pytest.mark.parametrize("date", ["2025-23-23"])
def test_invalid_publication_dates(publication_entry, date):
    publication_entry["date"] = date
    with pytest.raises(pydantic.ValidationError):
        data.PublicationEntry(**publication_entry)


def test_education_entry_grade_field(education_entry):
    education_entry["grade"] = "GPA: 3.00/4.00"
    entry = data.EducationEntry(**education_entry)
    assert entry.grade == "GPA: 3.00/4.00"


def test_locale():
    data_model = data.create_a_sample_data_model("John Doe")
    data_model.locale = data.Locale(
        month="a",
        months="b",
        year="c",
        years="d",
        present="e",
        to="f",
        abbreviations_for_months=[
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
        ],
        full_names_of_months=[
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
        ],
        phone_number_format="international",
    )

    locale_as_dict = data_model.locale.model_dump()
    del locale_as_dict["page_numbering_template"]
    del locale_as_dict["last_updated_date_template"]
    del locale_as_dict["language"]

    assert locale_as_dict == locale.locale


def test_if_local_catalog_resets():
    data_model = data.create_a_sample_data_model("John Doe")

    data_model.locale = data.Locale(
        month="a",
    )

    assert locale.locale["month"] == "a"

    data_model = data.create_a_sample_data_model("John Doe")

    assert locale.locale["month"] == "month"


def test_curriculum_vitae():
    data.CurriculumVitae(name="Test Doe")

    assert curriculum_vitae.curriculum_vitae == {"name": "Test Doe"}


def test_if_curriculum_vitae_resets():
    data.CurriculumVitae(name="Test Doe")

    assert curriculum_vitae.curriculum_vitae["name"] == "Test Doe"

    data.create_a_sample_data_model("John Doe")

    assert curriculum_vitae.curriculum_vitae["name"] == "John Doe"


@pytest.mark.parametrize(
    ("url", "expected_clean_url"),
    [
        ("https://example.com", "example.com"),
        ("https://example.com/", "example.com"),
        ("https://example.com/test", "example.com/test"),
        ("https://example.com/test/", "example.com/test"),
        ("https://www.example.com/test/", "www.example.com/test"),
    ],
)
def test_make_a_url_clean(url, expected_clean_url):
    assert computers.make_a_url_clean(url) == expected_clean_url
    assert (
        data.PublicationEntry(title="Test", authors=["test"], url=url).clean_url
        == expected_clean_url
    )


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


def test_make_keywords_bold_in_a_string():
    assert (
        data.make_keywords_bold_in_a_string(
            "This is a test string with some keywords.",
            ["test", "keywords"],
        )
        == "This is a **test** string with some **keywords**."
    )


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
