# `design` Field

The `design` field controls every visual aspect of your CV: colors, fonts, spacing, and layout.

## Available Themes

RenderCV includes << theme_count >> built-in themes. To use one, simply specify the theme:

```yaml
design:
  theme: classic
```

Available themes: << available_themes >>

## How Themes Work

All themes are identical except for their default values. If you specify a setting explicitly, it overrides the theme's default. This means:

- If you specify all design options in your YAML, changing the theme has no effect
- If you leave settings unspecified, changing the theme completely changes the design (because it uses different defaults)
- You can start with any theme and customize only what you want to change

## Customizing Design

You can override any field to fine-tune the theme:

```yaml
design:
  theme: classic
  colors:
    name: rgb(255, 0, 0)  # Override just the name color
```

Or specify all options for complete control:

```yaml
design:
  theme: classic

  page:
    size: us-letter # (1)!
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
    alignment: justified # (2)!
    date_and_location_column_alignment: right
    font_family: # (11)!
      body: Source Sans 3 # (9)!
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
    alignment: center # (3)!
    photo_width: 3.5cm
    photo_position: left # (8)!
    photo_space_left: 0.4cm
    photo_space_right: 0.4cm
    space_below_name: 0.7cm
    space_below_headline: 0.7cm
    space_below_connections: 0.7cm
    connections:
      phone_number_format: national # (7)!
      hyperlink: true
      show_icons: true
      display_urls_instead_of_usernames: false
      separator: ''
      space_between_connections: 0.5cm

  section_titles:
    type: with_partial_line # (4)!
    line_thickness: 0.5pt
    space_above: 0.5cm
    space_below: 0.3cm

  sections:
    allow_page_break: true
    space_between_regular_entries: 1.2em
    space_between_text_based_entries: 0.3em
    show_time_spans_in: # (5)!
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
      bullet: • # (6)!
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

1. **Page size options:** << available_page_sizes >>
2. **Body text alignment:** << available_body_alignments >>
   `justified` spreads text across the full width, `justified-with-no-hyphenation` does the same without breaking words
3. **Header alignment:** << available_alignments >>
4. **Section title styles:** << available_section_title_types >>
   `with_partial_line` adds a line next to the title, `with_full_line` spans the page, `without_line` has no line, `moderncv` uses ModernCV style
5. **Show time spans:** Specify which sections should display duration calculations (e.g., "2 years 3 months")
6. **Bullet characters:** << available_bullets >>
7. **Phone number formats:** << available_phone_number_formats >>
   `national` formats for domestic use, `international` includes country code, `E164` is the standard international format
8. **Photo position:** `left` or `right` of the header text
9. **Available fonts:** << available_font_families >>. Also, any system font can be used. Custom fonts can be used as well. See [Custom Fonts](../how_to/custom_fonts.md) for more information.
10. **Templates:** Advanced customization - define how each entry type is rendered using placeholders like NAME, COMPANY, DATE, etc.
11. **Font family shorthand:** You can specify `font_family: "Latin Modern Roman"` directly instead of using nested options to apply the same font everywhere
