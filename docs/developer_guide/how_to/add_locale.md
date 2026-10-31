# Add a New Locale

A **locale** supplies the words and conventions of a language: month names, the word for "present", and how a degree is joined to its subject. It translates only the text RenderCV writes itself; the CV's content stays exactly as the user wrote it. Every locale starts from the English one and replaces its values.

1. Create a YAML file in `src/rendercv/schema/models/locale/other_locales/`:

    ```bash
    touch src/rendercv/schema/models/locale/other_locales/mylanguage.yaml
    ```

2. Translate every value:

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
      phrases:
        degree_with_area: "DEGREE in AREA"
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

    In `degree_with_area`, keep the words `DEGREE` and `AREA`. They are **placeholders**: RenderCV replaces them with an education entry's degree and area, so `DEGREE in AREA` becomes "BS in Computer Science". Translate the words around them, and move them to wherever your language puts them.

    Take month names and abbreviations from [Unicode CLDR](https://github.com/unicode-org/cldr/tree/main/common/main), the shared database of each language's conventions for dates, numbers, and names that operating systems also use. Use its Gregorian **stand-alone** forms: the form a month name takes on its own, as in "January 2024". Some languages change a month's form inside a full date; Russian writes "январь" on its own but "5 января". RenderCV uses month names on their own, with CLDR's capitalization and punctuation ([CLDR's date guidance](https://cldr.unicode.org/translation/date-time/date-time-patterns)).

    RenderCV distinguishes only singular and plural, such as "1 year" and "2 years". Some languages use more forms: Polish says "1 rok", "2 lata", but "5 lat". For such languages, use an abbreviation that never changes; Polish uses "r." for both `year` and `years`.

3. Add the language to the two mappings in `src/rendercv/schema/models/locale/english_locale.py`.

    `language_iso_639_1` gives its two-letter code from ISO 639-1, the international list of language codes. The PDF and HTML record it as the document's language, which screen readers use to pronounce the text correctly, and Typst uses it to choose fonts for Chinese, Japanese, and Korean text:

    ```python
    return {
        "english": "en",
        # ... existing languages
        "mylanguage": "xx",
    }[self.language]
    ```

    `flag_emoji` gives a two-letter country code from ISO 3166-1, from which the language's flag emoji is built:

    ```python
    country = {
        "english": "GB",
        # ... existing languages
        "mylanguage": "XX",
    }[self.language]
    ```

4. Regenerate the schema, which lists every locale, then run the tests:

    ```bash
    just update-schema
    just test
    ```

5. Use it:

    ```bash
    rendercv new "John Doe" --locale mylanguage
    ```
