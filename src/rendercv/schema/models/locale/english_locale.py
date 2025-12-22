import functools
from typing import Annotated, Literal

import annotated_types as at
import pydantic

from ..base import BaseModelWithoutExtraKeys


class EnglishLocale(BaseModelWithoutExtraKeys):
    language: Literal["english"] = pydantic.Field(
        default="english",
        description="The language for your CV. The default value is `english`.",
    )
    last_updated: str = pydantic.Field(
        default="Last updated in",
        description=(
            'Translation of "Last updated in". The default value is `Last updated in`.'
        ),
    )
    month: str = pydantic.Field(
        default="month",
        description='Translation of "month" (singular). The default value is `month`.',
    )
    months: str = pydantic.Field(
        default="months",
        description='Translation of "months" (plural). The default value is `months`.',
    )
    year: str = pydantic.Field(
        default="year",
        description='Translation of "year" (singular). The default value is `year`.',
    )
    years: str = pydantic.Field(
        default="years",
        description='Translation of "years" (plural). The default value is `years`.',
    )
    present: str = pydantic.Field(
        default="present",
        description=(
            'Translation of "present" for ongoing dates. The default value is'
            " `present`."
        ),
    )
    # From https://web.library.yale.edu/cataloging/months
    month_abbreviations: Annotated[list[str], at.Len(min_length=12, max_length=12)] = (
        pydantic.Field(
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
            description="Month abbreviations (Jan-Dec).",
        )
    )
    month_names: Annotated[list[str], at.Len(min_length=12, max_length=12)] = (
        pydantic.Field(
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
            description="Full month names (January-December).",
        )
    )

    @functools.cached_property
    def language_iso_639_1(self) -> str:
        """Get ISO 639-1 two-letter language code for locale.

        Why:
            Typst's text element requires ISO 639-1/2/3 language codes for the
            lang parameter. This enables proper hyphenation, smart quotes, and
            accessibility (screen readers use it for voice selection). HTML export
            also uses it for lang attribute.

        Returns:
            Two-letter ISO 639-1 language code for Typst and HTML.
        """
        return {
            "danish": "dk",
            "english": "en",
            "french": "fr",
            "german": "de",
            "hindi": "hi",
            "italian": "it",
            "indonesian": "id",
            "japanese": "ja",
            "korean": "ko",
            "indonesia": "id",
            "mandarin_chineese": "zh",
            "portuguese": "pt",
            "russian": "ru",
            "spanish": "es",
            "turkish": "tr",
        }[self.language]
