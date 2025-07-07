# Structure of the YAML Input File

RenderCV's input file consists of four parts: `cv`, `design`, `locale` and `rendercv_settings`.

```yaml title="Your_Name_CV.yaml"
cv:
  ...
  YOUR CONTENT
  ...
design:
  ...
  YOUR DESIGN
  ...
locale:
  ...
  TRANSLATIONS TO YOUR LANGUAGE
  ...
rendercv_settings:
  ...
  RENDERCV SETTINGS
  ...
```

- The `cv` field is mandatory. It contains the **content of the CV**.
- The `design` field is optional. It contains the **design options of the CV**. If you don't provide a `design` field, RenderCV will use the default design options with the `classic` theme.
- The `locale` field is optional. It contains all the strings that define the CV's language (like month names, etc.). If you don't provide a `locale` field, the default English strings will be used.
- The `rendercv_settings` field is optional. It contains the settings of RenderCV (output paths, keywords to make bold, etc.). If you don't provide a `rendercv_settings` field, the default settings will be used.

!!! tip "Tip: JSON Schema"
    To maximize your productivity while editing the input YAML file, set up RenderCV's JSON Schema in your IDE. It will validate your inputs on the fly and give auto-complete suggestions.

    === "Visual Studio Code"

        1.  Install [YAML language support](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) extension.
        2.  Then the Schema will be automatically set up because the file ends with `_CV.yaml`.
        3.  Press `Ctrl + Space` to see the auto-complete suggestions.

    === "Other"

        4.  Ensure your editor of choice has support for JSON Schema.
        5.  Add the following line at the top of `Your_Name_CV.yaml`:

            ``` yaml
            # yaml-language-server: $schema=https://github.com/rendercv/rendercv/blob/main/schema.json?raw=true
            ```
        6. Press `Ctrl + Space` to see the auto-complete suggestions.

## "`cv`" field

The `cv` field of the YAML input starts with generic information, as shown below.

```yaml
cv:
  name: John Doe
  location: Your Location
  email: youremail@yourdomain.com
  phone: +905419999999 # (1)!
  website: https://example.com/
  connections_order: [location, email, phone, website, social_networks]
  social_networks:
    - network: LinkedIn # (2)!
      username: yourusername
    - network: GitHub 
      username: yourusername
  ...
```

1.  If you want to change the phone number formatting in the output, see the `locale` field's `phone_number_format` key.
2.  The available social networks are: {{available_social_networks}}.
3.  Use `connections_order` to customize the order of the items shown in
    the header. Valid values are `location`, `email`, `phone`, `website`,
    and `social_networks`.

None of the values above are required. You can omit any or all of them, and RenderCV will adapt to your input. These generic fields are used in the header of the CV.

The main content of your CV is stored in a field called `sections`.

```yaml hl_lines="12 13 14 15"
cv:
  name: John Doe
  location: Your Location
  email: youremail@yourdomain.com
  phone: +905419999999
  website: https://yourwebsite.com/
  connections_order: [location, email, phone, website, social_networks]
  social_networks:
    - network: LinkedIn
      username: yourusername
    - network: GitHub
      username: yourusername
  sections:
    ...
    YOUR CONTENT
    ...
```

### "`cv.sections`" field

The `cv.sections` field is a dictionary where the keys are the section titles, and the values are lists. Each item of the list is an entry for that section.

Here is an example:

```yaml hl_lines="3 7"
cv:
  sections:
    this_is_a_section_title: # (1)!
      - This is a TextEntry. # (2)!
      - This is another TextEntry under the same section.
      - This is another another TextEntry under the same section.
    this_is_another_section_title:
      - company: This time it's an ExperienceEntry. # (3)!
        position: Your position
        start_date: 2019-01-01
        end_date: 2020-01
        location: TX, USA
        highlights: 
          - This is a highlight (a bullet point).
          - This is another highlight.
      - company: Another ExperienceEntry.
        position: Your position
        start_date: 2019-01-01
        end_date: 2020-01-10
        location: TX, USA
        highlights: 
          - This is a highlight (a bullet point).
          - This is another highlight.
```

