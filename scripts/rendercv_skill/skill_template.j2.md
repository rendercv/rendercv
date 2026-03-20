---
name: rendercv
description: >-
  Create professional CVs and resumes with perfect typography using RenderCV
  (v{{ version }}). Users write content in YAML, and RenderCV produces
  publication-quality PDFs via Typst typesetting. Full control over every visual
  detail: colors, fonts, margins, spacing, section title styles, entry layouts,
  and more. {{ available_themes | length }} built-in themes with unlimited
  customization. Any language supported ({{ available_locales | length }} built-in, or define your own). Outputs
  PDF, PNG, HTML, and Markdown. Use when the user wants to create, edit,
  customize, or render a CV or resume.
---

## Quick Start

**Available themes:** `{{ available_themes | join("`, `") }}`
**Available locales:** `{{ available_locales | join("`, `") }}`

These are starting points — every aspect of the design and locale can be fully customized in the YAML file.

```bash
# Install RenderCV
uv tool install "rendercv[full]"

# Create a starter YAML file (you can specify theme and locale)
rendercv new "John Doe"
rendercv new "John Doe" --theme moderncv --locale german

# Render to PDF (also generates Typst, Markdown, HTML, PNG by default)
rendercv render John_Doe_CV.yaml

# Watch mode: auto-re-render whenever the YAML file changes
rendercv render John_Doe_CV.yaml --watch

# Render only PNG (useful for previewing or checking page count)
rendercv render John_Doe_CV.yaml --dont-generate-pdf --dont-generate-html --dont-generate-markdown

# Override fields from the CLI without editing the YAML
rendercv render cv.yaml --cv.name "Jane Doe" --design.theme "moderncv"
```

## YAML Structure

A RenderCV input has four sections. Only `cv` is required — the others have sensible defaults.

```yaml
cv:         # Your content: name, contact info, and all sections
design:     # Visual styling: theme, colors, fonts, margins, spacing, layouts
locale:     # Language: month names, phrases, translations
settings:   # Behavior: output paths, bold keywords, current date
```

**Single file vs. separate files:** All four sections can live in one YAML file, or each can be a separate file. Separate files are useful for reusing the same design/locale across multiple CVs:

```bash
# Single self-contained file (all sections in one file)
rendercv render John_Doe_CV.yaml

# Separate files: CV content + design + locale loaded independently
rendercv render cv.yaml --design design.yaml --locale-catalog locale.yaml --settings settings.yaml
```

When using separate files, each file contains only its section (e.g., `design.yaml` has `design:` as the top-level key). CLI-loaded files override values in the main YAML file.

The YAML maps directly to Pydantic models. The complete type-safe schema is provided below so you can understand every field, its type, and its default value.

## Pydantic Schema

The YAML input is validated against these Pydantic models.

### Top-Level Model

```python
{{ model_sources.rendercv_model }}
```

### CV Content (`cv`)

The `cv.sections` field is a dictionary where keys are section titles (any string you want) and values are lists of entries. Each section contains entries of the same type.

```python
{{ model_sources.cv }}
```

```python
{{ model_sources.social_network }}
```

```python
{{ model_sources.custom_connection }}
```

### Entry Types

`cv.sections` is a dictionary: keys are section titles (any string), values are lists of entries. Each section must use a **single** entry type — you cannot mix different entry types within the same section. The entry type is auto-detected from the fields present in each entry.

**Shared fields** — these are available on entry types that support dates and complex fields (ExperienceEntry, EducationEntry, NormalEntry, PublicationEntry):

| Field | Type | Default | Notes |
|---|---|---|---|
| `date` | `str \| int \| null` | `null` | Free-form: `"2020-09"`, `"Fall 2023"`, etc. Mutually exclusive with `start_date`/`end_date`. |
| `start_date` | `str \| int \| null` | `null` | Strict format: YYYY-MM-DD, YYYY-MM, or YYYY. |
| `end_date` | `str \| int \| "present" \| null` | `null` | Same formats as `start_date`, or `"present"`. Omitting defaults to `"present"` when `start_date` is set. |
| `location` | `str \| null` | `null` | |
| `summary` | `str \| null` | `null` | |
| `highlights` | `list[str] \| null` | `null` | Bullet points. |

**9 entry types:**

| Entry Type | Required Fields | Optional Fields | Typical Use |
|---|---|---|---|
| **ExperienceEntry** | `company`, `position` | all shared fields | Jobs, positions |
| **EducationEntry** | `institution`, `area` | `degree` + all shared fields | Degrees, schools |
| **PublicationEntry** | `title`, `authors` | `doi`, `url`, `journal`, `summary`, `date` | Papers, articles |
| **NormalEntry** | `name` | all shared fields | Projects, awards |
| **OneLineEntry** | `label`, `details` | — | Skills, languages |
| **BulletEntry** | `bullet` | — | Simple bullet points |
| **NumberedEntry** | `number` | — | Numbered list items |
| **ReversedNumberedEntry** | `reversed_number` | — | Reverse-numbered items (5, 4, 3...) |
| **TextEntry** | *(plain string)* | — | Free-form paragraphs |

Example:

```yaml
cv:
  sections:
    experience:          # list of ExperienceEntry (detected by company + position)
      - company: Google
        position: Engineer
        start_date: 2020-01
        highlights:
          - Did something impactful
    skills:              # list of OneLineEntry (detected by label + details)
      - label: Languages
        details: Python, C++
    about_me:            # list of TextEntry (plain strings)
      - This is a free-form paragraph about me.
```

