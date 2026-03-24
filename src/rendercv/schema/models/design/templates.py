import pydantic

from rendercv.schema.models.base import BaseModelWithoutExtraKeys


class OneLineEntryTemplate(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**LABEL:** DETAILS",
        description=(
            "Template for one-line entries. Available placeholders:\n- `LABEL`: The"
            ' label text (e.g., "Languages", "Citizenship")\n- `DETAILS`: The details'
            ' text (e.g., "English (native), Spanish (fluent)")\n\nYou can also add'
            " arbitrary keys to entries and use them as UPPERCASE placeholders.\n\nThe"
            " default value is `**LABEL:** DETAILS`."
        ),
    )


class EducationEntryTemplate(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**INSTITUTION**, AREA\nSUMMARY\nHIGHLIGHTS",
        description=(
            "Template for education entry main column. Available placeholders:\n-"
            " `INSTITUTION`: Institution name\n- `AREA`: Field of study/major\n-"
            " `DEGREE`: Degree type (e.g., BS, PhD)\n- `DEGREE_WITH_AREA`: Locale-aware"
            " phrase combining degree and area (e.g., 'BS in Computer Science')\n-"
            " `SUMMARY`: Summary text\n-"
            " `HIGHLIGHTS`: Bullet points list\n- `LOCATION`: Location text\n- `DATE`:"
            " Formatted date or date range\n\nYou can also add arbitrary keys to"
            " entries and use them as UPPERCASE placeholders.\n\nThe default value is"
            " `**INSTITUTION**, AREA\\nSUMMARY\\nHIGHLIGHTS`."
        ),
    )
    degree_column: str | None = pydantic.Field(
        default="**DEGREE**",
        description=(
            "Optional degree column template. If provided, displays degree in separate"
            " column. If `null`, no degree column is shown. Available placeholders:\n-"
            " `INSTITUTION`: Institution name\n- `AREA`: Field of study/major\n-"
            " `DEGREE`: Degree type (e.g., BS, PhD)\n- `SUMMARY`: Summary text\n-"
            " `HIGHLIGHTS`: Bullet points list\n- `LOCATION`: Location text\n- `DATE`:"
            " Formatted date or date range\n\nYou can also add arbitrary keys to"
            " entries and use them as UPPERCASE placeholders.\n\nThe default value is"
            " `**DEGREE**`."
        ),
    )
    date_and_location_column: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=(
            "Template for education entry date/location column. Available"
            " placeholders:\n- `INSTITUTION`: Institution name\n- `AREA`: Field of"
            " study/major\n- `DEGREE`: Degree type (e.g., BS, PhD)\n- `SUMMARY`:"
            " Summary text\n- `HIGHLIGHTS`: Bullet points list\n- `LOCATION`: Location"
            " text\n- `DATE`: Formatted date or date range\n\nYou can also add"
            " arbitrary keys to entries and use them as UPPERCASE placeholders.\n\nThe"
            " default value is `LOCATION\\nDATE`."
        ),
    )


class NormalEntryTemplate(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**NAME**\nSUMMARY\nHIGHLIGHTS",
        description=(
            "Template for normal entry main column. Available placeholders:\n- `NAME`:"
            " Entry name/title\n- `SUMMARY`: Summary text\n- `HIGHLIGHTS`: Bullet"
            " points list\n- `LOCATION`: Location text\n- `DATE`: Formatted date or"
            " date range\n\nYou can also add arbitrary keys to entries and use them as"
            " UPPERCASE placeholders.\n\nThe default value is"
            " `**NAME**\\nSUMMARY\\nHIGHLIGHTS`."
        ),
    )
    date_and_location_column: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=(
            "Template for normal entry date/location column. Available placeholders:\n-"
            " `NAME`: Entry name/title\n- `SUMMARY`: Summary text\n- `HIGHLIGHTS`:"
            " Bullet points list\n- `LOCATION`: Location text\n- `DATE`: Formatted date"
            " or date range\n\nYou can also add arbitrary keys to entries and use them"
            " as UPPERCASE placeholders.\n\nThe default value is `LOCATION\\nDATE`."
        ),
    )


