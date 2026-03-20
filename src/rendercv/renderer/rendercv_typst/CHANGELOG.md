# Changelog

All notable changes to the RenderCV **Typst package** (`@preview/rendercv`) will be documented in this file.

For the changelog of the RenderCV CLI and Python package, see [the RenderCV changelog](https://docs.rendercv.com/changelog/).

## 0.3.0 - 2026-03-20

### Added

- Four new centered section title styles: `centered_without_line`, `centered_with_partial_line`, `centered_with_centered_partial_line`, and `centered_with_full_line`.
- Harvard theme example (`examples/harvard.typ`).

## 0.2.0 - 2026-02-16

### Added

- RTL (right-to-left) language support via `text-direction` parameter (accepts native Typst `ltr`/`rtl` values). All layout elements (grids, insets, section titles, top note) mirror correctly for RTL languages.
- `title` parameter to customize the PDF document title.
- `entries-degree-width` parameter to control the width of the degree column in education entries.
- Persian RTL example (`examples/rtl.typ`).

### Fixed

- Correct spacing when a headline is present. Previously, `header-space-below-headline` was ignored when a headline existed.
- Empty second line detection in education entries.
- External link icon rendering issues.

## 0.1.0 - 2025-12-05

- Initial release of RenderCV Typst package.

