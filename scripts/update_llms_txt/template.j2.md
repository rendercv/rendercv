# RenderCV YAML Input Reference

RenderCV generates professional CVs/resumes from YAML input files. Write your CV as YAML, run `rendercv render your_cv.yaml`, and get a PDF with perfect typography.

## YAML Structure Overview

A RenderCV YAML file has four top-level fields. Only `cv` is required.

```yaml
cv:        # Required. Your CV content (personal info and sections).
  ...
design:    # Optional. Visual styling (theme, colors, fonts, spacing).
  ...
locale:    # Optional. Language and date formatting.
  ...
settings:  # Optional. Output paths, generation flags, bold keywords.
  ...
```

## `cv` Field

### Personal Information (Header)

All header fields are optional. RenderCV adapts to whatever you provide.

```yaml
cv:
  name: John Doe
  headline: Machine Learning Engineer
  location: San Francisco, CA
  email: john@example.com
  phone: "+14155551234"
  website: https://johndoe.dev
  photo: photo.jpg
  social_networks:
    - network: LinkedIn
      username: johndoe
    - network: GitHub
      username: johndoe
  custom_connections:
    - placeholder: Book a call
      url: https://cal.com/johndoe
      fontawesome_icon: calendar-days
```

**Header fields:**

{% for field in cv_fields %}
- `{{ field.name }}`{% if field.required %} (required){% endif %}: {{ field.type }}.{% if field.description %} {{ field.description }}.{% endif %}{% if field.examples %} Examples: {{ field.examples | map('tojson') | join(', ') }}.{% endif %}{{ "" }}
{% endfor %}

**Available social networks:** {{ social_networks | join(', ') }}.

**`email`, `phone`, and `website` accept a single value or a list** for multiple entries.

### Sections

The `sections` field holds the main content of your CV. It is a dictionary where keys are section titles (displayed as headings) and values are lists of entries.

```yaml
cv:
  sections:
    experience:       # Section title (can be anything)
      - company: Acme Corp
        position: Senior Engineer
        start_date: 2020-01
        end_date: present
        highlights:
          - Led migration to microservices architecture
    skills:
      - label: Languages
        details: Python, Go, Rust
```

- Section titles are arbitrary strings. Use any name you want.
- Each section must contain only one type of entry. You cannot mix different entry types in the same section.
- Entry types are auto-detected based on the fields you provide.

### Entry Types

RenderCV provides {{ entry_types | length }} entry types:

{% for entry in entry_types %}
#### {{ entry.name }}

{{ entry.description }}
{% if entry.fields %}

| Field | Required | Type | Description |
| ----- | -------- | ---- | ----------- |
{% for field in entry.fields %}
| `{{ field.name }}` | {{ "Yes" if field.required else "No" }} | {{ field.type }} | {{ field.description or "" }} |
{% endfor %}
{% endif %}

{% if entry.name == "EducationEntry" %}
```yaml
- institution: Princeton University
  area: Computer Science
  degree: PhD
  start_date: 2018-09
  end_date: 2023-05
  location: Princeton, NJ
  highlights:
    - "Thesis: Efficient Neural Architecture Search"
    - NSF Graduate Research Fellowship
```
{% elif entry.name == "ExperienceEntry" %}
```yaml
- company: Nexus AI
  position: Co-Founder & CTO
  start_date: 2023-06
  end_date: present
  location: San Francisco, CA
  summary: Building foundation model infrastructure
  highlights:
    - Raised $18M Series A led by Sequoia Capital
    - Scaled engineering team from 3 to 28
```
{% elif entry.name == "PublicationEntry" %}
```yaml
- title: "Sparse Mixture-of-Experts at Scale"
  authors:
    - "*John Doe*"
    - Sarah Williams
  doi: 10.1234/neurips.2023.1234
  journal: NeurIPS 2023
  date: 2023-07
```
{% elif entry.name == "NormalEntry" %}
```yaml
- name: "[FlashInfer](https://github.com/)"
  start_date: 2023-01
  end_date: present
  summary: Open-source library for high-performance LLM inference
  highlights:
    - Achieved 2.8x speedup over baseline attention implementations
    - 8,500+ GitHub stars, 200+ contributors
```
{% elif entry.name == "OneLineEntry" %}
```yaml
- label: Languages
  details: Python, C++, CUDA, Rust, Julia
```
{% elif entry.name == "BulletEntry" %}
```yaml
- bullet: MIT Technology Review 35 Under 35 Innovators (2024)
```
{% elif entry.name == "NumberedEntry" %}
```yaml
- number: "Adaptive Quantization for Neural Network Inference (US Patent 11,234,567)"
```
{% elif entry.name == "ReversedNumberedEntry" %}
```yaml
- reversed_number: "Scaling Laws for Efficient Inference — Stanford HAI Symposium (2024)"
```
{% elif entry.name == "TextEntry" %}
```yaml
sections:
  summary:
    - Software engineer with 10 years of experience in distributed systems.
    - See the [documentation](https://docs.rendercv.com) for more details.
```
{% endif %}

{% endfor %}

### Date Formats

Fields `date`, `start_date`, and `end_date` accept:
- Full date: `2024-01-15` (YYYY-MM-DD)
- Month precision: `2024-01` (YYYY-MM)
- Year only: `2024` (YYYY)
- Custom text: `"Fall 2023"`, `"Summer 2020"` (for `date` field only)
- Ongoing: `present` (for `end_date` only)

### Text Formatting

All text fields support basic Markdown:
- `**text**` renders as bold
- `*text*` renders as italic
- `[text](url)` renders as a hyperlink
- `` `code` `` renders as inline code

All text fields also support Typst syntax:
- `$$f(x) = x^2$$` renders as math
- `#emph[text]` and other Typst commands work directly

