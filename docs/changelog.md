---
toc_depth: 1
hide:
  - navigation
---

# Changelog

All notable changes to this project will be documented in this file.

[Click here to see the unreleased changes.](https://github.com/rendercv/rendercv/compare/v2.9...HEAD)

<!--
### Added
### Changed
### Fixed
### Removed
-->

## [2.9] - Unreleased

> **Full Changelog**: [v2.8...v2.9]

### Added

- Subsections: `SubsectionEntry` has a `title` and its own `entries`. Each list contains one entry type, which can itself be `SubsectionEntry` for deeper nesting ([#254](https://github.com/rendercv/rendercv/issues/254), [#545](https://github.com/rendercv/rendercv/issues/545), [#694](https://github.com/rendercv/rendercv/issues/694)). Their titles are styled with the new `subsection_titles` options of `design.typography` and `design.colors`, and spaced with `design.subsection_titles`.
- Overlays: `--overlay FILE` and `settings.render_command.overlays` merge YAML files over the input file, like private contact details over a CV published with placeholders ([#740](https://github.com/rendercv/rendercv/issues/740), [#747](https://github.com/rendercv/rendercv/issues/747)), or parts of a CV kept in their own files ([#477](https://github.com/rendercv/rendercv/issues/477)). See [Combine YAML Files](user_guide/how_to/combine_yaml_files.md).
- SVG files, one per page, are generated like PNG files, with `svg_path` and `dont_generate_svg` ([#731](https://github.com/rendercv/rendercv/issues/731)).
- `settings.sort_entries` is back: entries can be ordered by date, the most recent first or the oldest first ([#794](https://github.com/rendercv/rendercv/issues/794)).
- PDFs conform to PDF/UA-1, the accessibility standard ([#769](https://github.com/rendercv/rendercv/issues/769)). It requires `cv.name` and alternative text for images in Typst code; `settings.pdf_profile: standard` makes an ordinary PDF instead.
- A `DAY_ORDINAL` date placeholder, like `6th`, written by each locale in `locale.day_ordinals` ([#732](https://github.com/rendercv/rendercv/issues/732)).
- CLI overrides can add a list item at the index after the last one ([#774](https://github.com/rendercv/rendercv/issues/774)).
- Built-in locales for Swedish ([#713](https://github.com/rendercv/rendercv/issues/713), [#802](https://github.com/rendercv/rendercv/issues/802)), Polish ([#714](https://github.com/rendercv/rendercv/issues/714)), and Catalan ([#800](https://github.com/rendercv/rendercv/issues/800)).
- HuggingFace ([#746](https://github.com/rendercv/rendercv/issues/746)), Itch.io, and Devpost ([#756](https://github.com/rendercv/rendercv/issues/756)) social networks, WhatsApp usernames ([#777](https://github.com/rendercv/rendercv/issues/777)), and longer IMDb IDs ([#806](https://github.com/rendercv/rendercv/issues/806)).
- Custom connections can be plain text, without a URL ([#803](https://github.com/rendercv/rendercv/issues/803)).
- Chinese, Japanese, and Korean are rendered with the bundled Noto Sans fonts, in the variant of the CV's language ([#655](https://github.com/rendercv/rendercv/issues/655)).
- Python 3.15 is supported.

### Changed

- RenderCV no longer checks PyPI for a newer version when it starts.
- User content is parsed once into a tree and emitted once, as Typst or Markdown, instead of being rewritten as text several times. Escaping now follows the grammars exactly: `"` makes smart quotes, and `%`, `>`, and `/` are text.
- Bold and italic follow CommonMark: after punctuation, a closing `**` needs a space, punctuation, or the line's end after it, so `**C++**17` stays literal while `**C++** 17` is bold. Raw HTML and Markdown images in content are shown as text, in the HTML output too ([#594](https://github.com/rendercv/rendercv/pull/594)).
- In entry templates, an uppercase word of two or more letters or digits, like `GPA` or `Q3`, is a placeholder for the field of that name, and a single capital letter is text.
- A template placeholder without a value is removed together with the formatting, brackets, and connecting words that only existed for it.
- Markdown and HTML headings nest like the PDF's: sections are level 2 (they were level 1, like the name), subsections level 3, and entries one level below their section.
- The Markdown and HTML header lists the same contact details as the PDF, in the same format: phone numbers follow `design.header.connections.phone_number_format`, which is national by default.
- The time spans of month ranges count whole months: February to March is 2 months.
- An entry's header never ends a page without its content ([#190](https://github.com/rendercv/rendercv/issues/190)).
- `dont_generate_typst` no longer disables PDF and PNG generation, which compile from memory ([#730](https://github.com/rendercv/rendercv/issues/730), [#760](https://github.com/rendercv/rendercv/issues/760)).
- Paths given on the command line are relative to the current working directory ([#752](https://github.com/rendercv/rendercv/issues/752)), and the design, locale, and settings files are chosen with the precedence CLI > settings file > main file ([#776](https://github.com/rendercv/rendercv/issues/776)). Every render, and every re-render of watch mode, reads them again.
- The photo must be an image: PNG, JPEG, GIF, WebP, SVG, or PDF ([#598](https://github.com/rendercv/rendercv/issues/598)). A photo given as a URL is downloaded during validation, on every render.
- Templates written for RenderCV 1 are rejected with an explanation instead of printing their syntax, and syntax errors in template overrides are reported during validation ([#721](https://github.com/rendercv/rendercv/issues/721)).
- Custom theme names must start with a letter, everywhere ([#771](https://github.com/rendercv/rendercv/issues/771)), and the design options of a custom theme without an `__init__.py` are validated.
- A custom theme's `__init__.py` must define every design option of the classic theme. One created by an older version of RenderCV is rejected with the list of options it lacks; recreate it with `rendercv create-theme`.
- CLI overrides no longer accept negative list indices, which edited the last items.
- Validation errors are classified by their type instead of their text, and a mistyped language lists the available ones.
- The `rendercv-fonts` package is developed in this repository, as a uv workspace package, and its version 0.6.0 has Font Awesome 7.3.1.
- The Typst package `@preview/rendercv` is version 0.4.0. It draws the `●` highlight bullet of `engineeringresumes`, with tighter line spacing.
- The Docker image uses Python 3.15 on Debian trixie and the user ID 1000 ([#780](https://github.com/rendercv/rendercv/issues/780)).
- The AI agent skill lists every theme, keeps every contact detail it's given, and takes its references from RenderCV itself. It's published to [rendercv-skill](https://github.com/rendercv/rendercv-skill) with each release ([#784](https://github.com/rendercv/rendercv/issues/784), [#785](https://github.com/rendercv/rendercv/issues/785), [#787](https://github.com/rendercv/rendercv/issues/787), [#788](https://github.com/rendercv/rendercv/issues/788), [#791](https://github.com/rendercv/rendercv/issues/791), [#792](https://github.com/rendercv/rendercv/issues/792), [#793](https://github.com/rendercv/rendercv/issues/793), [#767](https://github.com/rendercv/rendercv/issues/767)).
- The documentation is built with Zensical ([#728](https://github.com/rendercv/rendercv/issues/728)) and hosted on Cloudflare, with a preview of each pull request. The pages of the API reference are now under `api_reference/rendercv/`.
- All dependencies have been upgraded, including Typst 0.15.

### Fixed

- Enabled output files are checked together before rendering: they cannot overwrite input files, each other, or another format’s numbered page files. The photo copied next to the Typst file is named after it, like `John_Doe_CV_photo.jpg`, so it can't overwrite an unrelated file.
- Accented letters in small capitals are small capitals too: the `ember` and `opal` themes use Source Sans 3, which has them, for their small-capital headings ([#807](https://github.com/rendercv/rendercv/issues/807)).
- Nested highlights are nested again ([#712](https://github.com/rendercv/rendercv/issues/712), [#754](https://github.com/rendercv/rendercv/issues/754), [#786](https://github.com/rendercv/rendercv/issues/786)).
- Formatting around a date that spans several lines is closed and reopened on each line ([#705](https://github.com/rendercv/rendercv/issues/705)).
- A year written as text, like `date: '2021'`, is shown as `2021` instead of `Jan 2021`, and its time span counts whole years.
- `bold_keywords` bolds whole words only, whatever their first and last characters ([#706](https://github.com/rendercv/rendercv/issues/706)), and never inside bold text, code, or links ([#736](https://github.com/rendercv/rendercv/issues/736)).
- The `sb2nov` theme uses the locale's degree phrase ([#755](https://github.com/rendercv/rendercv/issues/755), [#759](https://github.com/rendercv/rendercv/issues/759)), the `harvard` theme no longer shows the degree twice ([#804](https://github.com/rendercv/rendercv/issues/804)), and `ember` and `ink` no longer print a stray `*`.
- The HTML page has a title, `settings.pdf_title` ([#805](https://github.com/rendercv/rendercv/issues/805)).
- Phone numbers are laid out left to right in right-to-left CVs ([#781](https://github.com/rendercv/rendercv/issues/781)).
- A section named `interests`, `internships`, or anything containing `int`, `str`, or `list` no longer crashes the error report ([#758](https://github.com/rendercv/rendercv/issues/758)).
- `--settings` with `--output-folder` no longer crashes ([#551](https://github.com/rendercv/rendercv/issues/551)).
- Exceptions keep their messages ([#757](https://github.com/rendercv/rendercv/issues/757)), and `rendercv new` and `rendercv create-theme` honor `--quiet` ([#751](https://github.com/rendercv/rendercv/issues/751)).
- A saved Typst file compiles on its own, with the photo next to it ([#778](https://github.com/rendercv/rendercv/issues/778)).
- Phone numbers are serialized the same as a single value and in a list ([#789](https://github.com/rendercv/rendercv/issues/789), [#790](https://github.com/rendercv/rendercv/issues/790)), and lengths can start with a decimal point, like `.5cm` ([#798](https://github.com/rendercv/rendercv/issues/798), [#799](https://github.com/rendercv/rendercv/issues/799)).
- The JSON Schema accepts custom themes ([#772](https://github.com/rendercv/rendercv/issues/772)) and is the same on every operating system.
- Font Awesome icons render offline, in the Docker image too: the Font Awesome Typst package ships with RenderCV instead of being downloaded on the first render ([#775](https://github.com/rendercv/rendercv/issues/775)).
- A `/` or another character that can't be in a file name, in the CV owner's name, no longer makes directories in the output folder: it's replaced by `_` in file names.
- A partial `typography.font_family` mapping keeps the theme's own fonts for the elements it leaves out; they became Source Sans 3.
- A locale's `month_names`, `month_abbreviations`, and `day_ordinals` must have 12, 12, and 31 items. A shorter list is rejected during validation instead of crashing the render.

## [2.8] - March 21, 2026

> **Full Changelog**: [v2.7...v2.8]

### Added

- Four new themes have been added: `harvard`, `ink`, `opal`, and `ember`.
- Four new centered section title types have been added: `centered_without_line`, `centered_with_partial_line`, `centered_with_centered_partial_line`, and `centered_with_full_line`.
- Built-in locale defaults for 2 additional languages have been added: Vietnamese and Hungarian.
- Multi-platform Docker builds are now available for both `linux/amd64` and `linux/arm64` ([#697](https://github.com/rendercv/rendercv/issues/697)).

### Changed

- The `rendercv-typst` Typst package is now bundled inside the Python package. RenderCV no longer requires an internet connection to compile PDFs, as it no longer needs to download the package from Typst Universe at runtime. The package will continue to be published on Typst Universe for standalone Typst users.

### Fixed

- Custom fonts folder not being found when using a relative input path has been fixed ([#692](https://github.com/rendercv/rendercv/issues/692)).
- CLI overrides like `--design.theme` no longer crash when the target section is not present in the main YAML file ([#595](https://github.com/rendercv/rendercv/issues/595)).
- The `SUMMARY` placeholder can now be used inline in templates ([#653](https://github.com/rendercv/rendercv/issues/653)).
- Design and locale overlay files specified in YAML `settings.render_command` are now loaded correctly ([#690](https://github.com/rendercv/rendercv/issues/690)).
- Copied template files are now made writable for immutable distributions like NixOS ([#673](https://github.com/rendercv/rendercv/issues/673)).
- Markdown lines are now processed independently to prevent cross-line emphasis interference ([#685](https://github.com/rendercv/rendercv/issues/685)).
- Connector words in phrases no longer appear when their associated placeholder is empty (e.g., "BS in Mechanical Engineering" now correctly renders as "Mechanical Engineering" when the degree is omitted, instead of "in Mechanical Engineering").
- `EducationEntry` location placement in markdown output has been fixed ([#691](https://github.com/rendercv/rendercv/issues/691)).

## [2.7] - March 6, 2026

> **Full Changelog**: [v2.6...v2.7]

### Added

- A new `settings.pdf_title` field has been added to customize the title of produced PDF documents ([#624](https://github.com/rendercv/rendercv/issues/624)).
- A new `locale.phrases` field has been added for customizable phrases in the CV, allowing translations like "DEGREE in AREA" to be adapted per language ([#618](https://github.com/rendercv/rendercv/issues/618), [#650](https://github.com/rendercv/rendercv/issues/650), [#660](https://github.com/rendercv/rendercv/issues/660)).
- A new `design.entries.degree_width` field has been added ([#671](https://github.com/rendercv/rendercv/issues/671)).
- `--output-folder` option has been added to the `rendercv render` command to specify the output directory ([#578](https://github.com/rendercv/rendercv/issues/578)).
- Watch mode now monitors included config files and re-renders when they change ([#579](https://github.com/rendercv/rendercv/issues/579)).
- `DAY` and `DAY_IN_TWO_DIGITS` placeholders have been added to date formatting ([#548](https://github.com/rendercv/rendercv/issues/548)).
- Reddit has been added as a social network type ([#658](https://github.com/rendercv/rendercv/issues/658)).
- Right-to-left (RTL) language support has been added, with Arabic ([#591](https://github.com/rendercv/rendercv/issues/591)), Hebrew, and Persian as built-in locales ([#452](https://github.com/rendercv/rendercv/issues/452), [#645](https://github.com/rendercv/rendercv/issues/645)).
- Built-in locale defaults for 3 additional languages have been added: Dutch ([#585](https://github.com/rendercv/rendercv/issues/585)), Norwegian Bokmål, and Norwegian Nynorsk ([#652](https://github.com/rendercv/rendercv/issues/652)).
- URLs are now allowed for the `cv.photo` field.
- Empty sections are now allowed.
- `"today"` is now supported as a value for `settings.current_date`.

### Changed

- PyPI version check is now non-blocking ([#615](https://github.com/rendercv/rendercv/issues/615)).
- `bold_keywords` now only matches full words instead of sub-words.
- Extra keys are no longer allowed in the top-level YAML input and in the `cv` field.
- Obsolete PNG files are now automatically deleted when re-rendering ([#590](https://github.com/rendercv/rendercv/issues/590)).
- YAML aliases are now treated as literal strings.

### Fixed

- The `--quiet` option of the `rendercv render` command now works correctly ([#608](https://github.com/rendercv/rendercv/issues/608)).
- The design file not applying when used with a settings file has been fixed ([#642](https://github.com/rendercv/rendercv/issues/642)).
- `bold_keywords` no longer applies to placeholder variables in file paths and PDF titles ([#557](https://github.com/rendercv/rendercv/issues/557)).
- `DAY` and `DAY_IN_TWO_DIGITS` placeholders now work correctly in output file paths ([#684](https://github.com/rendercv/rendercv/issues/684)).
- Vertical alignment of titles with icons for education entries has been fixed ([#603](https://github.com/rendercv/rendercv/issues/603)).
- Mandarin Chinese locale spelling and schema validation have been corrected ([#617](https://github.com/rendercv/rendercv/issues/617), [#678](https://github.com/rendercv/rendercv/issues/678)).
- `settings.current_date` issues have been fixed.
- Arabic, Hebrew, and Persian locale issues have been fixed.
- Empty links no longer cause failures.
- A duplicate font has been removed from `available_font_families` ([#643](https://github.com/rendercv/rendercv/issues/643)).
- YAML error handling has been improved.
- Pydantic error handling for multiple YAML sources has been improved.

### Removed

- The `ex` unit is no longer accepted in dimension fields (e.g., margins, spacing).

## [2.6] - December 23, 2025

> **Full Changelog**: [v2.5...v2.6]

### Added

- Bluesky has been added as a social network type ([#560](https://github.com/rendercv/rendercv/issues/560)).
- Built-in locale defaults for 2 additional languages have been added: Danish and Indonesian ([#556](https://github.com/rendercv/rendercv/issues/556), [#567](https://github.com/rendercv/rendercv/issues/567)).

### Fixed

- Unicode corruption in sample YAML name generation has been fixed ([#570](https://github.com/rendercv/rendercv/issues/570)).
- Typst syntax is no longer included in Markdown and HTML outputs ([#563](https://github.com/rendercv/rendercv/issues/563), [#564](https://github.com/rendercv/rendercv/issues/564)).

## [2.5] - December 13, 2025

> **Full Changelog**: [v2.4...v2.5]

### Changed

- Top note and footer now have more placeholder options available.

### Fixed

- The `--design`, `--locale`, and `--settings` options of the `rendercv render` command now work correctly ([#543](https://github.com/rendercv/rendercv/issues/543)).
- Multiline summary rendering issues in entries have been fixed.

## [2.4] - December 10, 2025

> **Full Changelog**: [v2.3...v2.4]

### Added

- A new optional `cv.headline` field has been added to display a position title at the top of the CV ([#442](https://github.com/rendercv/rendercv/issues/442)).
- Built-in locale defaults for 11 languages have been added: French, German, Hindi, Italian, Japanese, Korean, Mandarin Chinese, Portuguese, Russian, Spanish, and Turkish. Users can now use these locales without writing all the translations themselves.
- Nested bullet points are now supported in highlights ([#177](https://github.com/rendercv/rendercv/issues/177)).
- WhatsApp has been added as a social network type ([#319](https://github.com/rendercv/rendercv/issues/319)).
- The `cv.custom_connections` field has been added to allow users to define custom header connections with a placeholder (displayed text), optional URL, and Font Awesome icon name ([#408](https://github.com/rendercv/rendercv/issues/408)).
- Support for multiple email addresses, websites, and phone numbers has been added ([#541](https://github.com/rendercv/rendercv/issues/541)).
- `--quiet` option has been added `rendercv render` command to suppress all messages ([#394](https://github.com/rendercv/rendercv/issues/394)).

### Changed

- RenderCV now uses its own [Typst package](https://typst.app/universe/package/rendercv), making Typst templates much clearer and simpler. The package is maintained at [rendercv/rendercv-typst](https://github.com/rendercv/rendercv-typst).
- The [documentation](https://docs.rendercv.com) has been completely rewritten, including the user guide and developer guide.
- The `design` field structure has been completely redesigned for better clarity and organization.
- The `rendercv_settings` field has been renamed to `settings`.
- The `rendercv_settings.date` field has been renamed to `settings.current_date`.

### Fixed

- Image paths are now correctly handled when providing a full image path for the photo field ([#361](https://github.com/rendercv/rendercv/issues/361)).
- The less than symbol `<` no longer causes an "unclosed label" error ([#364](https://github.com/rendercv/rendercv/issues/364)).
- Typst commands with parentheses (e.g., `#h(1cm)`) are now properly recognized and not escaped ([#383](https://github.com/rendercv/rendercv/issues/383)).
- `C++` and other strings ending with `++` or special characters are now formatted correctly ([#388](https://github.com/rendercv/rendercv/issues/388), [#446](https://github.com/rendercv/rendercv/issues/446)).
- Rendering issues when modifying `design.entry_types` templates have been fixed ([#413](https://github.com/rendercv/rendercv/issues/413)).
- The `--watch` option now correctly triggers re-rendering when the YAML file changes ([#513](https://github.com/rendercv/rendercv/issues/513)).
- `bold_keywords` are now properly applied to `PublicationEntry` authors ([#516](https://github.com/rendercv/rendercv/issues/516)).
- Calling `rendercv` with invalid arguments now displays help text instead of raising a TypeError ([#526](https://github.com/rendercv/rendercv/issues/526)).
- Page margin parsing issues in v2.3 have been resolved ([#531](https://github.com/rendercv/rendercv/issues/531)).
- Arbitrary keys in entries are now correctly recognized and substituted in templates ([#334](https://github.com/rendercv/rendercv/issues/334), [#376](https://github.com/rendercv/rendercv/issues/376), [#534](https://github.com/rendercv/rendercv/issues/534)).

## [2.3] - October 29, 2025

> **Full Changelog**: [v2.2...v2.3]

### Added

- A new command-line option has been added: `--nopdf` to skip PDF generation ([#482](https://github.com/rendercv/rendercv/pull/482)).
- Two new social networks have been added: `Leetcode` ([#483](https://github.com/rendercv/rendercv/pull/483)) and `IMDB` ([#479](https://github.com/rendercv/rendercv/pull/479)).
- More system fonts have been added ([#466](https://github.com/rendercv/rendercv/pull/466)).
- `grade` field has been added to `EducationEntry` ([#463](https://github.com/rendercv/rendercv/pull/463)).
- Optional automatic sorting capabilities for entries have been added ([#461](https://github.com/rendercv/rendercv/pull/461)).

### Changed

- Docker image has been optimized for a smaller runtime size ([#511](https://github.com/rendercv/rendercv/pull/511)).
- Header connection order now follows the YAML key order in the input file ([#455](https://github.com/rendercv/rendercv/pull/455)).

### Fixed

- Bold keywords now correctly ignore case and don't bold sub-words ([#348](https://github.com/rendercv/rendercv/pull/348)).
- Typo "parial" has been corrected to "partial" throughout the codebase ([#380](https://github.com/rendercv/rendercv/pull/380)).
- Arbitrary keys functionality has been fixed ([#457](https://github.com/rendercv/rendercv/pull/457)).

## [2.2] - January 25, 2025

> **Full Changelog**: [v2.1...v2.2]

### Added

- Two new entry types have been added: `NumberedEntry` and `ReversedNumberedEntry`.
- Four new fields have been added to the YAML input file: `design.section_titles.font_family`, `design.header.name_font_family`, `design.header.connections_font_family`, and `design.entries.allow_page_break_in_sections`.
- New fonts have been added: EB Garamond, Fontin, Gentium Book Plus, Lato, Noto Sans, Open Sans, Raleway, and Open Sauce Sans.
- Users are now allowed to use custom fonts, by providing font files in the `fonts` folder next to the YAML input file.
- Typst commands are now allowed in the YAML input file. For example, a text can be converted to a subscript with `#sub[text]`.
- A new social network has been added: `X` ([#212](https://github.com/rendercv/rendercv/pull/212), [#187](https://github.com/rendercv/rendercv/issues/187), [#109](https://github.com/rendercv/rendercv/issues/109), [#107](https://github.com/rendercv/rendercv/issues/107)).
- Executable files for Windows, MacOS, and Linux are now available with each release.

### Fixed

- `None` values in the entries are now handled correctly.
- `--png-path` option of the `rendercv render` command has been fixed ([#332](https://github.com/rendercv/rendercv/issues/332)).
- Issues with escaping Markdown characters have been fixed ([#347](https://github.com/rendercv/rendercv/issues/347)).


## [2.1] - January 25, 2025

> **Full Changelog**: [v2.0...v2.1]

### Added

- The `rendercv render` error caused by an open output PDF file in Windows is now handled ([#327](https://github.com/rendercv/rendercv/pull/327)).

### Fixed

- The "Font Awesome 6" font family issue (missing icons in the header) has been fixed ([#314](https://github.com/rendercv/rendercv/pull/314)).
- The Docker image has been fixed to use the latest version of RenderCV ([#321](https://github.com/rendercv/rendercv/pull/321)).
- Partial installation (`pip install rendercv` instead of `pip install rendercv[full]`) errors have been fixed ([#326](https://github.com/rendercv/rendercv/pull/326)).
- Path issues in `rendercv_settings` and CLI have been fixed ([#312](https://github.com/rendercv/rendercv/pull/312)).
- Bold and italic text rendering issues have been fixed ([#303](https://github.com/rendercv/rendercv/pull/303)).
- Asterisk is now escaped in Typst ([#303](https://github.com/rendercv/rendercv/pull/303)).

## [2.0] - January 7, 2025

> **Full Changelog**: [v1.18...v2.0]

RenderCV has transitioned from using $\LaTeX$ to Typst. RenderCV is now much faster and more powerful.

### Added

- RenderCV now supports Chinese, Japanese, and Korean characters by default ([#61](https://github.com/rendercv/rendercv/issues/61)).
- A new theme has been added: `engineeringclassic`.
- `summary` field has been added to `NormalEntry`, `ExperienceEntry`, and `EducationEntry` ([#210](https://github.com/rendercv/rendercv/issues/210)).
- `rendercv_settings.date` field has been added for time span calculations and last updated date text.

### Changed

- $\LaTeX$ has been replaced with Typst.
- The `design` field has been changed completely.
- The `locale_catalog` field has been renamed to `locale`, and some fields have been moved from `design` to `locale`.
- The `moderncv` theme's header has been changed.


## [1.18] - January 1, 2025

> **Full Changelog**: [v1.17...v1.18]

### Changed

- `design.seperator_between_connections` field has been renamed to `design.separator_between_connections` ([#282](https://github.com/rendercv/rendercv/issues/277)).

### Fixed

- `locale` field has been fixed ([#282](https://github.com/rendercv/rendercv/issues/275)).

## [1.17] - December 25, 2024

> **Full Changelog**: [v1.16...v1.17]

### Added
- `cv.photo` field has been added to the YAML input file. It allows users to add a photo to their CVs ([#193](https://github.com/rendercv/rendercv/pull/193)).
- `rendercv_settings.bold_keywords` field has been added to the YAML input file. It allows users to make specific keywords automatically bold in the rendered CV ([#144](https://github.com/rendercv/rendercv/issues/144)).
- `markdown_to_latex` filter has been added to Jinja templates ([#269](https://github.com/rendercv/rendercv/pull/269)).

### Changed
- `design.last_updated_date_style` and `design.page_numbering_style` fields are moved to `locale.last_updated_date_style` and `locale.page_numbering_style` fields, respectively ([#270](https://github.com/rendercv/rendercv/pull/270)).

## [1.16] - December 10, 2024

> **Full Changelog**: [v1.15...v1.16]

### Fixed

- `rendercv render` command has been fixed for Python 3.10 and 3.11 ([#249](https://github.com/rendercv/rendercv/pull/249), [#250](https://github.com/rendercv/rendercv/issues/250)).


## [1.15] - December 9, 2024

> **Full Changelog**: [v1.14...v1.15]

### Added

-   Four new options are added to the `rendercv render` command:
    -   `--watch` ([#170](https://github.com/rendercv/rendercv/pull/170)). It re-runs RenderCV automatically whenever the input file changes.
    -   `--design`, `--locale`, and `--rendercv_settings` ([#220](https://github.com/rendercv/rendercv/pull/220)). They take the `design`, `locale`, and `rendercv_settings` fields as separate YAML files.
-   The docker image of RenderCV is pushed to [Docker Hub](https://hub.docker.com/r/rendercv/rendercv) ([#222](https://github.com/rendercv/rendercv/issues/222)).
-   Telegram has been added as a social network type ([#187](https://github.com/rendercv/rendercv/issues/187)).
-   Math equations are now displayed in HTML with KaTeX ([#200](https://github.com/rendercv/rendercv/pull/200)).

### Changed

-   Math equations are now written between `$$` instead of `$`.

### Fixed

-   Path issues related to custom themes outside of root have been solved ([#240](https://github.com/rendercv/rendercv/issues/240)).
-   URL escaping issues have been solved ([#223](https://github.com/rendercv/rendercv/issues/223), [#236](https://github.com/rendercv/rendercv/issues/236)).
-   Placeholders can now be used in the `rendercv_settings.render_command.output_folder_name` field.
-   Special LATEX characters are now escaped in the section titles.
-   DOI rendering issues have been solved ([#184](https://github.com/rendercv/rendercv/issues/184)).
-   The `rendercv_settings.render_command.use_local_latex_command` field has been fixed ([#178](https://github.com/rendercv/rendercv/issues/178)).
-   The issue of rendering when PDF is open on Windows has been handled ([#172](https://github.com/rendercv/rendercv/issues/172)).
-   $ sign now works without escaping ([#154](https://github.com/rendercv/rendercv/issues/154)).
-   Timespan calculation has been fixed ([#180](https://github.com/rendercv/rendercv/pull/180)).
-   `PublicationEntry`'s `url` field's $\LaTeX$ character escaping issues have been fixed ([#236](https://github.com/rendercv/rendercv/issues/236)).


## [1.14] - September 7, 2024

> **Full Changelog**: [v1.13...v1.14]

### Added

- `rendercv_settings` field has been added to the YAML input file. It will be extended in the future.


## [1.13] - July 23, 2024

> **Full Changelog**: [v1.12...v1.13]

### Added

- Arbitrary keys are now allowed in the `cv` field.
- Two new fields have been added to the `locale` field: `phone_number_format` and `date_style` ([#130](https://github.com/rendercv/rendercv/issues/130)).

### Changed

- The default value of the `design.show_timespan_in` field for the `classic` theme has been changed to `[]` ([#135](https://github.com/rendercv/rendercv/issues/135)).
- Custom theme names with digits are now allowed.

### Fixed

- The data model overriding in CLI has been fixed.
- The `url` field is now shown in the `PublicationEntry` ([#128](https://github.com/rendercv/rendercv/issues/128)).

## [1.12] - July 16, 2024

> **Full Changelog**: [v1.11...v1.12]

### Added

- Arbitrary keys are now allowed in entry types. Users can use these keys in their templates.
- The `locale.full_names_of_months` field has been added to the data model ([#111](https://github.com/rendercv/rendercv/issues/111)).
- The `TODAY` placeholder can be used in the `design.page_numbering_style` field now.

### Changed

- Some articles and prepositions (like "and," "of," "the," etc.) are now not capitalized in the section titles.

### Fixed

- The `TODAY` placeholder in `design.last_updated_style` field is localized with the new `locale.full_names_of_months` field ([#111](https://github.com/rendercv/rendercv/issues/111))
- Rendering Markdown links with special characters has been fixed ([#112](https://github.com/rendercv/rendercv/issues/112)).

## [1.11] - June 19, 2024

> **Full Changelog**: [v1.10...v1.11]

### Added

- CLI options now have short versions.
- CLI now notifies the user when a new version is available ([#89](https://github.com/rendercv/rendercv/issues/89)).
- `Google Scholar` has been added as a social network type ([#85](https://github.com/rendercv/rendercv/issues/85)).
- Two new design options have been added to the `classic`, `sb2nov`, and `engineeringresumes` themes: `separator_between_connections` and `use_icons_for_connections`.

### Changed

- The punctuation of "ORCID" has been changed to uppercase, which was previously "Orcid" ([#90](https://github.com/rendercv/rendercv/issues/90)).
- HTML output has been improved with better CSS ([#96](https://github.com/rendercv/rendercv/discussions/96)).
- More complex section titles are now supported ([#106](https://github.com/rendercv/rendercv/issues/106)).
- Month abbreviations are not using dots anymore.
- Date ranges are now displayed as "Month Year - Month Year" instead of "Month Year to Month Year."
- DOI validator in the `PublicationEntry` has been disabled.
- `url` field has been added to the `PublicationEntry` as an alternative to the `doi` field ([#105](https://github.com/rendercv/rendercv/issues/105))
- `YouTube` username should be given without `@` now.

### Fixed

- The error related to the `validation_error_cause` flag of Pydantic has been fixed ([#66](https://github.com/rendercv/rendercv/issues/66)).
- `rendercv render` with relative input file paths has been fixed ([#95](https://github.com/rendercv/rendercv/issues/95)).

### Removed

- `Twitter` has been removed as a social network type ([#109](https://github.com/rendercv/rendercv/issues/109)).

## [1.10] - May 25, 2024

> **Full Changelog**: [v1.9...v1.10]

### Added

- `rendercv --version` command has been added to show the version of RenderCV.
- `StackOverflow` ([#77](https://github.com/rendercv/rendercv/pull/77)), `GitLab` ([#78](https://github.com/rendercv/rendercv/pull/78)), `ResearchGate`, and `YouTube` has been added to the available social network types.

### Fixed

- Authors in `PublicationEntry` are now displayed correctly in `engineeringresumes` and `sb2nov` themes.
- `justify-with-no-hyphenation` text alignment has been fixed.

## [1.9] - May 19, 2024

> **Full Changelog**: [v1.8...v1.9]

### Added

- RenderCV is now a multilingual tool. English strings can be overridden with `locale` section in the YAML input file ([#26](https://github.com/rendercv/rendercv/issues/26), [#20](https://github.com/rendercv/rendercv/pull/20)).
- PNG files for each page can be generated now ([#57](https://github.com/rendercv/rendercv/issues/57)).
- `rendercv new` command now generates Markdown and $\LaTeX$ source files in addition to the YAML input file so that the default templates can be modified easily.
- A new CLI command has been added, `rendercv create-theme`, to allow users to create their own themes easily.
  ```bash
  rendercv create-theme "customtheme" --based-on "classic"
  ```
- [A developer guide](https://docs.rendercv.com/developer_guide/) has been written.
- New options have been added to the `rendercv render` command:
    - `--output-folder-name "OUTPUT_FOLDER_NAME"`: Generates the output files in a folder with the given name. By default, the output folder name is `rendercv_output`. The output folder will be created in the current working directory. ([#58](https://github.com/rendercv/rendercv/issues/58))
    - `--latex-path LATEX_PATH`: Copies the generated $\LaTeX$ source code from the output folder and pastes it to the specified path.
    - `--pdf-path PDF_PATH`: Copies the generated PDF file from the output folder and pastes it to the specified path.
    - `--markdown-path MARKDOWN_PATH`: Copies the generated Markdown file from the output folder and pastes it to the specified path.
    - `--html-path HTML_PATH`: Copies the generated HTML file from the output folder and pastes it to the specified path.
    - `--png-path PNG_PATH`: Copies the generated PNG files from the output folder and pastes them to the specified path.
    - `--dont-generate-markdown`: Prevents the generation of the Markdown file.
    - `--dont-generate-html`: Prevents the generation of the HTML file.
    - `--dont-generate-png`: Prevents the generation of the PNG files.
    - `--ANY.LOCATION.IN.THE.YAML.FILE "VALUE"`: Overrides the value of `ANY.LOCATION.IN.THE.YAML.FILE` with `VALUE`. This option can be used to avoid storing sensitive information in the YAML file. Sensitive information, like phone numbers, can be passed as a command-line argument with environment variables. This method is also beneficial for creating multiple CVs using the same YAML file by changing only a few values.
- New options have been added to the `rendercv new` command:
    - `--dont-create-theme-source-files`: Prevents the creation of the theme source files. By default, the theme source files are created.
    - `--dont-create-markdown-source-files`: Prevents the creation of the Markdown source files. By default, the Markdown source files are created.

### Changed

- Package size has been reduced by removing unnecessary TinyTeX files.
- `date` field is now optional in `PublicationEntry`.
- [README.md](https://github.com/rendercv/rendercv) and the [documentation](https://docs.rendercv.com/) have been rewritten.

### Fixed

- `ExperienceEntry` and `NormalEntry` without location and dates have been fixed in the `engineeringresumes`, `classic`, and `sb2nov` themes.
- $\LaTeX$ templates have been polished.
- Bugs related to the special characters in email addresses have been fixed ([#64](https://github.com/rendercv/rendercv/issues/64)).

## [1.8] - April 16, 2024

> **Full Changelog**: [v1.7...v1.8]

### Added

- Horizontal space has been added between entry titles and dates in the `engineeringresumes` theme.
- The `date_and_location_width` option has been added to the `engineeringresumes` theme.
- A new design option, `disable_external_link_icons`, has been added.

### Changed

- `sb2nov` theme's $\LaTeX$ code has been changed completely. There are slight changes in the looks.
- `classic`, `sb2nov`, and `engineeringresumes` use the same $\LaTeX$ code base now.
- The design option `show_last_updated_date` has been renamed to `disable_last_updated_date` for consistency.
- Mastodon links now use the original hostnames instead of `https://mastodon.social/`.

### Fixed

- The location is now shown in the header ([#54](https://github.com/rendercv/rendercv/issues/54)).
- The `education_degree_width` option of the `classic` theme has been fixed.
- Lualatex and xelatex rendering problems have been fixed ([#52](https://github.com/rendercv/rendercv/issues/52)).

## [1.7] - April 8, 2024

> **Full Changelog**: [v1.6...v1.7]

### Added

- The new theme, `engineeringresumes`, is ready to be used now.
- The `education_degree_width` design option has been added for the `classic` theme.
- `last_updated_date_template` design option has been added for all the themes except `moderncv`.

### Fixed

- Highlights can now be broken into multiple pages in the `classic` theme ([#47](https://github.com/rendercv/rendercv/issues/47)).
- Some JSON Schema bugs have been fixed.

## [1.6] - March 31, 2024

> **Full Changelog**: [v1.5...v1.6]

### Added

- A new theme has been added: `engineeringresumes`. It hasn't been tested fully yet.
- A new text alignment option has been added to `classic` and `sb2nov`: `justified-with-no-hyphenation` ([#34](https://github.com/rendercv/rendercv/issues/34))
- Users are now allowed to run local `lualatex`, `xelatex`, `latexmk` commands in addition to `pdflatex` ([#48](https://github.com/rendercv/rendercv/issues/48)).

### Changed

- ORCID is now displayed in the header like other social media links.

### Fixed

- Decoding issues have been fixed ([#29](https://github.com/rendercv/rendercv/issues/29)).
- Classic theme's `ExperienceEntry` has been fixed ([#49](https://github.com/rendercv/rendercv/issues/49)).

## [1.5] - March 27, 2024

> **Full Changelog**: [v1.4...v1.5]

### Added

- Users can now make bold or italic texts normal with Markdown syntax.

### Changed

- The `moderncv` theme doesn't italicize any text by default now.

### Fixed

- The `moderncv` theme's PDF title issue has been fixed.
- The ordering of the data models' keys in JSON Schema has been fixed.
- The unhandled exception when a custom theme's `__init__.py` file is invalid has been fixed.
- The `sb2nov` theme's `PublicationEntry` without `journal` and `doi` fields is now rendered correctly.
- The `sb2nov` theme's `OneLineEntry`'s colon issue has been fixed.

## [1.4] - March 10, 2024

> **Full Changelog**: [v1.3...v1.4]

### Added

- A new entry type has been added: `BulletEntry`

### Changed

- `OneLineEntry`'s `name` field has been changed to `label`. This was required to generalize the entry validations.
- `moderncv`'s highlights are now bullet points.
- `moderncv`'s `TextEntries` don't have bullet points anymore.
- `sb2nov`'s `TextEntries` don't have bullet points anymore.

## [1.3] - March 9, 2024

> **Full Changelog**: [v1.2...v1.3]

### Added

- CLI documentation has been added to the user guide.

### Changed

- Future dates are now allowed.
- Authors' first names are no longer abbreviated in `PublicationEntry`.
- Markdown is now supported in the `authors` field of `PublicationEntry`.
- `doi` field is now optional for `PublicationEntry`.

### Fixed

- The `journal` is now displayed in the `PublicationEntry` of the `sb2nov` theme.

## [1.2] - February 27, 2024

> **Full Changelog**: [v1.1...v1.2]

### Fixed

- Markdown `TextEntry`, where all the paragraphs were concatenated into a single paragraph, has been fixed.
- Markdown `OneLineEntry`, where all the one-line entries were concatenated into a single line, has been fixed.
- The `classic` theme's `PublicationEntry`, where blank parentheses were rendered when the `journal` field was not provided, has been fixed.
- A bug where an email with special characters caused a $\LaTeX$ error has been fixed.
- The Unicode error when `rendercv new` is called with a name containing special characters has been fixed.

## [1.1] - February 25, 2024

> **Full Changelog**: [v0.10...v1.1]

### Added

- RenderCV is now a $\LaTeX$ CV framework. Users can move their $\LaTeX$ CV themes to RenderCV to produce their CV from RenderCV's YAML input.
- RenderCV now generates Markdown and HTML versions of the CV to allow users to paste the content of the CV to another software (like [Grammarly](https://www.grammarly.com/)) for spell checking.
- A new theme has been added: `moderncv`.
- A new theme has been added: `sb2nov`.

### Changed

- The data model has been changed to be more flexible. All the sections are now under the `sections` field. All the keys are arbitrary and rendered as section titles. The entry types can be any of the six built-in entry types, and they will be detected by RenderCV for each section.
- The templating system has been changed completely.
- The command-line interface (CLI) has been improved.
- The validation error messages have been improved.
- TinyTeX has been moved to [another repository](https://github.com/sinaatalay/tinytex-release), and it is being pulled as a Git submodule. It is still pushed to PyPI, but it's not a part of the repository anymore.
- Tests have been improved, and it uses `pytest` instead of `unittest`.
- The documentation has been rewritten.
- The reference has been rewritten.
- The build system has been changed from `setuptools` to `hatchling`.

## [0.10] - November 29, 2023

> **Full Changelog**: [v0.9...v0.10]

### Fixed

- Author highlighting issue has been fixed in `PublicationEntry`.

## [0.9] - November 29, 2023

> **Full Changelog**: [v0.8...v0.9]

### Added

- Page numbering has been added.
- Text alignment options have been added (left-aligned or justified).
- Header options (margins and header font size) have been added.
- The `university_projects` field has been added.

## [0.8] - November 17, 2023

> **Full Changelog**: [v0.7...v0.8]

### Fixed

- YYYY date issue has been solved ([#5](https://github.com/rendercv/rendercv/issues/5)).

## [0.7] - November 3, 2023

> **Full Changelog**: [v0.6...v0.7]

### Changed

- The date type has been improved. It now supports `YYYY-MM-DD`, `YYYY-MM`, and `YYYY` formats.

### Fixed

- The error messages for custom sections have been fixed.

## [0.6] - October 28, 2023

> **Full Changelog**: [v0.5...v0.6]

### Added

- New fields have been added: `experience`, `projects`, `awards`, `interests`, and `programming_skills`.

### Fixed

- DOI validation bug has been fixed by [@LabAsim](https://github.com/LabAsim) in [#3](https://github.com/rendercv/rendercv/pull/3).

## [0.5] - October 27, 2023

> **Full Changelog**: [v0.4...v0.5]

### Added

- ORCID support has been added.

### Fixed

- Special $\LaTeX$ characters' escaping has been fixed.

## [0.4] - October 22, 2023

> **Full Changelog**: [v0.3...v0.4]

### Changed

- CLI has been improved for more intuitive validation error messages.

## [0.3] - October 20, 2023

> **Full Changelog**: [v0.2...v0.3]

### Fixed

- The colors of the CLI output have been fixed.
- Encoding problems have been fixed.

## [0.2] - October 17, 2023

> **Full Changelog**: [v0.1...v0.2]

### Fixed

- MacOS compatibility issues have been fixed.

## [0.1] - October 15, 2023

The first release of RenderCV.

[v2.8...v2.9]: https://github.com/rendercv/rendercv/compare/v2.8...v2.9
[v2.7...v2.8]: https://github.com/rendercv/rendercv/compare/v2.7...v2.8
[v2.6...v2.7]: https://github.com/rendercv/rendercv/compare/v2.6...v2.7
[v2.5...v2.6]: https://github.com/rendercv/rendercv/compare/v2.5...v2.6
[v2.4...v2.5]: https://github.com/rendercv/rendercv/compare/v2.4...v2.5
[v2.3...v2.4]: https://github.com/rendercv/rendercv/compare/v2.3...v2.4
[v2.2...v2.3]: https://github.com/rendercv/rendercv/compare/v2.2...v2.3
[v2.1...v2.2]: https://github.com/rendercv/rendercv/compare/v2.1...v2.2
[v2.0...v2.1]: https://github.com/rendercv/rendercv/compare/v2.0...v2.1
[v1.18...v2.0]: https://github.com/rendercv/rendercv/compare/v1.18...v2.0
[v1.17...v1.18]: https://github.com/rendercv/rendercv/compare/v1.17...v1.18
[v1.16...v1.17]: https://github.com/rendercv/rendercv/compare/v1.16...v1.17
[v1.15...v1.16]: https://github.com/rendercv/rendercv/compare/v1.15...v1.16
[v1.14...v1.15]: https://github.com/rendercv/rendercv/compare/v1.14...v1.15
[v1.13...v1.14]: https://github.com/rendercv/rendercv/compare/v1.13...v1.14
[v1.12...v1.13]: https://github.com/rendercv/rendercv/compare/v1.12...v1.13
[v1.11...v1.12]: https://github.com/rendercv/rendercv/compare/v1.11...v1.12
[v1.10...v1.11]: https://github.com/rendercv/rendercv/compare/v1.10...v1.11
[v1.9...v1.10]: https://github.com/rendercv/rendercv/compare/v1.9...v1.10
[v1.8...v1.9]: https://github.com/rendercv/rendercv/compare/v1.8...v1.9
[v1.7...v1.8]: https://github.com/rendercv/rendercv/compare/v1.7...v1.8
[v1.6...v1.7]: https://github.com/rendercv/rendercv/compare/v1.6...v1.7
[v1.5...v1.6]: https://github.com/rendercv/rendercv/compare/v1.5...v1.6
[v1.4...v1.5]: https://github.com/rendercv/rendercv/compare/v1.4...v1.5
[v1.3...v1.4]: https://github.com/rendercv/rendercv/compare/v1.3...v1.4
[v1.2...v1.3]: https://github.com/rendercv/rendercv/compare/v1.2...v1.3
[v1.1...v1.2]: https://github.com/rendercv/rendercv/compare/v1.1...v1.2
[v0.10...v1.1]: https://github.com/rendercv/rendercv/compare/v0.10...v1.1
[v0.9...v0.10]: https://github.com/rendercv/rendercv/compare/v0.9...v0.10
[v0.8...v0.9]: https://github.com/rendercv/rendercv/compare/v0.8...v0.9
[v0.7...v0.8]: https://github.com/rendercv/rendercv/compare/v0.7...v0.8
[v0.6...v0.7]: https://github.com/rendercv/rendercv/compare/v0.6...v0.7
[v0.5...v0.6]: https://github.com/rendercv/rendercv/compare/v0.5...v0.6
[v0.4...v0.5]: https://github.com/rendercv/rendercv/compare/v0.4...v0.5
[v0.3...v0.4]: https://github.com/rendercv/rendercv/compare/v0.3...v0.4
[v0.2...v0.3]: https://github.com/rendercv/rendercv/compare/v0.2...v0.3
[v0.1...v0.2]: https://github.com/rendercv/rendercv/compare/v0.1...v0.2
[2.9]: https://github.com/rendercv/rendercv/releases/tag/v2.9
[2.8]: https://github.com/rendercv/rendercv/releases/tag/v2.8
[2.7]: https://github.com/rendercv/rendercv/releases/tag/v2.7
[2.6]: https://github.com/rendercv/rendercv/releases/tag/v2.6
[2.5]: https://github.com/rendercv/rendercv/releases/tag/v2.5
[2.4]: https://github.com/rendercv/rendercv/releases/tag/v2.4
[2.3]: https://github.com/rendercv/rendercv/releases/tag/v2.3
[2.2]: https://github.com/rendercv/rendercv/releases/tag/v2.2
[2.1]: https://github.com/rendercv/rendercv/releases/tag/v2.1
[2.0]: https://github.com/rendercv/rendercv/releases/tag/v2.0
[1.18]: https://github.com/rendercv/rendercv/releases/tag/v1.18
[1.17]: https://github.com/rendercv/rendercv/releases/tag/v1.17
[1.16]: https://github.com/rendercv/rendercv/releases/tag/v1.16
[1.15]: https://github.com/rendercv/rendercv/releases/tag/v1.15
[1.14]: https://github.com/rendercv/rendercv/releases/tag/v1.14
[1.13]: https://github.com/rendercv/rendercv/releases/tag/v1.13
[1.12]: https://github.com/rendercv/rendercv/releases/tag/v1.12
[1.11]: https://github.com/rendercv/rendercv/releases/tag/v1.11
[1.10]: https://github.com/rendercv/rendercv/releases/tag/v1.10
[1.9]: https://github.com/rendercv/rendercv/releases/tag/v1.9
[1.8]: https://github.com/rendercv/rendercv/releases/tag/v1.8
[1.7]: https://github.com/rendercv/rendercv/releases/tag/v1.7
[1.6]: https://github.com/rendercv/rendercv/releases/tag/v1.6
[1.5]: https://github.com/rendercv/rendercv/releases/tag/v1.5
[1.4]: https://github.com/rendercv/rendercv/releases/tag/v1.4
[1.3]: https://github.com/rendercv/rendercv/releases/tag/v1.3
[1.2]: https://github.com/rendercv/rendercv/releases/tag/v1.2
[1.1]: https://github.com/rendercv/rendercv/releases/tag/v1.1
[0.10]: https://github.com/rendercv/rendercv/releases/tag/v0.10
[0.9]: https://github.com/rendercv/rendercv/releases/tag/v0.9
[0.8]: https://github.com/rendercv/rendercv/releases/tag/v0.8
[0.7]: https://github.com/rendercv/rendercv/releases/tag/v0.7
[0.6]: https://github.com/rendercv/rendercv/releases/tag/v0.6
[0.5]: https://github.com/rendercv/rendercv/releases/tag/v0.5
[0.4]: https://github.com/rendercv/rendercv/releases/tag/v0.4
[0.3]: https://github.com/rendercv/rendercv/releases/tag/v0.3
[0.2]: https://github.com/rendercv/rendercv/releases/tag/v0.2
[0.1]: https://github.com/rendercv/rendercv/releases/tag/v0.1
