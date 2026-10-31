---
toc_depth: 1
---

# Setup

This guide teaches the tools behind RenderCV while you set it up, assuming you have never used them. Start here to run the project, then read [Understanding RenderCV](understanding_rendercv.md) to follow a CV from YAML to PDF.

## Prerequisites

You need three tools. Each one solves a problem that every software project runs into.

**[Git](https://git-scm.com/)** keeps the history of a project's files. Each saved change, called a **commit**, records what changed, who changed it, and why. With that history you can compare versions, undo mistakes, and prepare several changes separately. GitHub stores RenderCV's history online so that many people can work on the same files.

**[uv](https://docs.astral.sh/uv/)** installs Python and the packages RenderCV is built on. RenderCV reuses code that other people wrote and published as **packages**, and it needs particular versions of them. Installed by hand, those packages would be shared by every Python project on your computer, and two projects needing different versions would break each other. uv gives this project its own Python and exactly the versions it needs. You don't have to install Python yourself.

**[just](https://github.com/casey/just)** gives short names to long commands. The [`justfile`](https://github.com/rendercv/rendercv/blob/main/justfile) lists them: `just test` runs the tests with exactly the options the maintainers use, so nobody has to remember those options.

Install each one with its official guide: [Git](https://git-scm.com/install/), [uv](https://docs.astral.sh/uv/getting-started/installation/), [just](https://github.com/casey/just#installation).

## Setting up the development environment

1. Download the repository, which is the project's files together with their history:

    ```bash
    git clone https://github.com/rendercv/rendercv.git
    cd rendercv
    ```

2. Install everything the project needs:

    ```bash
    just sync
    ```

    This creates a **virtual environment** in the `.venv` folder: a Python installation that belongs only to this project, with its packages. The file `uv.lock` names the exact version of every package, so your environment matches every other contributor's. [Project Management](project_management.md) explains how.

3. Check that everything works:

    ```bash
    just test
    ```

4. Tell your editor to use that environment, so it can find the packages. In Visual Studio Code, press `Ctrl+Shift+P`, run `Python: Select Interpreter`, and choose the one in `./.venv`.

Run commands from the repository folder. The `just` commands go through `uv run`, which uses `.venv` automatically, so you never need to activate it.

## Available commands

### Development

- `just sync`: install the exact package versions listed in `uv.lock`
- `just lock`: update `uv.lock` after changing the dependencies in `pyproject.toml`
- `just format`: lay out the code consistently and apply Ruff's automatic fixes
- `just format-file <path>`: do the same for one file
- `just check`: run every check: code problems, layout, types, spelling, and configuration files

### Testing

- `just test`: run the tests
- `just test-coverage`: run the tests and report which lines of code they ran
- `just update-testdata`: accept new rendered output as the expected output (see [Testing](testing.md))

### Documentation

- `just serve-docs`: preview the documentation website on your computer; it updates as you edit
- `just build-docs`: build the documentation website

### Generated files

- `just update-schema`: regenerate the schema that editors use to check CV files (see [JSON Schema](json_schema.md))
- `just update-examples`: regenerate the example CVs
- `just update-entry-figures`: regenerate the entry pictures in the user guide
- `just download-typst-packages`: download the Typst packages that RenderCV ships
- `just create-executable`: build a single program file that runs without Python

### Utilities

- `just count-lines`: count the lines of Python code in `src/`
