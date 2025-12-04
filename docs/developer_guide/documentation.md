---
toc_depth: 3
---

# Documentation

This guide explains how RenderCV's documentation works - from Markdown files in the repository to the website at `https://docs.rendercv.com`.

## The Goal: Documentation as a Website

**The problem:** We want documentation accessible on a website, not just Markdown files buried in a repository.

**The solution:** Convert Markdown files into a static website (HTML, CSS, JavaScript files) and host it somewhere.

A static website is just a collection of HTML, CSS, and JavaScript files that can be served to users. Since these files don't change dynamically (no databases, no server-side logic), they can be hosted almost anywhere, often for free.

**How RenderCV does it:**

1. Write documentation as Markdown files in `docs/`
2. Use **MkDocs** to convert those Markdown files into a beautiful website
3. Deploy the generated website to **GitHub Pages** (free static hosting)
4. Access it at `https://docs.rendercv.com`

## What is MkDocs?

[MkDocs](https://www.mkdocs.org/) is a tool that takes Markdown files and generates a static website from them.

**Input:** Markdown files + configuration file
**Output:** HTML, CSS, and JavaScript files ready to host

**Why not just put Markdown files online?** Markdown files are readable, but they lack:
- Navigation (sidebar, search)
- Theming (colors, fonts, responsive design)
- Features (code highlighting, tabs, admonitions)

MkDocs gives us all of this automatically.

Raw MkDocs is functional but basic. We use [**MkDocs Material**](https://squidfunk.github.io/mkdocs-material/) - a professional, feature-rich theme.

## Configuration: `mkdocs.yaml`

[`mkdocs.yaml`](https://github.com/rendercv/rendercv/blob/main/mkdocs.yaml) configures how MkDocs builds the website. It defines:

- **Site metadata** (name, description, repository link)
- **Theme settings** (Material theme, colors, fonts, features)
- **Navigation structure** (sidebar menu)
- **Markdown extensions** (code highlighting, tabs, admonitions)
- **Plugins** (search, API reference generation, macros)

Open `mkdocs.yaml` to see the full configuration. Most of it is self-explanatory with comments.

## Working with Documentation Locally

To see how your changes look on the website:

1. Run
    ```
    just serve-docs
    ```
2. Open `http://127.0.0.1:8000` in your browser
3. Edit Markdown files in `docs/`
4. See changes instantly in the browser

Press `Ctrl+C` to stop the server.

### Building the Documentation Website

To generate the final HTML/CSS/JavaScript files:

```bash
just build-docs
```

This creates a `site/` directory with the complete website:

This is mainly for CI/CD (GitHub Actions) when deploying to production. Use `just serve-docs` for development.

## How Documentation Gets Deployed

Every time you push to the `main` branch, GitHub Actions automatically builds and deploys the documentation.

### The Deployment Workflow

See [`.github/workflows/deploy-docs.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/deploy-docs.yaml):

1. **Trigger:** Runs on every push to `main`
2. **Build step:**
   - Installs dependencies (`uv`, `just`)
   - Runs `just build-docs` to generate the website
   - Uploads the `site/` directory as an artifact
3. **Deploy step:**
   - Takes the uploaded artifact
   - Deploys it to GitHub Pages
   - Makes it available at `https://docs.rendercv.com`

**GitHub Pages** is GitHub's free static website hosting service. Any repository can host static files (HTML, CSS, JavaScript) and get a public URL.

**Result:** Anything you add to `docs/` and push to `main` automatically appears on `https://docs.rendercv.com` within minutes.

## Special Features

### API Reference (Auto-Generated)

The API Reference section is **automatically generated from code docstrings**, not manually written Markdown files.

**How it works:**

1. The `mkdocstrings` plugin reads Python source code
2. Extracts docstrings from functions, classes, and modules
3. Generates beautiful API documentation pages

See the configuration in `mkdocs.yaml` under `plugins: mkdocstrings`. As long as you write good docstrings in the code, the API reference stays up-to-date automatically.

### Entry Type Figures

The [YAML Input Structure](../user_guide/yaml_input_structure.md) page shows visual examples of each entry type (EducationEntry, ExperienceEntry, etc.) for each theme.

These images are generated automatically by rendering sample entries and converting them to PNG.

**To update these figures:**

```bash
just update-entry-figures
```

**When to run this:** After changing entry rendering logic or adding new themes/entry types.

### Macros and Templating

The `mkdocs-macros-plugin` lets us use variables and logic in Markdown files.

See `docs/docs_templating.py` for custom functions available in documentation. This is used sparingly - most documentation is just plain Markdown.

## Key Takeaways

**Documentation is just Markdown files in `docs/`** that get converted to a website and deployed automatically.

**Local development workflow:**
1. Run `just serve-docs`
2. Edit Markdown files in `docs/`
3. Preview changes at `http://127.0.0.1:8000`

**Deployment is automatic** - push to `main` and GitHub Actions handles the rest.

**To learn more:** See [Material theme documentation](https://squidfunk.github.io/mkdocs-material/).
