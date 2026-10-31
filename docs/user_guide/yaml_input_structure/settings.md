# `settings` Field

The `settings` field configures RenderCV's behavior, including output paths, file generation, and text formatting.

```yaml
settings:
  current_date: '2025-12-03' # (5)!
  render_command:
    output_folder: rendercv_output # (8)!
    design: path/to/design.yaml # (1)!
    locale: path/to/locale.yaml # (2)!
    overlays: # (6)!
      - path/to/publications.yaml
    typst_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.typ # (3)!
    pdf_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.pdf
    markdown_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.md
    html_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.html
    png_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.png
    svg_path: OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_CV.svg
    dont_generate_markdown: false
    dont_generate_html: false
    dont_generate_typst: false
    dont_generate_pdf: false
    dont_generate_png: false
    dont_generate_svg: false
  bold_keywords: # (4)!
    - AWS
    - Python
  sort_entries: none # (7)!
  pdf_title: NAME - CV # (9)!
  pdf_profile: accessible # (10)!
```


1. You can optionally split your YAML into multiple files. This file contains the `design` field.
2. You can optionally split your YAML into multiple files. This file contains the `locale` field.
3. Available placeholders are: `NAME`, `NAME_IN_SNAKE_CASE`, `NAME_IN_LOWER_SNAKE_CASE`, `NAME_IN_UPPER_SNAKE_CASE`, `NAME_IN_KEBAB_CASE`, `NAME_IN_LOWER_KEBAB_CASE`, `NAME_IN_UPPER_KEBAB_CASE`, `CURRENT_DATE`, `MONTH_NAME`, `MONTH_ABBREVIATION`, `MONTH`, `MONTH_IN_TWO_DIGITS`, `DAY`, `DAY_IN_TWO_DIGITS`, `DAY_ORDINAL`, `YEAR`, `YEAR_IN_TWO_DIGITS`.
4. These keywords are bolded wherever they appear in your CV text (highlights, summaries, etc.), as whole words and exactly as written, so `C++` and `Node.js` work too. Text that is already bold, code, and links are left alone.
5. Date used for file naming (when using date placeholders), the "last updated" text in the top note, and time span calculations for ongoing events (entries with `end_date: present`)
6. Files merged over the input file, in order, after the design and locale files and before the ones given with `--overlay`. See [Combine YAML Files](../how_to/combine_yaml_files.md).
7. The order of the entries of every section and subsection: `none` (as written), `reverse-chronological` (the most recent first), or `chronological` (the oldest first). Entries are ordered by their end dates, then their start dates, and the ones without dates come last in their written order.
8. The folder that `OUTPUT_FOLDER` stands for in the output paths.
9. The title that PDF readers and browser tabs show. It takes the same placeholders as the output paths.
10. `accessible` makes the PDF conform to PDF/UA-1, the accessibility standard, which requires `cv.name` and alternative text for images in Typst code. `standard` makes an ordinary PDF.

## Paths

Paths in YAML files, including the `design`, `locale`, and `overlays` of a file given with `--settings`, are relative to the main CV file. Paths given on the command line, like `--pdf-path` or `--cv.photo`, are relative to the folder you run `rendercv` in.

`output_folder` only moves the paths that use `OUTPUT_FOLDER`. Any other path has its own destination:

```yaml
settings:
  render_command:
    output_folder: build
    pdf_path: OUTPUT_FOLDER/resume.pdf  # build/resume.pdf
    typst_path: sources/resume.typ     # sources/resume.typ
```

In file names, characters that can't be in a file name, like `/`, are replaced with `_`. PNG and SVG files are one per page: `NAME_CV_1.png`, `NAME_CV_2.png`, and so on. Before writing anything, RenderCV checks that no output would overwrite an input file or another output.

`dont_generate_typst: true` only skips saving the Typst file: the PDF, PNG, and SVG files are still made. `dont_generate_markdown: true` also turns off HTML.
