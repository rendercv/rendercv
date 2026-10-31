---
toc_depth: 2
---

# GitHub Workflows

Some work has to happen every time something changes: run the tests when someone proposes a change, publish the packages when a version is released. Done by hand, it is slow and easily forgotten. [GitHub Actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions) does it automatically. When an **event** happens on GitHub, such as a pull request being opened, it starts fresh computers in GitHub's data centers and runs the commands we wrote down.

Those commands live in **workflows**: YAML files in [`.github/workflows/`](https://github.com/rendercv/rendercv/tree/main/.github/workflows) that say which events start them and what to do. A workflow is made of **jobs**, which run at the same time on separate machines unless one waits for another. Each job is a list of **steps**, such as downloading the code, installing dependencies, and running the tests.

Testing every proposed change automatically is called **continuous integration (CI)**. Reviewers see whether a change works on clean machines, not only on its author's computer. The workflows use the same `just` commands and the same locked versions as local development, so they check exactly what you can check yourself.

## Tests

[`test.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/test.yaml) runs for every pull request, every change to `main`, on request, and when another workflow calls it. It:

1. Runs the code checks (`just check`).
2. Runs the tests on Linux, Windows, and macOS, each with Python 3.12, 3.13, 3.14, and 3.15, recording coverage.
3. Combines the coverage of all those runs into one report and publishes it.
4. Builds the Docker image and renders a CV with the network switched off (see [Docker](dockerfile.md#building-and-testing-offline)).

The twelve combinations of operating system and Python version are called a **test matrix**. Running the same tests in each catches problems that appear only on one system, such as the backslashes Windows uses in file paths, or only with one Python version.

## Documentation

[`deploy-docs.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/deploy-docs.yaml) builds the documentation in strict mode for every pull request and every change to `main`. A change to `main` publishes it at docs.rendercv.com, and a pull request gets a preview at its own address. See [Documentation](documentation.md#publishing-and-previews).

## Executables

[`create-executables.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/create-executables.yaml) builds the [single-file programs](project_management.md#delivering-rendercv-to-users) with `just create-executable`, on request or as part of a release. An executable only runs on the kind of computer it was built for, so it is built four times: Linux on x86_64 and on ARM64, macOS on ARM64, and Windows on x86_64. x86_64 and ARM64 are the two common families of processors; most Windows computers use x86_64, and Macs with Apple chips use ARM64. The workflow saves the programs as **artifacts**, files a workflow keeps so that people or later jobs can download them.

## Releases

A GitHub **release** marks a version as published and holds its release notes and downloadable files. Publishing one starts [`release.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/release.yaml), which:

1. Runs the test workflow.
2. Builds RenderCV's wheel and source distribution, and the executables.
3. Attaches the wheel and the executables to the GitHub release.
4. Uploads the wheel and the source distribution to PyPI.
5. Publishes the AI agent skill.
6. Builds the Docker image and uploads it to GitHub Container Registry.

The release's tag, like `v2.9`, must be RenderCV's version.

The fonts package changes rarely and is many times larger than RenderCV, so it's released on its own, with its own version. Pushing a tag like `rendercv-fonts-v0.6.0` starts [`release-fonts.yaml`](https://github.com/rendercv/rendercv/blob/main/.github/workflows/release-fonts.yaml), which runs the tests and uploads that version of the fonts to PyPI:

```bash
git tag rendercv-fonts-v0.6.0
git push origin rendercv-fonts-v0.6.0
```

RenderCV requires the version of the fonts that it's tested with, and a test checks that `pyproject.toml` says so. Users get those fonts from PyPI, so before building, the release workflow checks that their version is released and that `packages/rendercv-fonts` hasn't changed since. To release new fonts with RenderCV, raise their version, release them, then release RenderCV.

PyPI accepts an upload only with proof that it comes from the project. Instead of a password stored in GitHub, which could leak, RenderCV uses **trusted publishing**: the project tells PyPI to accept uploads from one particular workflow, and GitHub vouches to PyPI for which workflow is running. The trusted publishers on PyPI name owner `rendercv`, repository `rendercv`, and environment `release`, with workflow `release.yaml` for `rendercv` and `release-fonts.yaml` for `rendercv-fonts`.

An **AI agent skill** is a set of instructions that teaches AI assistants how to use RenderCV. People install it from the [rendercv-skill](https://github.com/rendercv/rendercv-skill) repository, so that they don't have to download all of RenderCV for it. Step 5 runs [`scripts/rendercv_skill/generate.py`](https://github.com/rendercv/rendercv/blob/main/scripts/rendercv_skill/generate.py), which writes the skill from RenderCV's own schema, themes, locales, and commands, replaces that repository's contents with it, and attaches it to the release as `rendercv_skill.zip` for apps that install skills from a file. To change the skill, change the script or its templates here; to see the result, run it with a folder to write into:

```bash
uv run scripts/rendercv_skill/generate.py /tmp/rendercv-skill
```

Publishing on Typst Universe is separate; see [Publish the Typst Package](how_to/publish_typst_package.md).

## Issue and pull request assistance

Three workflows use Anthropic's Claude: one answers `@claude` requests, one reviews pull requests, and one triages new issues. They follow the same [contributing](contributing.md) and [testing](testing.md) guides as human contributors. They need the Claude GitHub App installed and the `ANTHROPIC_API_KEY` repository secret. Each workflow file defines what starts it and what it is allowed to do.

## Secrets

A **repository secret** is a value stored encrypted in the repository's settings, which workflows can use but nobody can read back. The workflows need three:

- `ANTHROPIC_API_KEY`, for the Claude workflows.
- `CLOUDFLARE_API_TOKEN`, a Cloudflare API token allowed to deploy the `rendercv-docs` Worker and its route, for the documentation.
- `RENDERCV_SKILL_DEPLOY_KEY`, the private half of a deploy key with write access to rendercv/rendercv-skill, for publishing the AI agent skill.