Entries also accept arbitrary extra keys (silently ignored during rendering). A typo in a field name will NOT cause an error.

### Design (`design`)

All built-in themes share the same structure — they only differ in default values. See the sample designs below for every available field and its default. Set `design.theme` to pick a theme, then override any field.

### Locale (`locale`)

Built-in locales: `{{ available_locales | join("`, `") }}`

Set `locale.language` to a built-in locale name to use it. Override any field to customize translations. Set `language` to any string and provide all translations for a fully custom locale.

### Settings (`settings`)

Key fields: `bold_keywords` (list of strings to auto-bold), `current_date` (override today's date), `render_command.*` (output paths, generation flags).

## Important Patterns

### YAML quoting

**ALWAYS quote string values that contain a colon (`:`).** This is the most common cause of invalid YAML. Highlights, titles, summaries, and any free-form text often contain colons:

```yaml
# WRONG — colon breaks YAML parsing:
- title: Catalytic Mechanisms: A New Approach
  highlights:
    - Relevant coursework: Distributed Systems, ML

# RIGHT — wrap in double quotes:
- title: "Catalytic Mechanisms: A New Approach"
  highlights:
    - "Relevant coursework: Distributed Systems, ML"
```

Rule: if a string value contains `:`, it MUST be quoted. When in doubt, quote it.

### Bullet characters

The `design.highlights.bullet` field only accepts these exact characters: `●`, `•`, `◦`, `-`, `◆`, `★`, `■`, `—`, `○`. Do not use en-dash (`–`), `>`, `*`, or any other character. When in doubt, omit `bullet` to use the theme default.

### Phone numbers

Phone numbers MUST be in international format with country code (E.164). Never invent a phone number — only include one if the user provides it.

```yaml
# WRONG:
phone: "(555) 123-4567"
phone: "555-123-4567"

# RIGHT:
phone: "+15551234567"
```

If the user provides a local number without country code, ask which country, or omit the phone field.

### Text formatting

All text fields support inline Markdown: `**bold**`, `*italic*`, `[link text](url)`. Block-level Markdown (headers, lists, blockquotes, code blocks) is not supported. Raw Typst commands and math (`$$f(x)$$`) also pass through.

### Date handling

- `date` and `start_date`/`end_date` are mutually exclusive. If `date` is provided, `start_date` and `end_date` are ignored.
- If only `start_date` is given, `end_date` defaults to `"present"`.
- `start_date`/`end_date` require strict formats: YYYY-MM-DD, YYYY-MM, or YYYY.
- `date` is flexible: accepts any string ("Fall 2023") in addition to date formats.

### Section titles

- `snake_case` keys auto-capitalize: `work_experience` → "Work Experience"
- Keys with spaces or uppercase are used as-is.

### Publication authors

Use `*Name*` (single asterisks, italic) to highlight the CV owner in author lists.

### Nested highlights (sub-bullets)

```yaml
highlights:
  - Main bullet point
    - Sub-bullet 1
    - Sub-bullet 2
```

## CLI Reference

### `rendercv new "Full Name"`

Generate a starter YAML file.

| Option | Short | What it does |
|---|---|---|
| `--theme THEME` | | Theme to use (default: `classic`) |
| `--locale LOCALE` | | Locale to use (default: `english`) |
| `--create-typst-templates` | | Also create editable Typst template files for full design control |

### `rendercv render <input.yaml>`

Generate PDF, Typst, Markdown, HTML, and PNG from a YAML file.

| Option | Short | What it does |
|---|---|---|
| `--watch` | `-w` | Re-render automatically when the YAML file changes |
| `--quiet` | `-q` | Suppress all output messages |
| `--design FILE` | `-d` | Load design section from a separate YAML file |
| `--locale-catalog FILE` | `-lc` | Load locale section from a separate YAML file |
| `--settings FILE` | `-s` | Load settings section from a separate YAML file |
| `--output-folder DIR` | `-o` | Custom output directory |

Per-format controls: `--{format}-path PATH` sets custom output path, `--dont-generate-{format}` skips generation. Formats: `pdf`, `typst`, `markdown`, `html`, `png`.

**Override any YAML field from the CLI** using dot notation (overrides without editing the file):

```bash
rendercv render CV.yaml --cv.name "Jane Doe" --design.theme "moderncv"
rendercv render CV.yaml --cv.sections.education.0.institution "MIT"
```

### `rendercv create-theme "theme-name"`

Scaffold a custom theme directory with editable Typst templates for complete design control.

## JSON Schema

For YAML editor autocompletion and validation:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v{{ version }}/schema.json
```

## Complete Example

### Sample CV

```yaml
{{ sample_cv }}
```

### Sample Design (classic — complete reference)

This shows every available design field with its default value. All themes share the same structure.

```yaml
{{ sample_classic_design }}
```

### Other Theme Overrides

Other themes only override specific fields from the classic defaults above. To use a theme, set `design.theme` and optionally override any field. Each theme also customizes `design.templates` (entry layout patterns) — see the classic sample above for the full template structure. The override YAMLs below omit templates for brevity.

{% for theme, yaml in theme_overrides.items() %}
#### {{ theme }}

```yaml
{{ yaml }}
```

{% endfor %}
