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
