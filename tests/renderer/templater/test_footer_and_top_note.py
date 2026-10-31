import pytest

from rendercv.renderer.templater.footer_and_top_note import (
    fill_document_template,
    render_footer_template,
    render_top_note_template,
)
from rendercv.renderer.templater.markup import emit, plain_text

placeholders = {
    "NAME": "John Doe",
    "CURRENT_DATE": "Jan 2024",
    "DAY": "1",
    "DAY_IN_TWO_DIGITS": "01",
    "MONTH": "1",
    "MONTH_IN_TWO_DIGITS": "01",
    "YEAR": "2024",
}


@pytest.mark.parametrize(
    ("template", "values", "expected"),
    [
        ("NAME - CV", placeholders, "John Doe - CV"),
        # Text that only accompanies a missing placeholder goes with it:
        ("NAME - CV", {**placeholders, "NAME": ""}, ""),
        ("**NAME**'s CV (YEAR)", placeholders, "John Doe's CV (2024)"),
        # Document templates have no arbitrary keys, so `_` separates names:
        ("NAME_CV_YEAR", placeholders, "John Doe_CV_2024"),
        ("CV_NAME", placeholders, "CV_John Doe"),
    ],
)
def test_fill_document_template(template, values, expected):
    assert plain_text(fill_document_template(template, values)) == expected


@pytest.mark.parametrize(
    ("template", "values", "expected"),
    [
        (
            "*LAST_UPDATED CURRENT_DATE*",
            placeholders,
            "#emph[Last updated in Jan 2024]",
        ),
        (
            "LAST_UPDATED CURRENT_DATE by NAME",
            {**placeholders, "NAME": ""},
            "Last updated in Jan 2024",
        ),
        ("NAME - DAY/MONTH/YEAR", placeholders, "John Doe - 1/1/2024"),
    ],
)
def test_render_top_note_template(template, values, expected):
    result = render_top_note_template(
        template, placeholders=values, last_updated="Last updated in"
    )

    assert emit(result, "typst") == expected


@pytest.mark.parametrize(
    ("template", "values", "expected"),
    [
        (
            "NAME - Page PAGE_NUMBER/TOTAL_PAGES - CURRENT_DATE",
            placeholders,
            (
                "John Doe - Page #str(here().page())/"
                "#str(counter(page).final().first()) - Jan 2024"
            ),
        ),
        (
            "*NAME -- PAGE_NUMBER/TOTAL_PAGES*",
            {**placeholders, "NAME": ""},
            "#emph[#str(here().page())/#str(counter(page).final().first())]",
        ),
        (
            "NAME - DAY_IN_TWO_DIGITS/MONTH_IN_TWO_DIGITS/YEAR",
            placeholders,
            "John Doe - 01/01/2024",
        ),
    ],
)
def test_render_footer_template(template, values, expected):
    result = render_footer_template(template, placeholders=values)

    assert emit(result, "typst") == expected
