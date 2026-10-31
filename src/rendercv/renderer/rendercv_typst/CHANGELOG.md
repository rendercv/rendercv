# Changelog

All notable changes to the RenderCV **Typst package** (`@preview/rendercv`) will be documented in this file.

For the changelog of the RenderCV CLI and Python package, see [the RenderCV changelog](https://docs.rendercv.com/changelog/).

## 0.4.0 - 2026-10-22

### Added

- Subsections: level-3 headings (`=== Title`) are subsection titles, styled with `colors-subsection-titles`, `typography-font-family-subsection-titles`, `typography-font-size-subsection-titles`, `typography-small-caps-subsection-titles`, and `typography-bold-subsection-titles`, and spaced with `subsection-titles-space-above` and `subsection-titles-space-below`. The space above a subsection title separates it from the content above it, so the first subsection of a section is right below the section title.
- `description` and `keywords` parameters for the metadata of the PDF ([#726](https://github.com/rendercv/rendercv/issues/726)).
- `name: none` for a document without a name.
- `page-height`, such as `auto` for a page as tall as its content.
- Chinese, Japanese, and Korean characters fall back to the Noto Sans fonts of these languages, which most fonts don't cover, preferring the font of the document's language.

### Changed

- An entry's header (its first row) never ends a page without its content.
- The `●` bullet is an enlarged `•` centered on the x-height, as the `●` glyph is too large in most fonts.
- `fontawesome` 0.6.2.

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