1. The section titles can be anything you want. They are the keys of the `sections` dictionary.
2. Each section is a list of entries. This section has three `TextEntry`s.
3. There are seven different entry types in RenderCV. Any of them can be used in the sections. This section has two `ExperienceEntry`s.

There are seven different entry types in RenderCV. Different types of entries cannot be mixed under the same section, so for each section, you can only use one type of entry.

The available entry types are: [`EducationEntry`](#educationentry), [`ExperienceEntry`](#experienceentry), [`PublicationEntry`](#publicationentry), [`NormalEntry`](#normalentry), [`OneLineEntry`](#onelineentry), [`BulletEntry`](#bulletentry), and [`TextEntry`](#textentry).

Each entry type is a different object (a dictionary). Below, you can find all the entry types along with their optional/mandatory fields and how they appear in each built-in theme.

{% for entry_name, entry in sample_entries.items() %}
#### {{ entry_name }}

{% if entry_name == "EducationEntry" %}

**Mandatory Fields:**

- `institution`: The name of the institution.
- `area`: The area of study.

**Optional Fields:**

- `degree`: The type of degree (e.g., BS, MS, PhD)
- `location`: The location
- `start_date`: The start date in `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` format
- `end_date`: The end date in `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` format or "present"
- `date`: The date as a custom string or in `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` format. This will override `start_date` and `end_date`.
- `summary`: The summary
- `highlights`: The list of bullet points

{% elif entry_name == "ExperienceEntry" %}

**Mandatory Fields:**

- `company`: The name of the company
- `position`: The position

**Optional Fields:**

- `location`: The location
- `start_date`: The start date in `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` format
- `end_date`: The end date in `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` format or "present"
- `date`: The date as a custom string or in `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` format. This will override `start_date` and `end_date`.
- `summary`: The summary
- `highlights`: The list of bullet points

{% elif entry_name == "PublicationEntry" %}

**Mandatory Fields:**

- `title`: The title of the publication
- `authors`: The authors of the publication

**Optional Fields:**

- `doi`: The DOI of the publication
- `url`: The URL of the publication
- `journal`: The journal of the publication
- `date`: The date as a custom string or in `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` format

{% elif entry_name == "NormalEntry" %}


**Mandatory Fields:**

- `name`: The name of the entry

**Optional Fields:**

- `location`: The location
- `start_date`: The start date in `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` format
- `end_date`: The end date in `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` format or "present"
- `date`: The date as a custom string or in `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` format. This will override `start_date` and `end_date`.
- `summary`: The summary
- `highlights`: The list of bullet points

{% elif entry_name == "OneLineEntry" %}

**Mandatory Fields:**

- `label`: The label of the entry
- `details`: The details of the entry

{% elif entry_name == "BulletEntry" %}

**Mandatory Fields:**

- `bullet`: The bullet point

{% elif entry_name == "NumberedEntry" %}

**Mandatory Fields:**

- `number`: The content of the numbered entry

{% elif entry_name == "ReversedNumberedEntry" %}

The `ReversedNumberedEntry` displays entries in descending numerical order.

**Mandatory Fields:**

- `reversed_number`: The content of the reversed numbered entry

{% elif entry_name == "TextEntry" %}

**Mandatory Fields:**

- The text itself

{% endif %}

```yaml
{{ entry["yaml"] }}
```
    {% for figure in entry["figures"] %}
=== "`{{ figure["theme"] }}` theme"
    ![figure["alt_text"]]({{ figure["path"] }})
    {% endfor %}
{% endfor %}

#### Markdown Syntax

All the fields in the entries support Markdown syntax.

You can make anything bold by surrounding it with `**`, italic with `*`, and links with `[]()`, as shown below.

```yaml
company: "**This will be bold**, *this will be italic*, 
  and [this will be a link](https://example.com)."
...
```

### Using arbitrary keys

RenderCV allows the usage of any number of extra keys in the entries. For instance, the following is an `ExperienceEntry` containing an additional key, `an_arbitrary_key`.

```yaml hl_lines="6"
company: Some Company
location: TX, USA
position: Software Engineer
start_date: 2020-07
end_date: '2021-08-12'
an_arbitrary_key: Developed an [IOS application](https://example.com).
highlights:
  - Received more than **100,000 downloads**.
  - Managed a team of **5** engineers.
```

By default, the `an_arbitrary_key` key will not affect the output as the default design options do not use it. However, you can use the `an_arbitrary_key` key in your own design options (see `design.entry_types` field).

## "`design`" field

The `design` field contains your theme selection and its options. Currently, the available themes are: {{available_themes}}. The only difference between the themes are the `design` options. Their Typst templates are the same. Any theme can be obtained by playing with the `design` options. Custom themes can also be created (see [here](faq.md#how-to-create-a-custom-theme)).

```yaml
design:
  theme: classic
  ...
```

Use an IDE that supports JSON schema to avoid missing any available options for the theme (see [above](#structure-of-the-yaml-input-file)).

An example `design` field for a `classic` theme is shown below:

```yaml
design:
  theme: classic # (1)!
  page:
    size: us-letter # (2)!
    top_margin: 2cm
    bottom_margin: 2cm
    left_margin: 2cm
    right_margin: 2cm
    show_page_numbering: true
    show_last_updated_date: true
  colors:
    text: black
    name: '#004f90'
    connections: '#004f90'
    section_titles: '#004f90'
    links: '#004f90'
    last_updated_date_and_page_numbering: grey
  text:
    font_family: Source Sans 3 # (3)!
    font_size: 10pt
    leading: 0.6em
    alignment: justified # (4)!
    date_and_location_column_alignment: right # (5)!
  links:
    underline: false
    use_external_link_icon: true
  header:
    name_font_family: Source Sans 3
    name_font_size: 30pt
    name_bold: true
    small_caps_for_name: false
    photo_width: 3.5cm
    vertical_space_between_name_and_connections: 0.7cm
    vertical_space_between_connections_and_first_section: 0.7cm
    horizontal_space_between_connections: 0.5cm
    connections_font_family: Source Sans 3
    separator_between_connections: ''
    use_icons_for_connections: true
    alignment: center # (6)!
  section_titles:
    type: with-partial-line # (7)!
    font_family: Source Sans 3
    font_size: 1.4em
    bold: true
    small_caps: false
    line_thickness: 0.5pt
    vertical_space_above: 0.5cm
    vertical_space_below: 0.3cm
  entries:
    date_and_location_width: 4.15cm
    left_and_right_margin: 0.2cm
    horizontal_space_between_columns: 0.1cm
    vertical_space_between_entries: 1.2em
    allow_page_break_in_sections: true
    allow_page_break_in_entries: true
    short_second_row: false
    show_time_spans_in: []
  highlights:
    bullet: • # (8)!
    top_margin: 0.25cm
    left_margin: 0.4cm
    vertical_space_between_highlights: 0.25cm
    horizontal_space_between_bullet_and_highlight: 0.5em
    summary_left_margin: 0cm
  entry_types:
    one_line_entry:
      template: '**LABEL:** DETAILS'
    education_entry:
      main_column_first_row_template: '**INSTITUTION**, AREA'
      degree_column_template: '**DEGREE**'
      degree_column_width: 1cm
      main_column_second_row_template: |-
        SUMMARY
        HIGHLIGHTS
      date_and_location_column_template: |-
        LOCATION
        DATE
    normal_entry:
      main_column_first_row_template: '**NAME**'
      main_column_second_row_template: |-
        SUMMARY
        HIGHLIGHTS
      date_and_location_column_template: |-
        LOCATION
        DATE
    experience_entry:
      main_column_first_row_template: '**COMPANY**, POSITION'
      main_column_second_row_template: |-
        SUMMARY
        HIGHLIGHTS
      date_and_location_column_template: |-
        LOCATION
        DATE
    publication_entry:
      main_column_first_row_template: '**TITLE**'
      main_column_second_row_template: |-
        AUTHORS
        URL (JOURNAL)
      main_column_second_row_without_journal_template: |-
        AUTHORS
        URL
      main_column_second_row_without_url_template: |-
        AUTHORS
        JOURNAL
      date_and_location_column_template: DATE
```

1. The `design.theme` field only changes the default values of all the other fields in the `design` field. Therefore, if you don't change any of the other fields, the output will be the same for all the themes. You can remove all the other fields and just keep the `design.theme` field to use the default values of that theme.

    The available themes are: {{available_themes}}.

2. The available page sizes are: {{available_page_sizes}}.
3. The available font families are: {{available_font_families}}.
4. The available text alignments are: {{available_text_alignments}}.
5. The available date and location column alignments are: {{available_header_alignments}}.
6. The available header alignments are: {{available_header_alignments}}.
7. The available section title types are: {{available_section_title_types}}.
8. The available bullet types are: {{available_bullets}}.

## "`locale`" field

This field is what makes RenderCV a multilingual tool. RenderCV uses some English strings to render PDFs. For example, it takes the dates in ISO format (`2020-01-01`) and converts them into human-friendly strings (`"Jan 2020"`). However, you can override these strings for your own language or needs with the `locale` field.

Here is an example:

```yaml
locale:
  language: en
  phone_number_format: national # (1)!
  page_numbering_template: NAME - Page PAGE_NUMBER of TOTAL_PAGES # (4)!
  last_updated_date_template: Last updated in TODAY # (3)!
  date_template: MONTH_ABBREVIATION YEAR # (2)!
  month: month
  months: months
  year: year
  years: years
  present: present
  to: –
  abbreviations_for_months:
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
  full_names_of_months:
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

1. The available phone number formats are: `national`, `international`, and `E164`.
2. The `MONTH_ABBREVIATION` and `YEAR` are placeholders. The available placeholders are: `FULL_MONTH_NAME`, `MONTH_ABBREVIATION`, `MONTH`, `MONTH_IN_TWO_DIGITS`, `YEAR`, and `YEAR_IN_TWO_DIGITS`.
3. The available placeholders are: `TODAY`, which prints the today's date with `locale.date_template`.
4. The available placeholders are: `NAME`, `PAGE_NUMBER`, `TOTAL_PAGES`, and `TODAY`.

## "`rendercv_settings`" field

The `rendercv_settings` field contains RenderCV settings. 

```yaml
rendercv_settings:
  date: "2025-01-06" # (1)!
  bold_keywords:
    - Python # (2)!
  render_command:
    output_folder_name: rendercv_output
    pdf_path: NAME_IN_SNAKE_CASE_CV.pdf # (3)!
    typst_path: NAME_IN_LOWER_SNAKE_CASE_cv.typ
    html_path: NAME_IN_KEBAB_CASE_CV.html
    markdown_path: NAME.md
    dont_generate_html: false 
    dont_generate_markdown: false 
    dont_generate_png: false 
```

1. This field is used for time span calculations and last updated date text.
2. The words in the list will be bolded in the output automatically.
3. `NAME_IN_SNAKE_CASE` is a placeholder. The available placeholders are: `NAME_IN_SNAKE_CASE`, `NAME_IN_LOWER_SNAKE_CASE`, `NAME_IN_UPPER_SNAKE_CASE`, `NAME_IN_KEBAB_CASE`, `NAME_IN_LOWER_KEBAB_CASE`, `NAME_IN_UPPER_KEBAB_CASE`, `NAME`, `FULL_MONTH_NAME`, `MONTH_ABBREVIATION`, `MONTH`, `MONTH_IN_TWO_DIGITS`, `YEAR`, and `YEAR_IN_TWO_DIGITS`.
