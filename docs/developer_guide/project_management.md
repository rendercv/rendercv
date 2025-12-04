---
toc_depth: 3
---

# Project Management

This guide explains how RenderCV is managed as a Python project - why we need more than just Python code, and how all the pieces fit together.

## What is "Project Management"?

When you look at RenderCV's repository, you see:

```
.
├── src/           ← The actual RenderCV code
├── tests/         ← Tests for that code
├── docs/          ← Documentation
├── .github/       ← CI/CD automation
├── pyproject.toml ← Project configuration
├── justfile       ← Command shortcuts
└── ...many other files
```

**Project management is everything except `src/`.** It's all the infrastructure that lets us:

- Share RenderCV with users (`pip install rendercv`)
- Manage dependencies consistently
- Automate testing, building, and releases
- Ensure reproducibility across machines and time

## Why Can't We Just Write Python Code?

Imagine RenderCV is just Python files in `src/`. You want to share it. Here's what breaks:

### Problem 1: Distribution

**How do users get your code?**

You could tell them "download these files and run them". But users want `pip install rendercv` and have it work instantly.

**This requires:** Packaging your code and uploading to [PyPI](https://pypi.org) (Python Package Index).

### Problem 2: Dependencies

RenderCV uses `pydantic`, `jinja2`, `typer`, and more. Without them, it doesn't work.

You could tell users "install these packages...". But which versions? How do you ensure everyone has compatible versions?

**This requires:** Declaring dependencies so pip installs them automatically.

### Problem 3: Reproducibility

- Developer A installs today, gets `pydantic==2.10`
- Developer B installs next month, gets `pydantic==2.11` with a breaking change
- Code works on A's machine, breaks on B's machine
- User reports a bug from 6 months ago - how do you recreate their environment?

**This requires:** Locking exact versions of every package.

### The Solution

Look at the [Setup](index.md) instructions:

1. Install two tools: `uv` and `just`
2. Clone the repository
3. Run `just sync`

**That's it.** You're ready to develop RenderCV.

With one command, you get:

- The correct Python version installed automatically
- Every dependency installed at the exact same version as every other developer
- A reproducible environment identical to what CI/CD uses
- All development tools configured and ready

**This works today. It will work next month. It will work in 2027.**

Developer A in California and Developer B in Tokyo get identical environments. A bug reported from 6 months ago? Check out that commit and run `just sync` - you have the exact environment from back then.

**How is this possible?** All those files you see in the repository - `pyproject.toml`, `uv.lock`, `justfile`, and more - work together to make this happen. They're the infrastructure that lets us solve distribution, dependency management, and reproducibility with one command.

The rest of this guide explains what each file does and how they fit together.

## Files and Folders in the Root

This section explains each file and folder you see in RenderCV's root directory.

### [`pyproject.toml`](https://github.com/rendercv/rendercv/blob/main/pyproject.toml)

**What is it?** The project definition file - the standard way to configure a Python project.

This file defines:

- Project metadata (name, version, description)
- Dependencies (what packages RenderCV needs)
- Optional dependencies (CLI tools that only work outside web environments)
- Entry points (makes `rendercv` a command)
- Build configuration (how to package RenderCV)
- Tool settings (ruff, pyright, pytest, etc.)

Open the file to see the full configuration with detailed comments.

### [`uv.lock`](https://github.com/rendercv/rendercv/blob/main/uv.lock)

**What is it?** A dependency lock file - a record of the exact version of every package RenderCV uses (including dependencies of dependencies).

**Why do we need it?** Remember Problem 3 (reproducibility)? This file solves it. When you run `just sync`, uv reads this file and installs the exact same versions everyone else has - not "the latest version", but "the exact version that's known to work". Without this file, developers would get different package versions and environments would drift apart.

**Never edit this manually** - uv generates and updates it automatically. **Always commit it to git** - that's how everyone gets identical environments.

### [`justfile`](https://github.com/rendercv/rendercv/blob/main/justfile)

**What is it?** [just](https://github.com/casey/just) is a command runner - a tool that lets you define terminal commands in a file and run them easily.

**Why do we need it?** During development, you constantly run commands like "run tests with coverage", "format all code", "build and serve docs". Without standardization:

- Everyone types different commands with different options
- You have to remember long command strings

The `justfile` solves this - define each command once, and everyone runs the same thing:

```bash
just test           # Runs pytest with the right options
just format         # Formats code with ruff
just serve-docs     # Builds and serves documentation locally
just update-schema  # Regenerates schema.json
```

This is why `just sync` works so elegantly - it's a standardized command that does exactly the same thing for everyone.

### [`.pre-commit-config.yaml`](https://github.com/rendercv/rendercv/blob/main/.pre-commit-config.yaml)

**What is it?** Configuration file for [pre-commit](https://pre-commit.com/) - a tool that runs code quality checks.

**Why do we need it?** We already have ruff for formatting - pre-commit's value is **fast CI/CD**. [pre-commit.ci](https://pre-commit.ci/) (free for open-source projects) automatically runs checks on every push and pull request. Forgot to format your code? The workflow fails, making it immediately obvious. Without pre-commit, we'd have to set up our own workflow to run these checks.

Run `just check` locally to check your code before committing. We don't use pre-commit as git hooks (that run before every commit) - we prefer manual checks when ready.

### [`docs/`](https://github.com/rendercv/rendercv/tree/main/docs) and [`mkdocs.yaml`](https://github.com/rendercv/rendercv/blob/main/mkdocs.yaml)

**The problem:** We want documentation on a website (`https://docs.rendercv.com`), not just Markdown files in a repository.

**The solution:** [MkDocs](https://www.mkdocs.org/) - a tool that converts Markdown files into a static website (HTML/CSS files we can host).

See [Documentation](documentation.md) for details on how documentation works in RenderCV.

### [`schema.json`](https://github.com/rendercv/rendercv/blob/main/schema.json)

**What is it?** A [JSON Schema](https://json-schema.org/) - a standard way to describe the structure and validation rules of JSON/YAML files.

**Why do we need it?** For great user experience. When users edit RenderCV YAML files in VS Code, they get:

- Autocomplete for field names
- Inline documentation for each field
- Real-time validation errors

**How?** VS Code reads `schema.json` to understand what fields are allowed, what types they should be, and what they mean.

**Where it comes from:** Auto-generated from RenderCV's pydantic models with `just update-schema`. The pydantic models define the structure, and we export them to JSON Schema format that VS Code understands.


### [`tests/`](https://github.com/rendercv/rendercv/tree/main/tests)

**What is it?** Automated tests that verify RenderCV works correctly.

**Why do we need it?** You could manually test every feature after each change - but that's impossible for large projects. Without automated tests, every change is risky because you can't verify everything still works. Tests let you confidently modify code, knowing that if tests pass, the core functionality still works. They also document expected behavior through examples.

Run with `just test`. See [Testing](testing.md) for details on how testing works in RenderCV.

### [`scripts/`](https://github.com/rendercv/rendercv/tree/main/scripts)

**What is it?** Python scripts that automate project maintenance tasks.

**Why do we need it?** Some tasks need to be done repeatedly but are too complex for simple shell commands:

- `update_schema.py` - Generate `schema.json` from pydantic models
- `update_examples.py` - Regenerate all example PDFs when renderer changes
- `create_executable.py` - Build standalone executable for releases

These scripts are called by `just` commands (`just update-schema`, `just update-examples`, etc.).

### [`.github/workflows/`](https://github.com/rendercv/rendercv/tree/main/.github/workflows)

**What is it?** GitHub Actions workflow files - automation scripts that run on GitHub's servers.

**Why do we need it?** Manual processes don't scale - someone has to remember to run tests, build docs, publish releases, etc. GitHub Actions automates all of this. Every push runs tests. Every commit to `main` deploys documentation. Every release publishes to PyPI. It happens automatically, consistently, without human intervention.

See [CI/CD](ci_cd.md) for details.

## Key Takeaways

**Project management is everything outside `src/`** - the infrastructure that makes RenderCV a complete Python project.

**The goal:** Make it easy to write, test, document, package, and share Python code that works reliably for everyone.

**To learn more:** See [uv documentation](https://docs.astral.sh/uv/) for project management
