---
toc_depth: 3
---

# Project Management

## What is "Project Management"?

When you look at RenderCV's repository, you see:

```
.
├── src/                     ← The actual RenderCV code
├── pyproject.toml           ← Project configuration
├── justfile                 ← Command shortcuts
├── scripts/                 ← Supplementary Python scripts
├── .pre-commit-config.yaml  ← Pre-commit configuration
└── uv.lock                  ← Dependency lock file
```

**Project management is everything except `src/`.** It's all the infrastructure that lets us:

- Share RenderCV with users (`pip install rendercv`)
- Manage dependencies consistently
- Automate testing, building, and releases
- Ensure reproducibility across machines and time

## Why Can't We Just Write Python Code?

RenderCV is a Python project. The actual source code lives in `src/rendercv/`. Why do we need all these other files - `pyproject.toml`, `uv.lock`, `justfile`, `.github/workflows/`, etc.?

**Because code alone doesn't solve two critical problems: distribution and development environment.**

### Problem 1: Distribution

**How do users get your code?**

You could tell them "download these files, install dependencies with `pip install -r requirements.txt`, and run them with `python main.py`". But users want `pip install rendercv` and have it work instantly with `rendercv` command.

**This requires:** Packaging your code and uploading to [PyPI](https://pypi.org) (Python Package Index).

### Problem 2: Development Environment

You have the source code. Two developers want to contribute.

Developer A installs today with Python 3.11 and gets `pydantic==2.10`. Tests pass. Developer B installs one month later with Python 3.12 and gets `pydantic==2.11` which has breaking changes. Tests fail. "Works on A's machine" but not B's. B asks: "What formatter do you use? What settings? How do I run tests?"

**What needs to happen:** Everyone gets the same Python version, same package versions (locked, not "latest"), same development tools with same settings. All in one command.

**This requires:** Locking dependencies (Python version, every package, frozen in time), configuring all tools in one place, and automating setup so it's identical for everyone.

### The Solution

All those files you see in the repository (`pyproject.toml`, `uv.lock`, `justfile`, and more) work together to solve these problems. The result:

**For users:**
```bash
pip install rendercv
```

Works instantly. Every time. Anywhere. All dependencies installed automatically.

**For developers** ([Setup](index.md)):
```bash
just sync
```

One command. Identical environment for everyone: correct Python version, exact dependency versions, all dev tools ready. Works today, works in 2027. Bug from 6 months ago? Check out that commit, run `just sync`, exact environment recreated.

The rest of this guide explains what each file does.

## Files and Folders in the Root

### [`pyproject.toml`](https://github.com/rendercv/rendercv/blob/main/pyproject.toml)

The project definition file. This is the [standard way to configure a Python project](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).

This file defines:

- Project metadata (name, version, description)
- Dependencies (what packages RenderCV needs)
- Entry points (makes `rendercv` a command)
- Build configuration (how to package RenderCV)
- Tool settings (`ruff`, `pyright`, `pytest`, etc.)

Open the file to see the full configuration with detailed comments.

### [`justfile`](https://github.com/rendercv/rendercv/blob/main/justfile)

[just](https://github.com/casey/just) is a command runner, a tool that lets you define terminal commands in a file and run them easily.

**Why do we need it?** During development, you constantly run commands like "run tests with coverage", "format all code", "build and serve docs". Without standardization:

- Everyone types different commands with different options
- You have to remember long command strings

The `justfile` solves this: define each command once, and everyone runs the same thing:

```bash
just test           # Runs pytest with the right options
just format         # Formats code with ruff
just serve-docs     # Builds and serves documentation locally
just update-schema  # Regenerates schema.json
```

### [`scripts/`](https://github.com/rendercv/rendercv/tree/main/scripts)

Python scripts that automate some repetitive tasks that are not part of RenderCV's functionality.

**Why do we need it?** Some tasks need to be done repeatedly but are too complex for simple shell commands:

- `update_schema.py`: Generate `schema.json` (see [JSON Schema](json_schema.md) for more details) from pydantic models
- `update_examples.py`: Regenerate all example YAML files and PDFs in [`examples/`](https://github.com/rendercv/rendercv/tree/main/examples) folder
- `create_executable.py`: Build standalone executable of RenderCV

These scripts are called by `just` commands (`just update-schema`, `just update-examples`, etc.).

### [`.pre-commit-config.yaml`](https://github.com/rendercv/rendercv/blob/main/.pre-commit-config.yaml)

Configuration file for [`pre-commit`](https://pre-commit.com/), a tool that runs code quality checks.

**Why do we need it?** Pre-commit's value is **fast CI/CD**. [pre-commit.ci](https://pre-commit.ci/) (free for open-source projects) automatically checks if the source code has any `ruff` or `pyright` errors on every push and pull request. Forgot to format your code? The workflow fails, making it immediately obvious.

### [`uv.lock`](https://github.com/rendercv/rendercv/blob/main/uv.lock)

A dependency lock file. This is a record of the exact version of every package RenderCV uses (including dependencies of dependencies of dependencies...).

**Why do we need it?** Remember development environment problem? This file solves it. When you run `just sync`, `uv` reads this file and installs the exact same versions everyone else has, not "the latest version", but "the exact version that's known to work". Without this file, developers would get different package versions and environments would drift apart.

**Never edit this manually.** Use `just lock` to update it. **Always commit it to git.** That's how everyone gets identical environments.

## Learn More

See the [`uv` documentation](https://docs.astral.sh/uv/) for more information on project management.
