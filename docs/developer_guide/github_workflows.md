---
toc_depth: 3
---

# GitHub Actions

## The Problem

Every software project has repetitive tasks that must run consistently:

- **On every update:** Run tests, redeploy documentation
- **On every release:** Run tests, update `schema.json` and examples, build executables for 4 platforms, build package, upload to PyPI, push Docker image

You could do these manually. But manual means:

- Forgetting steps ("Did I update `schema.json`? Did I build the Windows executable?")
- Wasted time ("Why am I doing the same 15 steps every release?")

**What if you could write down these tasks once, and have them run automatically every time?**

That's what **CI/CD (Continuous Integration/Continuous Deployment)** is. And **GitHub Actions** is GitHub's system for it.

## What are GitHub Actions?

GitHub actions are **automation scripts that run on GitHub's servers when certain events happen**.

You define them in `.github/workflows/*.yaml` files. Each file describes:

1. **When to run** - push to main? Pull request? New release?
2. **What to do** - Run tests? Build docs? Publish package?
3. **Where to run** - Linux? Windows? macOS? Multiple versions?

GitHub reads these files and executes them automatically when the triggering events occur.

**Why GitHub's servers?** Because you don't want to worry about it. Push your code, turn off your computer, you're done. GitHub handles the rest - running tests, deploying docs, building packages - without you having to keep your machine on or manually run anything.

## RenderCV's Workflows

RenderCV has 5 workflows. Each handles a specific automation task.

**How workflows start:** Every workflow begins the same way - clone the repository, install `uv`, install `just`, then run some `just` commands. This recreates the same environment you'd have locally (see [Setup](index.md)).

### 1. [`test.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/test.yaml) - Run Tests

**When it runs:**

- Every push to `main` branch
- Every pull request
- Manually (via GitHub UI)
- When called by other workflows

**What it does:**

1. Runs `just test-coverage` across **9 different environments** (3 operating systems × 3 Python versions: 3.12, 3.13, 3.14)
2. Combines all coverage reports and uploads them to show the coverage report

### 2. [`deploy-docs.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/deploy-docs.yaml) - Deploy Documentation

**When it runs:**

- Every push to `main` branch
- Manually (via GitHub UI)

**What it does:**

1. Builds the documentation website using `just build-docs`
2. Uploads it to GitHub Pages
3. Documentation is now live at https://docs.rendercv.com

### 3. [`update-files.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/update-files.yaml) - Update Generated Files

**When it runs:**

- Manually (via GitHub UI)
- When called by the release workflow

**What it does:**

1. Regenerates files derived from code:
   - `schema.json` using `just update-schema`
   - Example YAML files and PDFs in `examples/` folder using `just update-examples`
   - Entry figures using `just update-entry-figures`
2. Commits and pushes these changes to the repository

### 4. [`create-executables.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/create-executables.yaml) - Create Executables

**When it runs:**

- Manually (via GitHub UI)
- When called by the release workflow

**What it does:**

1. Builds standalone executables using `just create-executable` for 4 platforms:
   - Linux (x86_64 and ARM64)
   - macOS (ARM64)
   - Windows (x86_64)
2. Uploads executables as artifacts

These are single-file executables that users can download and run without installing Python.

### 5. [`release.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/release.yaml) - Publish a Release

**When it runs:**

- When a new GitHub release is published

**What it does:**

This is the complete release pipeline. It orchestrates everything:

1. **Run tests** - Calls `test.yaml` to ensure everything works
2. **Update files** - Calls `update-files.yaml` to regenerate schema/examples
3. **Build package** - Installs `uv`, builds Python wheel and source distribution using `uv build`
4. **Create executables** - Calls `create-executables.yaml` for all platforms
5. **Create GitHub release** - Downloads and uploads executables and wheel to the release
6. **Publish to PyPI** - Downloads and uploads package so users can `pip install rendercv`
7. **Publish Docker image** - Builds and pushes Docker image to GitHub Container Registry

## Learn More

- [GitHub Actions Documentation](https://docs.github.com/en/actions) - Official docs
- [`.github/workflows/`](https://github.com/rendercv/rendercv/tree/main/.github/workflows) - RenderCV's workflow files