class ExperienceEntryTemplate(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**COMPANY**, POSITION\nSUMMARY\nHIGHLIGHTS",
        description=(
            "Template for experience entry main column. Available placeholders:\n-"
            " `COMPANY`: Company name\n- `POSITION`: Job title/position\n- `SUMMARY`:"
            " Summary text\n- `HIGHLIGHTS`: Bullet points list\n- `LOCATION`: Location"
            " text\n- `DATE`: Formatted date or date range\n\nYou can also add"
            " arbitrary keys to entries and use them as UPPERCASE placeholders.\n\nThe"
            " default value is `**COMPANY**, POSITION\\nSUMMARY\\nHIGHLIGHTS`."
        ),
    )
    date_and_location_column: str = pydantic.Field(
        default="LOCATION\nDATE",
        description=(
            "Template for experience entry date/location column. Available"
            " placeholders:\n- `COMPANY`: Company name\n- `POSITION`: Job"
            " title/position\n- `SUMMARY`: Summary text\n- `HIGHLIGHTS`: Bullet points"
            " list\n- `LOCATION`: Location text\n- `DATE`: Formatted date or date"
            " range\n\nYou can also add arbitrary keys to entries and use them as"
            " UPPERCASE placeholders.\n\nThe default value is `LOCATION\\nDATE`."
        ),
    )


class PublicationEntryTemplate(BaseModelWithoutExtraKeys):
    main_column: str = pydantic.Field(
        default="**TITLE**\nSUMMARY\nAUTHORS\nURL (JOURNAL)",
        description=(
            "Template for publication entry main column. Available placeholders:\n-"
            " `TITLE`: Publication title\n- `AUTHORS`: List of authors (formatted as"
            " comma-separated string)\n- `SUMMARY`: Summary/abstract text\n- `DOI`:"
            " Digital Object Identifier\n- `URL`: Publication URL (if DOI not"
            " provided)\n- `JOURNAL`: Journal/conference/venue name\n- `DATE`:"
            " Formatted date\n\nYou can also add arbitrary keys to entries and use them"
            " as UPPERCASE placeholders.\n\nThe default value is"
            " `**TITLE**\\nSUMMARY\\nAUTHORS\\nURL (JOURNAL)`."
        ),
    )
    date_and_location_column: str = pydantic.Field(
        default="DATE",
        description=(
            "Template for publication entry date column. Available placeholders:\n-"
            " `TITLE`: Publication title\n- `AUTHORS`: List of authors (formatted as"
            " comma-separated string)\n- `SUMMARY`: Summary/abstract text\n- `DOI`:"
            " Digital Object Identifier\n- `URL`: Publication URL (if DOI not"
            " provided)\n- `JOURNAL`: Journal/conference/venue name\n- `DATE`:"
            " Formatted date\n\nYou can also add arbitrary keys to entries and use them"
            " as UPPERCASE placeholders.\n\nThe default value is `DATE`."
        ),
    )


