---
toc_depth: 1
---

# Changelog

All notable changes to this project will be documented in this file.

[Click here to see the unreleased changes.](https://github.com/rendercv/rendercv/compare/v2.3...HEAD)

<!--
### Added
### Changed
### Fixed
### Removed
-->

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
- The `design` field has been changed completely. See the [documentation](https://docs.rendercv.com/user_guide/structure_of_the_yaml_input_file/#design-field) for details.
- The `locale_catalog` field has been renamed to `locale`, and some fields have been moved from `design` to `locale`. See the [documentation](https://docs.rendercv.com/user_guide/structure_of_the_yaml_input_file/#locale-field) for details.
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

- `rendercv_settings` field has been added to the YAML input file. For details, see [here](../user_guide/structure_of_the_yaml_input_file.md#rendercv_settings-field). It will be extended in the future.


## [1.13] - July 23, 2024

> **Full Changelog**: [v1.12...v1.13]

### Added

- Arbitrary keys are now allowed in the `cv` field. For details, see [here](../user_guide/structure_of_the_yaml_input_file.md#using-arbitrary-keys).
- Two new fields have been added to the `locale` field: `phone_number_format` and `date_style` ([#130](https://github.com/rendercv/rendercv/issues/130)). For details, see [here](../user_guide/structure_of_the_yaml_input_file.md#locale-field).

### Changed

- The default value of the `design.show_timespan_in` field for the `classic` theme has been changed to `[]` ([#135](https://github.com/rendercv/rendercv/issues/135)).
- Custom theme names with digits are now allowed.

### Fixed

- The data model overriding in CLI has been fixed.
- The `url` field is now shown in the `PublicationEntry` ([#128](https://github.com/rendercv/rendercv/issues/128)).

## [1.12] - July 16, 2024

> **Full Changelog**: [v1.11...v1.12]

### Added

- Arbitrary keys are now allowed in entry types. Users can use these keys in their templates. For details, see the [documentation](../user_guide/structure_of_the_yaml_input_file.md#using-arbitrary-keys).
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

- CLI options now have short versions. See the [CLI documentation](https://docs.rendercv.com/user_guide/cli/) for more information.
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

- RenderCV is now a multilingual tool. English strings can be overridden with `locale` section in the YAML input file ([#26](https://github.com/rendercv/rendercv/issues/26), [#20](https://github.com/rendercv/rendercv/pull/20)). See the [documentation](../user_guide/structure_of_the_yaml_input_file.md#locale-field) for more information.
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
