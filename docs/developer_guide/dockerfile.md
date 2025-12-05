---
toc_depth: 3
---

# Dockerfile

## What is Docker?

Docker lets software bring **its whole working setup** with it — almost like carrying a tiny, preconfigured computer inside a file. This setup (a *Docker image*) includes everything the app expects: the right Python version, the right libraries, and the right configuration. When you run that image, Docker creates a **container**, which is a temporary, isolated copy of that tiny computer running on your machine.

A helpful way to think about it: a Docker image is a **snapshot of a complete software environment**, frozen at a moment when everything works. A container is that snapshot *brought to life*. When you're done, you may delete it, and it leaves no trace.

## Why Docker Is Useful for RenderCV

If you have Python installed, RenderCV already installs easily with:

```bash
pip install rendercv
```

So Docker is **not** needed for most users. RenderCV provides a Docker image for people who want one of these things:

1. **Zero installation footprint** — no Python installation, no packages, no system changes.
2. **A guaranteed, known-good environment** — the exact same setup every time, on every machine.
3. **Freedom from system restrictions** — some computers block installing software but allow running containers.
4. **A clean workflow** — some users prefer tools to run in disposable containers rather than clutter their system.

In those cases, the Docker image is a ready-made snapshot that already contains the right Python version and RenderCV itself. You just run it:

```bash
docker run -v "$PWD":/work -w /work ghcr.io/rendercv/rendercv render Your_CV.yaml
```

## How the Image Gets Published

When you publish a GitHub release, the [`release.yaml` workflow](https://github.com/rendercv/rendercv/blob/main/.github/workflows/release.yaml) automatically builds and publishes the Docker image.

The image is published to GitHub Container Registry at `ghcr.io/rendercv/rendercv` with tags:

- `latest` - Most recent release
- Version tags - e.g., `v2.4`, `v2.4.1`

Users can then pull and run it:

```bash
docker run -v "$PWD":/work -w /work ghcr.io/rendercv/rendercv new "Your Name"
```

## Learn More

To learn more about writing `Dockerfile`, see the `uv`'s guide on [Docker](https://docs.astral.sh/uv/guides/integration/docker/).
