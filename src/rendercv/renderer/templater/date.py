from rendercv.schema.models.cv.section import Entry


def compute_date_string(entry: Entry) -> str | None:
    return ""


def format_date(date: Date, date_template: str | None = None) -> str:
    """Formats a `Date` object to a string in the following format: "Jan 2021". The
    month names are taken from the `locale` dictionary from the
    `rendercv.data_models.models` module.

    Example:
        ```python
        format_date(Date(2024, 5, 1))
        ```
        will return

        `"May 2024"`

    Args:
        date: The date to format.
        date_template: The template of the date string. If not provided, the default date
            style from the `locale` dictionary will be used.

    Returns:
        The formatted date.
    """
    full_month_names = locale["full_names_of_months"]
    short_month_names = locale["abbreviations_for_months"]

    month = int(date.strftime("%m"))
    year = date.strftime(format="%Y")

    placeholders = {
        "FULL_MONTH_NAME": full_month_names[month - 1],
        "MONTH_ABBREVIATION": short_month_names[month - 1],
        "MONTH_IN_TWO_DIGITS": f"{month:02d}",
        "YEAR_IN_TWO_DIGITS": str(year[-2:]),
        "MONTH": str(month),
        "YEAR": str(year),
    }
    if date_template is None:
        date_template = locale["date_template"]  # type: ignore

    assert isinstance(date_template, str)

    for placeholder, value in placeholders.items():
        date_template = date_template.replace(placeholder, value)  # type: ignore

    return date_template
