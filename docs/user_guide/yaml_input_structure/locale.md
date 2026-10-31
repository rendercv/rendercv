# `locale` Field

The `locale` field lets you create a CV in any language by customizing month names, date formatting, and other language-specific text.

## Built-in Locales

RenderCV includes translations for << locale_count >> languages. To use one, simply specify the language:

```yaml
locale:
  language: german
```

Available languages: << available_locales >>.

## Section Titles

Section titles are your CV’s content. Write the keys under `cv.sections` in
any language, just as you write entry text:

```yaml
cv:
  sections:
    Esperienza lavorativa:
      - company: Acme
        position: Ingegnere
locale:
  language: italian
```

The locale translates generated words such as month names and “present”; it
does not translate your content. Options that identify sections, such as
`show_time_spans_in`, use the title in lowercase with spaces replaced by
underscores (`esperienza_lavorativa` here). Overlays use the exact YAML key.

## Customizing Locale

You can override any field to fine-tune the translations:

```yaml
locale:
  language: german
  present: jetzt  # Override just this field
```

Or create a completely custom locale:

```yaml
locale:
  language: english
  last_updated: Last updated in
  month: month
  months: months
  year: year
  years: years
  present: present
  month_abbreviations:
    - Jan
    - Feb
    - Mar
    - Apr
    - May
    - June
    - July
    - Aug
    - Sept
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
