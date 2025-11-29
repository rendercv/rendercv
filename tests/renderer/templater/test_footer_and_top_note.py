from datetime import date as Date

import pytest

from rendercv.renderer.templater.footer_and_top_note import (
    render_footer_template,
    render_top_note_template,
)
from rendercv.schema.models.locale.english_locale import EnglishLocale


@pytest.mark.parametrize(
    ("name", "top_note_template", "expected"),
    [
        (
            "John Doe",
            "LAST_UPDATED CURRENT_DATE by NAME",
            "Last updated in Jan 2024 by John Doe",
        ),
        (
            None,
            "LAST_UPDATED CURRENT_DATE by NAME",
            "Last updated in Jan 2024 by",
        ),
    ],
)
def test_render_top_note_template(name, top_note_template, expected):
    result = render_top_note_template(
        top_note_template,
        locale=EnglishLocale(),
        current_date=Date(2024, 1, 1),
        name=name,
        single_date_template="MONTH_ABBREVIATION YEAR",
    )
    assert result == expected


@pytest.mark.parametrize(
    ("name", "footer_template", "expected"),
    [
        (
            "John Doe",
            "NAME - Page PAGE_NUMBER/TOTAL_PAGES - CURRENT_DATE",
            "John Doe - Page TYPST_PAGE_NUMBER/TYPST_TOTAL_PAGES - Jan 2024",
        ),
        (
            None,
            "NAME - Page PAGE_NUMBER/TOTAL_PAGES - CURRENT_DATE",
            "- Page TYPST_PAGE_NUMBER/TYPST_TOTAL_PAGES - Jan 2024",
        ),
    ],
)
def test_render_footer_template(name, footer_template, expected):
    result = render_footer_template(
        footer_template,
        locale=EnglishLocale(),
        current_date=Date(2024, 1, 1),
        name=name,
        single_date_template="MONTH_ABBREVIATION YEAR",
    )
    assert result.replace('context { [', "").replace('] }', "") == expected.replace(
        "TYPST_PAGE_NUMBER", "#str(here().page())"
    ).replace("TYPST_TOTAL_PAGES", "#str(counter(page).final().first())")
