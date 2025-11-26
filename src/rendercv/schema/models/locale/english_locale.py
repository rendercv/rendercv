import functools
from typing import Annotated, Literal

import annotated_types as at
import pydantic

from ..base import BaseModelWithoutExtraKeys


class EnglishLocale(BaseModelWithoutExtraKeys):
    language: Literal["english"] = pydantic.Field(
        default="english",
        description="The language of the locale. The default value is 'english'.",
    )
    last_updated: str = pydantic.Field(
        default="Last updated in",
        description='Translation of "Last updated in" in the locale. The default value is "Last updated in".',
    )
    month: str = pydantic.Field(
        default="month",
        description='Translation of the word "month" in the locale.',
    )
    months: str = pydantic.Field(
        default="months",
        description='Translation of the word "months" in the locale.',
    )
    year: str = pydantic.Field(
        default="year",
        description='Translation of the word "year" in the locale.',
    )
    years: str = pydantic.Field(
        default="years",
        description='Translation of the word "years" in the locale.',
    )
    present: str = pydantic.Field(
        default="present",
        description='Translation of the word "present" in the locale.',
    )
    # From https://web.library.yale.edu/cataloging/months
    abbreviations_for_months: Annotated[
        list[str], at.Len(min_length=12, max_length=12)
    ] = pydantic.Field(
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
    full_names_of_months: Annotated[list[str], at.Len(min_length=12, max_length=12)] = (
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
            description="Full names of the months in the locale.",
        )
    )

    @functools.cached_property
    def language_iso_639_1(self) -> str:
        return {
            "english": "en",
            "mandarin_chineese": "zh",
            "hindi": "hi",
            "spanish": "es",
            "french": "fr",
            "portuguese": "pt",
            "german": "de",
            "turkish": "tr",
            "italian": "it",
            "russian": "ru",
            "japanese": "ja",
            "korean": "ko",
        }[self.language]
