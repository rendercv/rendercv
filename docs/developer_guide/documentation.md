---
toc_depth: 2
---

# Documentation

This website is written as Markdown files in `docs/`. Plain text is easy to edit and review, but a browser needs HTML pages with styles, navigation, and search. A **static site generator** bridges the two: it converts the text files into a complete website once, ahead of time. RenderCV uses [Zensical](https://zensical.org/docs/). The result is a folder of ordinary files that any web host can serve; Cloudflare serves ours at [docs.rendercv.com](https://docs.rendercv.com).

## Previewing and building

```bash
just serve-docs
just build-docs
```

`just serve-docs` shows the site at `http://localhost:8000`, an address that points to your own computer, and refreshes it as you edit. `just build-docs` writes the whole site to `site/`. It runs in strict mode, where any warning, such as a broken link, fails the build, so mistakes are caught before the site is published.

## Configuration and appearance

[`zensical.toml`](https://github.com/rendercv/rendercv/blob/main/zensical.toml) defines the navigation, the Markdown extensions, the site's details, and Zensical's modern theme. Add each new page to its `project.nav` list.

The **theme** decides how every page looks, and it is built from [templates](understanding_rendercv.md#assembling-a-document-with-templates). An **override** is our own file that replaces one of the theme's templates. Overrides give us control, but each one has to be updated whenever Zensical changes the template it replaces, so keep them few and small. Brand colors, sidebar styling, and the logo animation live in `docs/assets/`, and custom icons in `docs/overrides/.icons/`. The header, tabs, and logo use Zensical's own templates.

The only template override, `toc-item.html`, limits how many heading levels a page's table of contents lists, using the page's `toc_depth` setting. That setting goes in the **front matter**, a small YAML block between `---` lines at the top of a page; `toc_depth: 2` lists headings down to the second level.

When changing an override, compare it with the matching template in [Zensical UI](https://github.com/zensical/ui). Zensical's templates use MiniJinja, a smaller variant of Jinja, so use its own filters and tests rather than Python methods. Follow the [customization guide](https://zensical.org/docs/customization/), and after upgrading Zensical check navigation on desktop and mobile, search, and both color schemes.

## Generated content

Some pages show information that already lives in RenderCV's code, such as the list of themes or a field's default value. A hand-written copy would fall out of date. The **macros extension** lets a page run Python while the site is built: `zensical.extensions.macros` loads [`docs/docs_templating.py`](https://github.com/rendercv/rendercv/blob/main/docs/docs_templating.py), which reads defaults and examples straight from RenderCV, so adding a theme updates the theme list by itself. These insertions use their own delimiters, which `zensical.toml` sets, so they can't be confused with the Jinja examples shown on the pages. If an insertion fails, the build fails.

The [API Reference](../api_reference/index.md) describes RenderCV's Python functions and classes. Its text comes from **docstrings**, the descriptions written at the start of each function and class. The `zensical.extensions.mkdocstrings` extension turns them into pages, and Zensical's `api-autonav` plugin creates a page for each module. To change the reference, edit the docstrings.

The [entry pictures](../user_guide/yaml_input_structure/cv.md) in the user guide come from `docs/user_guide/sample_entries.yaml`. `just update-entry-figures` renders each entry directly to PNG with Typst, on a page sized to fit the entry, so no cropping or image conversion is needed.

## Publishing and previews

Cloudflare serves the site from a **Worker**, a program on Cloudflare's servers that answers the requests for a web address. Ours runs no code of its own: [`wrangler.toml`](https://github.com/rendercv/rendercv/blob/main/wrangler.toml) tells Cloudflare to answer requests for `docs.rendercv.com` with the files in `site/`, and Wrangler, Cloudflare's command-line tool, uploads them.

[The documentation workflow](https://github.com/rendercv/rendercv/blob/main/.github/workflows/deploy-docs.yaml) builds the site for every pull request and every change to `main`. A change to `main` replaces the published site. A pull request gets a **preview**: the site with its changes, at an address of its own that the workflow posts as a comment and updates with every push. Closing the pull request deletes the preview. Previews are public, like the repository, and ask search engines not to index them.

Uploading needs `CLOUDFLARE_API_TOKEN`, a [repository secret](github_workflows.md#secrets) allowed to deploy the Worker. GitHub doesn't give secrets to pull requests from forks or from Dependabot, so their documentation is only built, which still catches its mistakes.
