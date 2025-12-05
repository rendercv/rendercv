---
toc_depth: 1
---

# CLI Reference

## `rendercv`

Show version:

```bash
rendercv --version  
```

Show help:

```bash
rendercv --help        
```

## `rendercv new`

Create a new CV YAML input file

```bash
rendercv new "John Doe"
```

### Options

| Option                        | Description                                                      |
| ----------------------------- | ---------------------------------------------------------------- |
| `--theme THEME`               | Use a built-in theme: << available_themes >>. Default: `classic` |
| `--locale LOCALE`             | Use a locale: << available_locales >>. Default: `english`        |
| `--create-typst-templates`    | Generate Typst template files for advanced customization         |
| `--create-markdown-templates` | Generate Markdown template files for advanced customization      |

## `rendercv render`

Render a CV from a YAML file.

```bash
rendercv render John_Doe_CV.yaml
```

### Options

All output paths are relative to the input file.

| Option                     | Short     | Description                                              |
| -------------------------- | --------- | -------------------------------------------------------- |
| `--watch`                  | `-w`      | Re-render automatically when the YAML file changes       |
| `--quiet`                  | `-q`      | Suppress all output messages                             |
| `--design FILE`            | `-d`      | Load `design` field from a separate YAML file            |
| `--locale-catalog FILE`    | `-lc`     | Load `locale` field from a separate YAML file            |
| `--settings FILE`          | `-s`      | Load `rendercv_settings` field from a separate YAML file |
| `--pdf-path PATH`          | `-pdf`    | Custom path for PDF output                               |
| `--typst-path PATH`        | `-typ`    | Custom path for Typst source output                      |
| `--markdown-path PATH`     | `-md`     | Custom path for Markdown output                          |
| `--html-path PATH`         | `-html`   | Custom path for HTML output                              |
| `--png-path PATH`          | `-png`    | Custom path for PNG output                               |
| `--dont-generate-pdf`      | `-nopdf`  | Skip PDF generation                                      |
| `--dont-generate-typst`    | `-notyp`  | Skip Typst generation (implies `-nopdf`, `-nopng`)       |
| `--dont-generate-markdown` | `-nomd`   | Skip Markdown generation (implies `-nohtml`)             |
| `--dont-generate-html`     | `-nohtml` | Skip HTML generation                                     |
| `--dont-generate-png`      | `-nopng`  | Skip PNG generation                                      |


### Overriding YAML values

Override any field in the YAML file from the command line:

```bash
rendercv render John_Doe_CV.yaml --cv.phone "+1-555-555-5555"
```

```bash
rendercv render John_Doe_CV.yaml --cv.sections.education.0.institution "MIT"
```

Useful for keeping sensitive information (phone, address) out of version control.

## `rendercv create-theme`

Create a custom theme with Typst templates you can modify.

```bash
rendercv create-theme "mytheme"
```

Creates a `mytheme/` directory in the current folder with all template files.