### Arbitrary Keys

You can add custom fields to any entry. By default they are ignored, but you can reference them in `design.templates` as UPPERCASE placeholders.

```yaml
experience:
  - company: Startup Inc
    position: Founder
    start_date: 2020-01
    end_date: present
    revenue: $5M ARR  # Custom field, available as REVENUE in templates
```

## `design` Field

### Available Themes

Available themes: {{ themes | join(', ') }}.

All themes share the same design options but have different default values. If you specify a setting explicitly, it overrides the theme's default.

```yaml
design:
  theme: classic  # Choose a theme, then override any option below
```

### Design Options

Below are all available design options. All are optional; themes provide defaults.

{% for section in design_sections %}
#### `design.{{ section.name }}`

{% for field in section.fields %}
- `{{ field.name }}`: {{ field.type }}.{% if field.description %} {{ field.description }}.{% endif %}{% if field.default is not none %} Default: `{{ field.default }}`.{% endif %}

{% endfor %}
{% for sub in section.sub_sections %}
##### `design.{{ section.name }}.{{ sub.name }}`

{% for field in sub.fields %}
- `{{ field.name }}`: {{ field.type }}.{% if field.description %} {{ field.description }}.{% endif %}{% if field.default is not none %} Default: `{{ field.default }}`.{% endif %}

{% endfor %}
{% endfor %}
{% endfor %}

### Design Example

```yaml
design:
  theme: classic
  page:
    size: us-letter
    top_margin: 0.7in
    bottom_margin: 0.7in
    left_margin: 0.7in
    right_margin: 0.7in
    show_footer: true
    show_top_note: true
  colors:
    body: rgb(0, 0, 0)
    name: rgb(0, 79, 144)
    connections: rgb(0, 79, 144)
    section_titles: rgb(0, 79, 144)
    links: rgb(0, 79, 144)
  typography:
    line_spacing: 0.6em
    alignment: justified
    font_family: Source Sans 3  # Shorthand: applies to all elements
    font_size:
      body: 10pt
      name: 30pt
  links:
    underline: false
    show_external_link_icon: false
  header:
    alignment: center
    connections:
      phone_number_format: national
      show_icons: true
  section_titles:
    type: with_partial_line
  sections:
    show_time_spans_in:
      - experience
  entries:
    date_and_location_width: 4.15cm
    highlights:
      bullet: "\u2022"
  templates:
    footer: "*NAME -- PAGE_NUMBER/TOTAL_PAGES*"
    top_note: "*LAST_UPDATED CURRENT_DATE*"
    single_date: MONTH_ABBREVIATION YEAR
    date_range: "START_DATE \u2013 END_DATE"
    time_span: HOW_MANY_YEARS YEARS HOW_MANY_MONTHS MONTHS
    one_line_entry:
      main_column: "**LABEL:** DETAILS"
    education_entry:
      main_column: "**INSTITUTION**, AREA\nSUMMARY\nHIGHLIGHTS"
      degree_column: "**DEGREE**"
      date_and_location_column: "LOCATION\nDATE"
    normal_entry:
      main_column: "**NAME**\nSUMMARY\nHIGHLIGHTS"
      date_and_location_column: "LOCATION\nDATE"
    experience_entry:
      main_column: "**COMPANY**, POSITION\nSUMMARY\nHIGHLIGHTS"
      date_and_location_column: "LOCATION\nDATE"
    publication_entry:
      main_column: "**TITLE**\nSUMMARY\nAUTHORS\nURL (JOURNAL)"
      date_and_location_column: DATE
```

#### Template Placeholders

Templates use UPPERCASE placeholders that map to entry fields:
- **All entries:** DATE, LOCATION, SUMMARY, HIGHLIGHTS
- **ExperienceEntry:** COMPANY, POSITION
- **EducationEntry:** INSTITUTION, AREA, DEGREE
- **PublicationEntry:** TITLE, AUTHORS, URL, DOI, JOURNAL
- **NormalEntry:** NAME
- **OneLineEntry:** LABEL, DETAILS
- **Page-level:** NAME, PAGE_NUMBER, TOTAL_PAGES, LAST_UPDATED, CURRENT_DATE
- **Date templates:** MONTH_ABBREVIATION, MONTH_NAME, YEAR, START_DATE, END_DATE, HOW_MANY_YEARS, HOW_MANY_MONTHS, YEARS, MONTHS

You can also add arbitrary keys to entries and use them as UPPERCASE placeholders.

## `locale` Field

### Available Languages

Available languages: {{ locales | join(', ') }}.

```yaml
locale:
  language: german  # Use a built-in locale
  present: jetzt    # Override individual fields
```

### Customizable Fields

{% for field in locale_fields %}
- `{{ field.name }}`: {{ field.type }}.{% if field.description %} {{ field.description }}.{% endif %}{% if field.default is not none %} Default: `{{ field.default }}`.{% endif %}

{% endfor %}

## `settings` Field

{% for field in settings_fields %}
- `{{ field.name }}`: {{ field.type }}.{% if field.description %} {{ field.description }}.{% endif %}{% if field.default is not none %} Default: `{{ field.default }}`.{% endif %}

{% endfor %}

### `settings.render_command`

{% for field in render_command_fields %}
- `{{ field.name }}`: {{ field.type }}.{% if field.description %} {{ field.description }}.{% endif %}{% if field.default is not none %} Default: `{{ field.default }}`.{% endif %}

{% endfor %}

### Path Placeholders

Output path fields (`typst_path`, `pdf_path`, etc.) support these placeholders:

{% for p in path_placeholders %}
- `{{ p.name }}`: {{ p.description }}
{% endfor %}

## Complete Example

```yaml
{{ complete_example }}```
