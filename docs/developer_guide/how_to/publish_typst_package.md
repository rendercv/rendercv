---
toc_depth: 2
---

# Publish the Typst Package

RenderCV's layout code is written in Typst, as a **package**: a reusable bundle of Typst code that any Typst document can import. It lives in `src/rendercv/renderer/rendercv_typst/` and also works on its own, so Typst users can write CVs without the Python application. [Typst Universe](https://typst.app/universe/) is the public catalog of Typst packages. Publishing there lets anyone use it with one line, such as `#import "@preview/rendercv:0.4.0": *`.

The package has its own version number, separate from the Python package. Publishing it means proposing it to the [typst/packages](https://github.com/typst/packages) repository with a pull request; RenderCV's release workflow doesn't do that.

## Check the package

`typst.toml` is the package's **manifest**, its identity card: it tells Typst the package's name and version and which file to load first. Read the version being published from it, then check:

- Required files: `lib.typ`, `typst.toml`, `README.md`, `LICENSE`, `thumbnail.png`, and `template/main.typ`.
- Manifest fields: name, version, entry point, authors, license, and description, plus the template's path, entry point, and thumbnail.
- Version numbers: the imports in `README.md`, `template/main.typ`, and the examples match the manifest.
- Changelog: `CHANGELOG.md` has an entry for the version.
- Examples: every theme pictured in `README.md` has an `examples/<theme>.typ`, and relative links work.
- Template import: `template/main.typ` imports `@preview/rendercv:<version>`, not `lib.typ` through a relative path, because the template is copied into users' own projects, where that path doesn't exist.

Compile the template and the examples, and look at the results. Fix every failure before submitting. The upstream [publishing guide](https://github.com/typst/packages/blob/main/docs/publishing.md) lists the current requirements.

## Prepare the submission

First check whether a pull request for this version already exists. Submissions are made from a **fork**, your own copy of the typst/packages repository on GitHub, where you can commit and then propose the changes back. Start a new branch from upstream `main` in a separate checkout, so other package submissions you may have in progress stay untouched.

Create `packages/preview/rendercv/<version>/` and copy `lib.typ`, `typst.toml`, `README.md`, `LICENSE`, `thumbnail.png`, `template/`, and `examples/` into it. Leave out generated PDFs, `CHANGELOG.md`, and repository files. Check the copy again, including its relative links and the template's import.

## Open the pull request

Title it `rendercv:<version>` and fill in the current upstream pull request template. Say whether this is a new package or an update, summarize what changed since the previous published version, using the version's changelog entry, and keep the contributor credits. Report the pull request's link, its branch, and anything reviewers still need to look at.
