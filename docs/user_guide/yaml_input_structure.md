# The YAML Input File

RenderCV uses a single YAML file to generate your CV. This file has four top-level fields:

```yaml title="Your_Name_CV.yaml"
cv:
  # Your content (name, sections, entries)
design:
  # Visual styling (theme, colors, fonts, spacing)
locale:
  # Language strings (month names, "present", etc.)
settings:
  # RenderCV behavior (current date, bold keywords)
```

Only `cv` is required. The others have sensible defaults.


!!! Tip
    To maximize your productivity while editing the input YAML file, set up RenderCV's JSON Schema in your IDE. It will validate your inputs on the fly and give auto-complete suggestions.

    === "Visual Studio Code"

        1. Install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml).
        2. Name your file ending with `_CV.yaml` — the schema activates automatically.
        3. Press `Ctrl + Space` for suggestions.

    === "Other Editors"

        1. Add this line at the top of your file:
            ```yaml
            # yaml-language-server: $schema=https://github.com/rendercv/rendercv/blob/main/schema.json?raw=true
            ```
        2. Press `Ctrl + Space` for suggestions (if your editor supports JSON Schema).


## The `cv` Field

### Header Information

The `cv` field begins with your personal information. All fields are optional — RenderCV adapts to whatever you provide.

```yaml
cv:
  name: John Doe
  headline: Machine Learning Engineer
  location: San Francisco, CA
  email: john@example.com
  phone: +14155551234
  website: https://johndoe.dev
  photo: photo.jpg
  social_networks:
    - network: LinkedIn
      username: johndoe
    - network: GitHub
      username: johndoe
```

| Field             | Description                                                                                                                                            |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`            | Your full name, displayed prominently in the header                                                                                                    |
| `headline`        | A brief professional title, shown below your name                                                                                                      |
| `location`        | City, state, country — whatever format you prefer                                                                                                      |
| `email`           | Your email address (automatically linked). Multiple emails can be provided as a list.                                                                  |
| `phone`           | Your Phone number. See `design.header.connections.phone_number_format` to control output formatting. Multiple phone numbers can be provided as a list. |
| `website`         | Your personal website or portfolio URL. Multiple websites can be provided as a list.                                                                   |
| `photo`           | Path to a headshot image (relative to the YAML file)                                                                                                   |
| `social_networks` | List of social profiles. Available networks: {{available_social_networks}}                                                                             |

### Sections

The `sections` field holds the main content of your CV. It's a dictionary where:

- **Keys** are section titles (displayed as headings)
- **Values** are lists of entries

```yaml
cv:
  name: John Doe
  sections:
    summary:
      - Software engineer with 10 years of experience in distributed systems.
    
    experience:
      - company: Acme Corp
        position: Senior Engineer
        start_date: 2020-01
        end_date: present
        highlights:
          - Led migration to microservices architecture
          - Reduced deployment time by 80%
    
    education:
      - institution: MIT
        area: Computer Science
        degree: BS
        start_date: 2012-09
        end_date: 2016-05
    
    skills:
      - label: Languages
        details: Python, Go, Rust, TypeScript
      - label: Infrastructure
        details: Kubernetes, Terraform, AWS