class Templates(BaseModelWithoutExtraKeys):
    footer: str = pydantic.Field(
        default="*NAME -- PAGE_NUMBER/TOTAL_PAGES*",
        description=(
            "Template for the footer. Available placeholders:\n"
            "- `NAME`: The CV owner's name from `cv.name`\n"
            "- `PAGE_NUMBER`: Current page number\n"
            "- `TOTAL_PAGES`: Total number of pages\n"
            "- `CURRENT_DATE`: Formatted date based on `design.templates.single_date`\n"
            "- `MONTH_NAME`: Full month name (e.g., January)\n"
            "- `MONTH_ABBREVIATION`: Abbreviated month name (e.g., Jan)\n"
            "- `MONTH`: Month number (e.g., 1)\n"
            "- `MONTH_IN_TWO_DIGITS`: Zero-padded month (e.g., 01)\n"
            "- `DAY`: Day of the month (e.g., 5)\n"
            "- `DAY_IN_TWO_DIGITS`: Zero-padded day (e.g., 05)\n"
            "- `YEAR`: Full year (e.g., 2025)\n"
            "- `YEAR_IN_TWO_DIGITS`: Two-digit year (e.g., 25)\n\n"
            "The default value is `*NAME -- PAGE_NUMBER/TOTAL_PAGES*`."
        ),
    )
    top_note: str = pydantic.Field(
        default="*LAST_UPDATED CURRENT_DATE*",
        description=(
            "Template for the top note. Available placeholders:\n- `LAST_UPDATED`:"
            ' Localized "last updated" text from `locale.last_updated`\n-'
            " `CURRENT_DATE`: Formatted date based on `design.templates.single_date`\n-"
            " `NAME`: The CV owner's name from `cv.name`\n- `MONTH_NAME`: Full month"
            " name (e.g., January)\n- `MONTH_ABBREVIATION`: Abbreviated month name"
            " (e.g., Jan)\n- `MONTH`: Month number (e.g., 1)\n- `MONTH_IN_TWO_DIGITS`:"
            " Zero-padded month (e.g., 01)\n- `DAY`: Day of the month (e.g., 5)\n-"
            " `DAY_IN_TWO_DIGITS`: Zero-padded day (e.g., 05)\n- `YEAR`: Full year"
            " (e.g., 2025)\n- `YEAR_IN_TWO_DIGITS`: Two-digit year (e.g., 25)\n\n"
            "The default value is `*LAST_UPDATED CURRENT_DATE*`."
        ),
    )
    single_date: str = pydantic.Field(
        default="MONTH_ABBREVIATION YEAR",
        description=(
            "Template for single dates. Available placeholders:\n"
            "- `MONTH_NAME`: Full month name (e.g., January)\n"
            "- `MONTH_ABBREVIATION`: Abbreviated month name (e.g., Jan)\n"
            "- `MONTH`: Month number (e.g., 1)\n"
            "- `MONTH_IN_TWO_DIGITS`: Zero-padded month (e.g., 01)\n"
            "- `DAY`: Day of the month (e.g., 5)\n"
            "- `DAY_IN_TWO_DIGITS`: Zero-padded day (e.g., 05)\n"
            "- `YEAR`: Full year (e.g., 2025)\n"
            "- `YEAR_IN_TWO_DIGITS`: Two-digit year (e.g., 25)\n\n"
            "The default value is `MONTH_ABBREVIATION YEAR`."
        ),
    )
    date_range: str = pydantic.Field(
        default="START_DATE – END_DATE",
        description=(
            "Template for date ranges. Available placeholders:\n- `START_DATE`:"
            " Formatted start date based on `design.templates.single_date`\n-"
            " `END_DATE`: Formatted end date based on `design.templates.single_date`"
            ' (or "present"/"ongoing" for current positions)\n\nThe default value is'
            " `START_DATE – END_DATE`."
        ),
    )
    time_span: str = pydantic.Field(
        default="HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS",
        description=(
            "Template for time spans (duration calculations). Available"
            " placeholders:\n- `HOW_MANY_YEARS`: Number of years (e.g., 2)\n- `YEARS`:"
            ' Localized word for "years" from `locale.years` (or singular "year")\n-'
            " `HOW_MANY_MONTHS`: Number of months (e.g., 3)\n- `MONTHS`: Localized word"
            ' for "months" from `locale.months` (or singular "month")\n\nThe default'
            " value is `HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS`."
        ),
    )
    one_line_entry: OneLineEntryTemplate = pydantic.Field(
        default_factory=OneLineEntryTemplate,
        description="Template for one-line entries.",
    )
    education_entry: EducationEntryTemplate = pydantic.Field(
        default_factory=EducationEntryTemplate,
        description="Template for education entries.",
    )
    normal_entry: NormalEntryTemplate = pydantic.Field(
        default_factory=NormalEntryTemplate,
        description="Template for normal entries.",
    )
    experience_entry: ExperienceEntryTemplate = pydantic.Field(
        default_factory=ExperienceEntryTemplate,
        description="Template for experience entries.",
    )
    publication_entry: PublicationEntryTemplate = pydantic.Field(
        default_factory=PublicationEntryTemplate,
        description="Template for publication entries.",
    )
