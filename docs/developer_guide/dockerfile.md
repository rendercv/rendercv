---
toc_depth: 3
---

# Dockerfile

## What is Docker?

Docker lets software carry **its entire working environment** with it: the right language runtime, libraries, and configuration, all bundled into a single file called an *image*. Think of an image as a **frozen filesystem where everything is already installed and configured correctly**.

When you run an image, Docker creates a **container**: a live, isolated instance of that environment running on your machine. When you're done, you can delete it without a trace. Your actual system stays untouched.

## Why Docker Is Useful for RenderCV

## Why Docker for RenderCV?

RenderCV installs easily with `pip install rendercv` if you have Python. Most users don't need Docker.

But Docker makes sense if you want:

- **No installation at all** — no Python, no packages, nothing added to your system
- **A reproducible environment** — the exact same setup on every machine, every time
- **To bypass restrictions** — some systems block software installation but allow containers

The RenderCV Docker image is a ready-made environment with Python and RenderCV pre-installed. Just run:
```bash
docker run -v "$PWD":/work -w /work ghcr.io/rendercv/rendercv render Your_CV.yaml
```

## How the Image Gets Published

Docker images are stored in **registries**, which are servers that host images so anyone can download and run them. Docker Hub is the most popular, but GitHub has its own called GitHub Container Registry (GHCR).

When you publish a GitHub release, the [`release.yaml` workflow](https://github.com/rendercv/rendercv/blob/main/.github/workflows/release.yaml) automatically builds and publishes the RenderCV image to GHCR at `ghcr.io/rendercv/rendercv`.

When users run `docker run ghcr.io/rendercv/rendercv`, Docker automatically pulls the image from the registry if it's not already on their machine.

## Learn More

To learn more about writing `Dockerfile`, see the `uv`'s guide on [Docker](https://docs.astral.sh/uv/guides/integration/docker/).