```

Section titles can be anything. RenderCV formats them automatically (e.g., `work_experience` becomes "Work Experience").

!!! warning "One entry type per section"
    Each section must contain only one type of entry. You cannot mix `ExperienceEntry` and `EducationEntry` in the same section.

## Entry Types

RenderCV provides {{entry_count}} entry types:
{% for entry_name in entry_names %}
{{ loop.index }}. {{ entry_name }}
{% endfor %}
 each designed for different kinds of content.

{% for entry_name, entry in sample_entries.items() %}
### {{ entry_name }}

{% if entry_name == "EducationEntry" %}
For academic credentials.

| Field         | Required | Description                              |
| ------------- | -------- | ---------------------------------------- |
| `institution` | Yes      | School or university name                |
| `area`        | Yes      | Field of study                           |
| `degree`      | No       | Degree type (BS, MS, PhD, etc.)          |
| `date`        | No       | Custom date string (overrides start/end) |
| `start_date`  | No       | Start date                               |
| `end_date`    | No       | End date (or `present`)                  |
| `location`    | No       | Institution location                     |
| `summary`     | No       | Brief description                        |
| `highlights`  | No       | List of bullet points                    |

{% elif entry_name == "ExperienceEntry" %}
For work history and professional roles.

| Field        | Required | Description                              |
| ------------ | -------- | ---------------------------------------- |
| `company`    | Yes      | Employer name                            |
| `position`   | Yes      | Job title                                |
| `date`       | No       | Custom date string (overrides start/end) |
| `start_date` | No       | Start date                               |
| `end_date`   | No       | End date (or `present`)                  |
| `location`   | No       | Office location                          |
| `summary`    | No       | Role description                         |
| `highlights` | No       | List of accomplishments                  |

{% elif entry_name == "PublicationEntry" %}
For papers, articles, and other publications.

| Field     | Required | Description                                      |
| --------- | -------- | ------------------------------------------------ |
| `title`   | Yes      | Publication title                                |
| `authors` | Yes      | List of author names (use `*Name*` for emphasis) |
| `doi`     | No       | Digital Object Identifier                        |
| `url`     | No       | Link to the publication                          |
| `journal` | No       | Journal, conference, or venue name               |
| `date`    | No       | Publication date                                 |

{% elif entry_name == "NormalEntry" %}
A flexible entry for projects, awards, certifications, or anything else.

| Field        | Required | Description                              |
| ------------ | -------- | ---------------------------------------- |
| `name`       | Yes      | Entry title                              |
| `date`       | No       | Custom date string (overrides start/end) |
| `start_date` | No       | Start date                               |
| `end_date`   | No       | End date (or `present`)                  |
| `location`   | No       | Associated location                      |
| `summary`    | No       | Brief description                        |
| `highlights` | No       | List of bullet points                    |

{% elif entry_name == "OneLineEntry" %}
For compact key-value pairs, ideal for skills or technical proficiencies.

| Field     | Required | Description        |
| --------- | -------- | ------------------ |
| `label`   | Yes      | Category name      |
| `details` | Yes      | Associated details |

{% elif entry_name == "BulletEntry" %}
A single bullet point. Use for simple lists.

| Field    | Required | Description     |
| -------- | -------- | --------------- |
| `bullet` | Yes      | The bullet text |

{% elif entry_name == "NumberedEntry" %}
An automatically numbered entry.

| Field    | Required | Description       |
| -------- | -------- | ----------------- |
| `number` | Yes      | The entry content |

{% elif entry_name == "ReversedNumberedEntry" %}
A numbered entry that counts down (useful for publication lists where recent items come first).

| Field             | Required | Description       |
| ----------------- | -------- | ----------------- |
| `reversed_number` | Yes      | The entry content |

{% elif entry_name == "TextEntry" %}
Plain text without structure. Just write a string.

{% endif %}

```yaml
{{ entry["yaml"] }}
```

{% for figure in entry["figures"] %}
=== "`{{ figure["theme"] }}` theme"
    ![{{ figure["alt_text"] }}]({{ figure["path"] }})
{% endfor %}

{% endfor %}

### Date Formats

Dates accept multiple formats:

| Format        | Example         | Output      |
| ------------- | --------------- | ----------- |
| `YYYY-MM-DD`  | `2023-06-15`    | June 2023   |
| `YYYY-MM`     | `2023-06`       | June 2023   |
| `YYYY`        | `2023`          | 2023        |
| `present`     | `present`       | present     |
| Custom string | `"Summer 2023"` | Summer 2023 |

The `date` field accepts any string and displays it verbatim, useful for non-standard formats like "Expected May 2025" or "Fall 2023".

### Markdown in Entries

All text fields support basic Markdown:

```yaml
highlights:
  - Increased revenue by **$2M** annually
  - Developed [open-source tool](https://github.com/example) with *500+ stars*
```

| Syntax        | Result    |
| ------------- | --------- |
| `**text**`    | **bold**  |
| `*text*`      | *italic*  |
| `[text](url)` | hyperlink |

### Custom Keys

You can add arbitrary keys to any entry. By default, they're ignored — but you can reference them in custom templates (see `design.templates`). See [Arbitrary Keys in Entries](../user_guide/how_to/arbitrary_keys_in_entries.md) for more information.

```yaml
experience:
  - company: Startup Inc
    position: Founder
    start_date: 2020-01
    end_date: present
    revenue: $5M ARR  # Custom field
    highlights:
      - Built product from zero to profitability
```

## The `design` Field

The `design` field controls the visual appearance of your CV. Start by choosing a theme:

```yaml
design:
  theme: classic
```

Available themes: {{available_themes}}

Each theme has different default styling, but all options can be customized. The themes share the same underlying template — you can recreate any theme by adjusting the design options.

!!! tip "Use the JSON Schema"
    The design options are extensive. Use an editor with JSON Schema support to explore all available options with autocomplete.

### Complete Example

Below is a fully specified `design` field showing all available options:

```yaml
design:
  theme: classic
  
  page:
    size: us-letter              # (1)!
    top_margin: 0.7in
    bottom_margin: 0.7in
    left_margin: 0.7in
    right_margin: 0.7in
    show_footer: true            
    show_top_note: true         
  
  colors:
    body: rgb(0, 0, 0)
    name: rgb(0, 79, 144)
    headline: rgb(0, 79, 144)
    connections: rgb(0, 79, 144)
    section_titles: rgb(0, 79, 144)
    links: rgb(0, 79, 144)
    footer: rgb(128, 128, 128)
    top_note: rgb(128, 128, 128)
  
  typography:
    line_spacing: 0.6em
    alignment: justified         # (2)!
    date_and_location_column_alignment: right
    font_family:
      body: Source Sans 3        # (9)!
      name: Source Sans 3
      headline: Source Sans 3
      connections: Source Sans 3
      section_titles: Source Sans 3
    font_size:
      body: 10pt
      name: 30pt
      headline: 10pt
      connections: 10pt
      section_titles: 1.4em
    small_caps:
      name: false
      headline: false
      connections: false
      section_titles: false
    bold:
      name: true
      headline: false
      connections: false
      section_titles: true
  
  links:
    underline: false
    show_external_link_icon: false
  
  header:
    alignment: center            # (3)!
    photo_width: 3.5cm
    photo_position: left         # (8)!
    photo_space_left: 0.4cm
    photo_space_right: 0.4cm
    space_below_name: 0.7cm
    space_below_headline: 0.7cm
    space_below_connections: 0.7cm
    connections:
      phone_number_format: national  # (7)!
      hyperlink: true
      show_icons: true
      display_urls_instead_of_usernames: false
      separator: ''
      space_between_connections: 0.5cm
  
  section_titles:
    type: with_partial_line      # (4)!
    line_thickness: 0.5pt
    space_above: 0.5cm
    space_below: 0.3cm
  
  sections:
    allow_page_break: true
    space_between_regular_entries: 1.2em
    space_between_text_based_entries: 0.3em
    show_time_spans_in:          # (5)!
      - experience
  
  entries:
    date_and_location_width: 4.15cm
    side_space: 0.2cm
    space_between_columns: 0.1cm
    allow_page_break: false
    short_second_row: true
    summary:
      space_above: 0cm
      space_left: 0cm
    highlights:
      bullet: •                  # (6)!
      nested_bullet: •
      space_left: 0.15cm
      space_above: 0cm
      space_between_items: 0cm
      space_between_bullet_and_text: 0.5em
  
  templates: # (10)!
    footer: '*NAME -- PAGE_NUMBER/TOTAL_PAGES*'
    top_note: '*LAST_UPDATED CURRENT_DATE*'
    single_date: MONTH_ABBREVIATION YEAR
    date_range: START_DATE – END_DATE
    time_span: HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS
    one_line_entry:
      main_column: '**LABEL:** DETAILS'
    education_entry:
      main_column: |-
        **INSTITUTION**, AREA
        SUMMARY
        HIGHLIGHTS
      degree_column: '**DEGREE**'
      date_and_location_column: |-
        LOCATION
        DATE
    normal_entry:
      main_column: |-
        **NAME**
        SUMMARY
        HIGHLIGHTS
      date_and_location_column: |-
        LOCATION
        DATE
    experience_entry:
      main_column: |-
        **COMPANY**, POSITION
        SUMMARY
        HIGHLIGHTS
      date_and_location_column: |-
        LOCATION
        DATE
    publication_entry:
      main_column: |-
        **TITLE**
        AUTHORS
        URL (JOURNAL)
      date_and_location_column: DATE
```

1. {{available_page_sizes}}
2. {{available_body_alignments}}
3. {{available_alignments}}
4. {{available_section_title_types}}
5. Sections that show duration (e.g., "2 years")
6. {{available_bullets}}
7. {{available_phone_number_formats}}
8. `left`, `right`
9. {{available_font_families}}
10. Advanced: customize entry rendering

### Template Placeholders

The `templates` section uses placeholders that RenderCV replaces with actual values:

| Placeholder          | Description                       |
| -------------------- | --------------------------------- |
| `NAME`               | Your name from `cv.name`          |
| `PAGE_NUMBER`        | Current page number               |
| `TOTAL_PAGES`        | Total page count                  |
| `CURRENT_DATE`       | Date from `settings.current_date` |
| `LAST_UPDATED`       | Text from `locale.last_updated`   |
| `MONTH_ABBREVIATION` | Abbreviated month name            |
| `YEAR`               | Four-digit year                   |
| `START_DATE`         | Formatted start date              |
| `END_DATE`           | Formatted end date                |
| `HOW_MANY_YEARS`     | Duration in years                 |
| `HOW_MANY_MONTHS`    | Duration in months                |

Entry-specific placeholders (like `COMPANY`, `POSITION`, `INSTITUTION`) correspond to the entry's fields.

## The `locale` Field

The `locale` field lets you customize all language-specific strings. This is how you create a CV in any language.

```yaml
locale:
  language: german
  last_updated: Zuletzt aktualisiert am
  month: Monat
  months: Monate
  year: Jahr
  years: Jahre
  present: heute
  month_abbreviations:
    - Jan
    - Feb
    - März
    - Apr
    - Mai
    - Juni
    - Juli
    - Aug
    - Sept
    - Okt
    - Nov
    - Dez
  month_names:
    - Januar
    - Februar
    - März
    - April
    - Mai
    - Juni
    - Juli
    - August
    - September
    - Oktober
    - November
    - Dezember
```

| Field                 | Description                             |
| --------------------- | --------------------------------------- |
| `language`            | Language name (for your reference only) |
| `last_updated`        | Text before the date in the top note    |
| `month` / `months`    | Singular/plural for duration display    |
| `year` / `years`      | Singular/plural for duration display    |
| `present`             | Text shown when `end_date` is `present` |
| `month_abbreviations` | 12 abbreviated month names (Jan–Dec)    |
| `month_names`         | 12 full month names                     |

## The `settings` Field

The `settings` field configures RenderCV's behavior.

```yaml
settings:
  current_date: '2025-12-03'
  render_command:
    design:
    locale:
    typst_path: rendercv_output/NAME_IN_SNAKE_CASE_CV.typ
    pdf_path: rendercv_output/NAME_IN_SNAKE_CASE_CV.pdf
    markdown_path: rendercv_output/NAME_IN_SNAKE_CASE_CV.md
    html_path: rendercv_output/NAME_IN_SNAKE_CASE_CV.html
    png_path: rendercv_output/NAME_IN_SNAKE_CASE_CV.png
    dont_generate_markdown: false
    dont_generate_html: false
    dont_generate_typst: false
    dont_generate_pdf: false
    dont_generate_png: false
  bold_keywords:
    - AWS
    - Python
```

| Field           | Description                                                                                                |
| --------------- | ---------------------------------------------------------------------------------------------------------- |
| `current_date`  | Reference date for duration calculations and "last updated" text. Format: `YYYY-MM-DD`. Defaults to today. |
| `bold_keywords` | List of words to automatically bold throughout the CV. Useful for highlighting key skills.                 |
