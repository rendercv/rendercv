# Add a New Locale

1. Create a YAML file in `src/rendercv/schema/models/locale/other_locales/`

    ```bash
    touch src/rendercv/schema/models/locale/other_locales/mylanguage.yaml
    ```

2. Add the schema reference and provide translations

    ```yaml
    # yaml-language-server: $schema=../../../../../../schema.json
    locale:
      language: mylanguage
      last_updated: "Your translation"
      month: "Your translation"
      months: "Your translation"
      year: "Your translation"
      years: "Your translation"
      present: "Your translation"
      month_abbreviations:
        - Jan
        - Feb
        - Mar
        - Apr
        - May
        - Jun
        - Jul
        - Aug
        - Sep
        - Oct
        - Nov
        - Dec
      month_names:
        - January
        - February
        - March
        - April
        - May
        - June
        - July
        - August
        - September
        - October
        - November
        - December
    ```

3. Add ISO 639-1 language code to `english_locale.py`

    Edit `src/rendercv/schema/models/locale/english_locale.py` line 97-114:

    ```python
    return {
        "english": "en",
        # ... existing languages
        "mylanguage": "xx",  # Add your two-letter ISO 639-1 code
    }[self.language]
    ```

4. Done. Use it:

    ```bash
    rendercv new "John Doe" --locale mylanguage
    ```
