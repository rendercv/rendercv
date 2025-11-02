import importlib
from pathlib import Path
from typing import Annotated, Any, Literal
from functools import reduce
from operator import or_
import annotated_types as at
import pydantic

from ..base import BaseModelWithoutExtraKeys


class EnglishLocale(BaseModelWithoutExtraKeys):
    """Base class for all locale variants.

    All fields are required to ensure that each locale implementation provides
    complete translations and formatting.
    """

    language: Literal["english"] = pydantic.Field(
        default="english",
        description="The language of the locale. The default value is 'english'.",
    )
    phone_number_format: Literal["national", "international", "E164"] | None = (
        pydantic.Field(
            default="national",
            description=(
                "If 'national', phone numbers are formatted without the country code."
                " If 'international', phone numbers are formatted with the country"
                " code. The default value is 'national'."
            ),
        )
    )
    page_numbering_template: str = pydantic.Field(
        default="NAME - Page PAGE_NUMBER of TOTAL_PAGES",
        description=(
            "The template of the page numbering at the bottom of the page."
            "\n\nThe following placeholders can be used:"
            "\n- NAME: The name of the person"
            "\n- PAGE_NUMBER: The current page number"
            "\n- TOTAL_PAGES: The total number of pages"
            "\n- TODAY: Today's date with `locale.date_template`"
        ),
    )
    last_updated_date_template: str = pydantic.Field(
        default="Last updated in TODAY",
        description=(
            "The template of the last updated date at the top right corner of the"
            " page.\n\nThe following placeholders can be used:"
            "\n- NAME: The name of the person"
            "\n- PAGE_NUMBER: The current page number"
            "\n- TOTAL_PAGES: The total number of pages"
            "\n- TODAY: Today's date with `locale.date_template`"
        ),
    )
    date_template: str | None = pydantic.Field(
        default="MONTH_ABBREVIATION YEAR",
        description=(
            "The template of the date.\n\nThe following placeholders can be used:"
            "\n- FULL_MONTH_NAME: Full name of the month (e.g., January)"
            "\n- MONTH_ABBREVIATION: Abbreviation of the month (e.g., Jan)"
            "\n- MONTH: Month as a number (e.g., 1)"
            "\n- MONTH_IN_TWO_DIGITS: Month as a number in two digits (e.g., 01)"
            "\n- YEAR: Year as a number (e.g., 2024)"
            "\n- YEAR_IN_TWO_DIGITS: Year as a number in two digits (e.g., 24)"
        ),
    )
    month: str | None = pydantic.Field(
        default="month",
        description='Translation of the word "month" in the locale.',
    )
    months: str | None = pydantic.Field(
        default="months",
        description='Translation of the word "months" in the locale.',
    )
    year: str | None = pydantic.Field(
        default="year",
        description='Translation of the word "year" in the locale.',
    )
    years: str | None = pydantic.Field(
        default="years",
        description='Translation of the word "years" in the locale.',
    )
    present: str | None = pydantic.Field(
        default="present",
        description='Translation of the word "present" in the locale.',
    )
    to: str | None = pydantic.Field(
        default="–",
        description=(
            "The word or character used to indicate a range in the locale (e.g.,"
            ' "2020 - 2021").'
        ),
    )
    # From https://web.library.yale.edu/cataloging/months
    abbreviations_for_months: (
        Annotated[list[str], at.Len(min_length=12, max_length=12)] | None
    ) = pydantic.Field(
        default=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "June",
            "July",
            "Aug",
            "Sept",
            "Oct",
            "Nov",
            "Dec",
        ],
        description="Abbreviations of the months in the locale.",
    )
    full_names_of_months: (
        Annotated[list[str], at.Len(min_length=12, max_length=12)] | None
    ) = pydantic.Field(
        default=[
            "January",
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
        description="Full names of the months in the locale.",
    )


def create_other_locale_class(
    locale_name: str, defaults: dict[str, Any]
) -> type[EnglishLocale]:
    """Dynamically create a locale model class with the given defaults.

    Args:
        locale_name: Name of the locale (e.g., "english", "turkish")
        defaults: Dictionary of field names to default values

    Returns:
        A dynamically created Pydantic model class that inherits from BaseLocale
        with all field defaults applied from the defaults dictionary.

    Example:
        >>> locale_data = {"language": "english", "month": "month", ...}
        >>> english_locale = create_locale_class("english", locale_data)
        >>> locale = english_locale()
        >>> locale.language
        'english'
    """
    base_fields = EnglishLocale.model_fields
    field_specs: dict[str, Any] = {}

    for field_name, default_value in defaults.items():
        if field_name not in base_fields:
            raise ValueError(
                f"Field {field_name} in defaults for {locale_name} "
                "is not defined in BaseLocale"
            )

        base_field_info = base_fields[field_name]

        new_field = pydantic.Field(
            default=default_value,
            description=base_field_info.description,
            title=base_field_info.title,
        )

        field_annotation = base_field_info.annotation

        # For discriminated unions, each subclass needs a Literal type
        if field_name == "language":
            field_annotation = Literal[default_value]  # type: ignore

        field_specs[field_name] = (field_annotation, new_field)

    model_class_name = f"{locale_name.replace('_', ' ').title().replace(' ', '')}Locale"

    return pydantic.create_model(
        model_class_name,
        __base__=EnglishLocale,
        __module__="rendercv.schema.models.locale",
        **field_specs,
    )


def discover_other_locales() -> dict[str, type[EnglishLocale]]:
    """Auto-discover and load all locale files from locales/ directory.

    Returns:
        Dictionary mapping class names (e.g., "EnglishLocale") to dynamically
        created Pydantic model classes.
    """
    locales_dir = Path(__file__).parent / "other_locales"
    discovered: dict[str, type[EnglishLocale]] = {}

    for py_file in sorted(locales_dir.glob("*.py")):
        if py_file.stem == "__init__":
            continue

        locale_name = py_file.stem
        module = importlib.import_module(
            f"rendercv.schema.models.locale.other_locales.{locale_name}"
        )
        locale_data = getattr(module, f"{locale_name}_locale")
        locale_class = create_other_locale_class(locale_name, locale_data)
        discovered[locale_class.__name__] = locale_class

    return discovered


# Build discriminated union dynamically
type Locale = Annotated[
    reduce(
        or_, discover_other_locales().values()
    ),  # pyright: ignore[reportInvalidTypeForm]
    pydantic.Field(discriminator="language"),
]
