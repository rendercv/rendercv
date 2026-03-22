# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is RenderCV?

RenderCV is a resume/CV builder for academics and engineers. Users write CVs in YAML, and RenderCV produces PDFs with professional typography. It supports multiple themes (classic, moderncv, sb2nov, engineeringresumes, engineeringclassic) and custom themes. Deployed at rendercv.com as a web app.

## Core Pipeline

```
YAML → (ruamel.yaml) → Python dict → (pydantic) → RenderCVModel → (jinja2) → Typst file → (typst) → PDF
```

1. **Parse**: `ruamel.yaml` reads YAML into Python dicts (`schema/yaml_reader.py`)
2. **Validate**: `pydantic` validates into `RenderCVModel` (`schema/models/rendercv_model.py`)
3. **Template**: `jinja2` renders Typst templates with model data (`renderer/templater/templater.py`)
4. **Compile**: `typst` Python bindings compile `.typ` to PDF (`renderer/pdf_png.py`)

Markdown in YAML fields is converted to Typst syntax via the `markdown` library (`renderer/templater/markdown_parser.py`).

## Commands

```bash
just sync              # Install dependencies
just test              # Run tests (parallel via pytest-xdist)
just check             # Lint (ruff) + type-check (ty) + pre-commit hooks
just format            # Format (black + ruff)
just update-testdata   # Regenerate reference files for tests
just test-coverage     # Run tests with coverage report
just update-schema     # Regenerate JSON schema
just update-examples   # Update example output files
```

Run a single test:
```bash
uv run --frozen --all-extras pytest tests/renderer/templater/test_date.py -x
```

Run tests matching a keyword:
```bash
uv run --frozen --all-extras pytest -k "test_markdown_to_typst" -x
```

## Source Layout

```
src/rendercv/
  cli/                          # Typer CLI (render, new, create-theme commands)
    render_command/run_rendercv.py  # Main render orchestration
  schema/                       # Data models and validation
    models/
      cv/                       # CV content models (entries, sections)
      design/                   # Theme models (classic, moderncv, etc.)
      locale/                   # Localization model
      settings/                 # Rendering settings
      rendercv_model.py         # Top-level RenderCVModel
    rendercv_model_builder.py   # Builds RenderCVModel from YAML with overrides
  renderer/                     # Output generation
    templater/
      templates/typst/          # Jinja2 templates for Typst output (per theme)
      templater.py              # Jinja2 rendering logic
      markdown_parser.py        # Markdown → Typst conversion
    typst.py                    # Typst source file generation
    pdf_png.py                  # PDF/PNG compilation
    html.py                     # HTML output
    markdown.py                 # Markdown output
```

## Testing

Tests mirror the source structure: `src/rendercv/renderer/templater/date.py` → `tests/renderer/templater/test_date.py`.

**Reference file testing**: Renderer tests compare generated output against reference files in test data directories. Use `just update-testdata` to regenerate references when output intentionally changes.

**Key fixtures** (in `tests/renderer/conftest.py`):
- `minimal_rendercv_model` / `full_rendercv_model` — pre-built models for testing
- `compare_file_with_reference` — compares generated output against reference files

## Code Conventions

- **No private API syntax**: Never use underscore-prefixed names (`_Foo`, `_bar`). All names are public.
- **Strict typing**: Every function, variable, and class attribute must have type annotations.
- **Python 3.12+ syntax**: Use `type` statements for aliases, `X | Y` unions, `X | None` for optionals.
- **Docstrings**: Google-style with Why/Args/Returns/Raises sections.
- **`just check` must show zero errors** before committing.
- Use `uv`, never `pip` or `python` directly.
