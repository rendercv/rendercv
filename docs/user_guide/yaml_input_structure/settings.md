# `settings` Field

The `settings` field configures RenderCV's behavior, including output paths, file generation, and text formatting.

```yaml
settings:
  current_date: '2025-12-03' # (5)!
  render_command:
    design: path/to/design.yaml # (1)!
    locale: path/to/locale.yaml # (2)!
    typst_path: rendercv_output/NAME_IN_SNAKE_CASE_CV.typ # (3)!
    pdf_path: rendercv_output/NAME_IN_SNAKE_CASE_CV.pdf
    markdown_path: rendercv_output/NAME_IN_SNAKE_CASE_CV.md
    html_path: rendercv_output/NAME_IN_SNAKE_CASE_CV.html
    png_path: rendercv_output/NAME_IN_SNAKE_CASE_CV.png
    dont_generate_markdown: false
    dont_generate_html: false
    dont_generate_typst: false
    dont_generate_pdf: false
    dont_generate_png: false
  bold_keywords: # (4)!
    - AWS
    - Python
```


1. You can optionally split your YAML into multiple files. This file contains the `design` field.
2. You can optionally split your YAML into multiple files. This file contains the `locale` field.
3. Available placeholders are: `NAME`, `NAME_IN_SNAKE_CASE`, `NAME_IN_LOWER_SNAKE_CASE`, `NAME_IN_UPPER_SNAKE_CASE`, `NAME_IN_KEBAB_CASE`, `NAME_IN_LOWER_KEBAB_CASE`, `NAME_IN_UPPER_KEBAB_CASE`, `MONTH_NAME`, `MONTH_ABBREVIATION`, `MONTH`, `MONTH_IN_TWO_DIGITS`, `YEAR`, `YEAR_IN_TWO_DIGITS`.
4. These keywords will be bolded wherever they appear in your CV text (highlights, summaries, etc.).
5. Date used for file naming (when using date placeholders), the "last updated" text in the top note, and time span calculations for ongoing events (entries with `end_date: present`)
