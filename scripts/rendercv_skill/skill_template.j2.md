---
name: rendercv
description: Create, edit, style, and render CVs and resumes with RenderCV {{ version }}, using YAML and Typst. Use for work on a user's CV or resume.
---

# RenderCV {{ version }}

Keep the user's facts and requested scope. Separate content (`cv`) from appearance
(`design`), date/phrase translations (`locale`), and rendering options (`settings`).

Preserve every supplied contact detail. A phone number needs a country code;
if only a local number is provided, ask for its country instead of guessing
or dropping the number to make validation pass.

## Start and verify

```sh
uv tool install "rendercv[full]=={{ version }}"
rendercv new "Jane Doe"
rendercv render Jane_Doe_CV.yaml
```

For an existing installation, check `rendercv --version`; these references describe
{{ version }}. Read an existing CV before editing it. Render after changes and inspect
the PDF or page images for layout and content loss. Fix the YAML or design rather
than editing generated files. Do not shrink text simply to force a page count.

## Read only the reference you need

- [Example YAML](references/example.yaml): entry shapes and a complete starting point.
- [JSON Schema](references/schema.json): exact fields, descriptions, types, and defaults.
  Search the relevant `$defs` instead of loading the whole schema.
- [CLI reference](references/cli.md): command options generated from the actual CLI.
- Theme defaults:
{% for theme in available_themes %}
  - [`{{ theme }}`](references/themes/{{ theme }}.yaml)
{% endfor %}

Locale catalogs: `{{ available_locales | join("`, `") }}`. These translate generated
phrases and dates; CV content and section titles can be written in any language.

## Contracts that matter

- Section keys are titles, in the user's chosen language. A subsection is an entry
  with `title` and `entries`. Entries within each list share one entry type.
- Dates use `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, or `present`. A custom `date` string is
  also allowed. `date` takes precedence over `start_date` and `end_date`.
- `DATE` includes the duration in the sections listed in
  `design.sections.show_time_spans_in`; the `time_span` template formats it.
- Field content uses Markdown. Each keyword in `settings.bold_keywords` is bolded as
  a whole word, punctuation included (`C++`), outside links and code. Prefer
  ordinary content over raw Typst.
- Paths in YAML are relative to the main CV file. Paths given on the command line
  are relative to the working directory.
- `--design`, `--locale-catalog`, and `--settings` replace whole components.
  `--overlay` files merge in order: mappings merge, lists and values are replaced.
  Dotted CLI overrides apply last.
- PDFs conform to PDF/UA-1 by default (`settings.pdf_profile: accessible`), which
  needs `cv.name` and alternative text for images in raw Typst.
- Page breaks are automatic, and headings stay with the content that follows them.
