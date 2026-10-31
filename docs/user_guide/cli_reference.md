---
toc_depth: 1
---

# CLI Reference

RenderCV provides a command-line interface with three main commands:

- **`rendercv new`** - Generate a sample CV to get started
- **`rendercv render`** - Generate PDF, Markdown, HTML, PNG, and SVG from your YAML input
- **`rendercv create-theme`** - Create a custom theme with editable templates

!!! tip "New to command line?"
    Commands are typed in your terminal/command prompt. Options starting with `--` modify behavior:

    ```bash
    rendercv new "John Doe" --theme moderncv
    ```

    **You can combine multiple options** in a single command:

    ```bash
    rendercv render CV.yaml --watch --dont-generate-html --dont-generate-png
    ```

    This renders your CV with auto-reload enabled, skipping HTML and PNG generation.

## `rendercv`

Check your installed version:

```bash
rendercv --version
```

Get help anytime:

```bash
rendercv --help
```

## `rendercv new`

Generate a sample CV file to start editing. Use `--quiet` or `-q` to suppress messages.

**Basic usage:**

```bash
rendercv new "John Doe"
```

This creates `John_Doe_CV.yaml` in your current folder.

**Choose a different theme:**

```bash
rendercv new "John Doe" --theme moderncv
```

Available themes: << available_themes >>

**Use a different language:**

```bash
rendercv new "John Doe" --locale french
```

Available locales: << available_locales >>

**For advanced users - generate editable templates:**

```bash
rendercv new "John Doe" --create-typst-templates
```

This creates template files you can customize for complete design control. See [Override Default Templates](how_to/override_default_templates.md) for details.

## `rendercv render`

Generate your CV outputs (PDF, Markdown, HTML, PNG, SVG) from a YAML file.

**Basic usage:**

```bash
rendercv render John_Doe_CV.yaml
```

This creates a `rendercv_output` folder beside the input YAML with all formats.

### Common Scenarios

**Auto-reload while editing:**

```bash
rendercv render John_Doe_CV.yaml --watch
```

The CV regenerates when the main YAML or any selected design, locale, settings, or overlay file changes. Their contents and references are reloaded each time. Watch mode keeps running after input errors, so you can fix them and save again. An error while compiling, for example in a custom template, stops it.

**Only generate PDF:**

```bash
rendercv render John_Doe_CV.yaml --dont-generate-typst --dont-generate-markdown --dont-generate-png --dont-generate-svg
```

Or use the short form:

```bash
rendercv render John_Doe_CV.yaml -notyp -nomd -nopng -nosvg
```

**Merge a private file over the CV:**

```bash
rendercv render John_Doe_CV.yaml --overlay private.yaml
```

An overlay has the structure of a CV file, with only the fields it changes, like your real email and phone in a CV published with placeholders. See [Combine YAML Files](how_to/combine_yaml_files.md).

**Custom output location:**

```bash
rendercv render John_Doe_CV.yaml --pdf-path ~/Desktop/MyCV.pdf
```

All paths passed on the command line are relative to the **current working directory**, including output paths and `--design`, `--locale-catalog`, `--settings`, and `--overlay`. Absolute paths also work. Paths written inside YAML files, including a settings overlay, remain relative to the **main input YAML**.

Output paths can start with `OUTPUT_FOLDER`, which expands to the configured output folder, and their file names support name placeholders such as `NAME_IN_SNAKE_CASE` and date placeholders such as `YEAR` and `MONTH_IN_TWO_DIGITS`:

```bash
rendercv render inputs/CV.yaml --output-folder build --pdf-path OUTPUT_FOLDER/NAME_IN_SNAKE_CASE_YEAR.pdf
```

For design and locale file references, the precedence is **CLI flag > settings overlay > main YAML**, independently for each field. A missing reference in the settings overlay falls back to the main YAML; an explicit `null` clears it. An overlay replaces its corresponding top-level section rather than merging its individual fields.

`--dont-generate-typst` suppresses only the saved `.typ` file; PDF, PNG, and SVG still compile from the Typst source in memory. The photo is copied next to the Typst file, so a saved Typst file compiles on its own. `--dont-generate-markdown` also disables HTML generation.

### All Options

| Option                     | Short     | What it does                     |
| -------------------------- | --------- | -------------------------------- |
| `--watch`                  | `-w`      | Re-render when file changes      |
| `--quiet`                  | `-q`      | Hide all messages                |
| `--design FILE`            | `-d`      | Load design from separate file   |
| `--locale-catalog FILE`    | `-lc`     | Load locale from separate file   |
| `--settings FILE`          | `-s`      | Load settings from separate file |
| `--overlay FILE`           |           | Merge a file over the input      |
| `--output-folder PATH`     | `-o`      | Base folder for generated files  |
| `--pdf-path PATH`          | `-pdf`    | Custom PDF location              |
| `--typst-path PATH`        | `-typ`    | Custom Typst location            |
| `--markdown-path PATH`     | `-md`     | Custom Markdown location         |
| `--html-path PATH`         | `-html`   | Custom HTML location             |
| `--png-path PATH`          | `-png`    | Custom PNG location              |
| `--svg-path PATH`          | `-svg`    | Custom SVG location              |
| `--dont-generate-pdf`      | `-nopdf`  | Skip PDF generation              |
| `--dont-generate-typst`    | `-notyp`  | Skip saving Typst source         |
| `--dont-generate-markdown` | `-nomd`   | Skip Markdown generation         |
| `--dont-generate-html`     | `-nohtml` | Skip HTML generation             |
| `--dont-generate-png`      | `-nopng`  | Skip PNG generation              |
| `--dont-generate-svg`      | `-nosvg`  | Skip SVG generation              |

**Override any YAML value:**

Use dot notation to change specific fields. This overrides values in the YAML without editing the file.

```bash
rendercv render CV.yaml --cv.phone "+1-555-555-5555"
rendercv render CV.yaml --cv.sections.education.0.institution "MIT"
rendercv render CV.yaml --design.theme "moderncv"
```

List items are numbered from 0, and the number after the last item adds an item. If `skills` has two entries, this adds a third:

```bash
rendercv render CV.yaml --cv.sections.skills.2.label "Languages" --cv.sections.skills.2.details "English, Turkish"
```

## `rendercv create-theme`

Create your own theme with full control over the design. Use `--quiet` or `-q` to suppress messages. Theme names must start with a lowercase letter and contain only lowercase letters and digits. Invalid names are rejected before any files are created.

**Basic usage:**

```bash
rendercv create-theme "mytheme"
```

This creates a `mytheme/` folder with template files you can edit. See [Override Default Templates](how_to/override_default_templates.md) for details.
