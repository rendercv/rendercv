# `locale` Field

The `locale` field lets you create a CV in any language by customizing month names, date formatting, and other language-specific text.

## Built-in Locales

RenderCV includes translations for 12 languages. To use one, simply specify the language:

```yaml
locale:
  language: german
```

Available languages: << available_locales >>.

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
