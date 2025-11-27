from datetime import date as Date

from rendercv.schema.models.locale.locale import Locale

from .date import date_object_to_string
from .string_processor import substitute_placeholders


def render_top_note_template(
    top_note_template: str,
    *,
    locale: Locale,
    current_date: Date,
    name: str | None,
    single_date_template: str,
) -> str:
    placeholders: dict[str, str] = {
        "CURRENT_DATE": date_object_to_string(
            current_date,
            locale=locale,
            single_date_template=single_date_template,
        ),
        "LAST_UPDATED": locale.last_updated,
        "NAME": name or "",
    }
    return substitute_placeholders(top_note_template, placeholders)


def render_footer_template(
    footer_template: str,
    *,
    locale: Locale,
    current_date: Date,
    name: str | None,
    single_date_template: str,
) -> str:
    placeholders: dict[str, str] = {
        "CURRENT_DATE": date_object_to_string(
            current_date,
            locale=locale,
            single_date_template=single_date_template,
        ),
        "NAME": name or "",
        "PAGE_NUMBER": '" + str(here().page()) + "',
        "TOTAL_PAGES": '" + str(counter(page).final().first()) + "',
    }
    return f'context {{ "{substitute_placeholders(footer_template, placeholders)}" }}'
