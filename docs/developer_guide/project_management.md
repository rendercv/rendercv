---
toc_depth: 2
---

# Project Management

RenderCV's Python files say what the program does. The files around them answer three practical questions: what does the project need installed, how does everyone get exactly the same tools, and how does the finished program reach users? This page explains those files.

## Describing the project

[`pyproject.toml`](https://github.com/rendercv/rendercv/blob/main/pyproject.toml) is the project's description card. It records the package's name and version, the Python versions it supports, what it depends on, and settings for the development tools.

A **dependency** is a package that RenderCV uses but didn't write: ruamel.yaml reads YAML, Pydantic checks the input, Jinja fills in templates. Listing them lets an installer fetch them automatically.

`pyproject.toml` also connects the `rendercv` command to Python code:

```toml
[project.scripts]
rendercv = "rendercv.cli.entry_point:entry_point"
```

When RenderCV is installed, the installer creates a `rendercv` command that runs the `entry_point()` function in that module. This link is called an **entry point**.

Not every user needs every dependency. A Python program that only reads and checks CV data has no use for the command line or the PDF compiler. So the basic `rendercv` package contains the data models and templates, and `rendercv[full]` adds the command-line interface, the Typst compiler, file watching, and fonts. Python packaging calls such a named set of optional dependencies an **extra**; this one is named `full`.

Developing RenderCV needs tools that users never do, such as pytest for testing or Zensical for this website. They're listed in **dependency groups**, which `just sync` installs for contributors and which never reach users.

## Keeping everyone's versions identical

`pyproject.toml` usually allows a range of versions, such as `pydantic>=2.14.1`. The range helps users combine RenderCV with other packages, but installing on two different days can then produce two different sets of versions, and a bug can appear on one computer and not on another.

[`uv.lock`](https://github.com/rendercv/rendercv/blob/main/uv.lock) removes that uncertainty. It records the exact version chosen for every package, including the packages those packages depend on. `just sync` installs exactly those versions into `.venv`, and the automated checks do the same. Commit `uv.lock` so that contributors and checks share it. It covers every supported operating system and Python version, but those environments still differ, so we test on each of them. See [uv's documentation](https://docs.astral.sh/uv/concepts/projects/layout/).

After changing the dependencies in `pyproject.toml`, run `just lock`. To move to newer versions on purpose, run `uv lock --upgrade`, then review and test the result. Let uv write `uv.lock`; don't edit it by hand.

A **workspace** keeps several related Python projects in one repository with one lock file and one environment. RenderCV's workspace contains the main package, the fonts package in `packages/rendercv-fonts`, and the ATS analysis tools in `scripts/ats_proof`. The fonts package is released separately, with its own version. During development RenderCV uses the fonts package from this repository; a user's installation downloads the published one.

## Sharing commands

The [`justfile`](https://github.com/rendercv/rendercv/blob/main/justfile) gives names to commands, so everyone runs `just test` or `just build-docs` with the same options. `just --list` shows them all. Longer tasks, such as generating the examples, are Python programs in `scripts/` that a `just` command runs.

## Checking code automatically

Some mistakes can be found without running the code. A **linter** reads code and points out likely errors, such as a variable that is never used. A **formatter** rewrites code into one consistent layout, so reviews can focus on meaning instead of spacing. Ruff does both. A **type checker** compares how each value is used with the type the code declares for it, catching mistakes such as passing text where a number is expected; RenderCV uses ty.

[prek](https://prek.j178.dev/) runs all of these, plus a spell checker and a check of configuration files, in one command. `.pre-commit-config.yaml` lists the checks. `just check` runs prek, and the [GitHub workflows](github_workflows.md) run it on every proposed change. The checks use the versions in `uv.lock`, so they reach the same verdict on every computer.

## Delivering RenderCV to users

Users install RenderCV with a command such as `pip install "rendercv[full]"`, which downloads it from **PyPI**, the public catalog of Python packages. A file prepared for installation is called a **distribution**. There are two kinds:

- A **wheel** (`.whl`) is the package ready to install; the installer only unpacks it.
- A **source distribution** (`.tar.gz`) holds the source code, from which an installer can build a wheel.

A **build backend** is the tool that creates these files according to `pyproject.toml`. RenderCV uses `uv_build`. From the repository folder:

```bash
just download-typst-packages
uv build --package rendercv
```

The first command downloads the Typst packages that RenderCV's themes import. Git ignores them, but the build includes them, so users can render with the built-in themes without downloading anything. Custom Typst code can still import other packages, which then need the network. The second command builds RenderCV into `dist/`, and `uv build --package rendercv-fonts` builds the fonts package. The [release workflows](github_workflows.md#releases) upload them to PyPI.

Not everyone has Python. `just create-executable` uses PyInstaller to pack Python, RenderCV, and everything they need into a single program file for one operating system, which runs without installing anything. [Docker](dockerfile.md) is a third route. The executable recipe, the release workflow, and the Dockerfile all download the Typst packages before building.
