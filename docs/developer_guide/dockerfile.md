---
toc_depth: 2
---

# Docker

RenderCV needs Python, a dozen packages in particular versions, fonts, and Typst packages. Installing all of that differs between Windows, macOS, and Linux, and one small difference, such as an older Python or a missing font, can break rendering or change the PDF. Some people can't or don't want to install Python at all, and a server that renders CVs needs an installation that behaves the same every time.

[Docker](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/) solves this by shipping a program together with everything it needs, down to a minimal operating system. Anyone with Docker installed can run it, and it behaves the same on every computer. Three words describe how:

- An **image** is that shipment: a frozen copy of every file the program needs (a small Linux system, Python, RenderCV, fonts), plus the command that starts the program. Once built, an image doesn't change.
- A **container** is one run of an image. Docker starts the program in a sealed-off space where it sees the image's files instead of your computer's, plus only the folders you choose to share. Every new container starts from the unchanged image, so nothing left behind by an earlier run can affect it.
- A **Dockerfile** is the recipe that builds the image, step by step: start from a small Linux with Python, install RenderCV, set the start command.

A container isn't a complete virtual computer. It runs on your computer's own operating system, which is why it starts in moments. On macOS and Windows, Docker runs a small Linux in the background for this.

## Running RenderCV in a container

RenderCV's image already contains Python, RenderCV, its fonts, and the Typst packages its themes use. What the container doesn't have is your CV, or a place to put the PDF. Sharing a folder solves both: a **bind mount** makes a folder on your computer appear inside the container, and files the container writes there appear on your computer.

From the folder that contains `Your_Name_CV.yaml`, on macOS or Linux:

```bash
docker run --rm -v "$PWD":/work \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -w /work \
  ghcr.io/rendercv/rendercv render Your_Name_CV.yaml
```

Piece by piece:

- `ghcr.io/rendercv/rendercv` names the image. Docker downloads it the first time. Everything after the name goes to RenderCV, exactly as if you had typed `rendercv render Your_Name_CV.yaml`.
- `-v "$PWD":/work` shares the current folder, which the container sees as `/work`.
- `-w /work` starts RenderCV in that folder, so it finds your file and writes `rendercv_output/` next to it.
- `--user "$(id -u):$(id -g)"` runs RenderCV as you. Operating systems record each file's owner as a number; without this option, files written on Linux would belong to the container's account instead of yours. `-e HOME=/tmp` gives that account a home folder it can write to.
- `--rm` deletes the container when RenderCV finishes. Your files remain because they were written to the shared folder.

Replace `render Your_Name_CV.yaml` with `new "Your Name"` to create a sample CV instead.

## How the image is built

The [`Dockerfile`](https://github.com/rendercv/rendercv/blob/main/Dockerfile) builds in two stages, called a **multi-stage build**. The first stage contains the tools for installing RenderCV; the second receives only the installed result. The installation tools stay out of the image that users download, which keeps it small.

The first stage installs the exact dependency versions from `uv.lock`, downloads the Typst packages, and installs RenderCV and its fonts from the repository. The second stage copies that installation and creates an account called `rendercv`, with user and group number 1000, so RenderCV doesn't run as the all-powerful `root` account. It then makes `rendercv` the command every container runs. Both stages use Python 3.15 on Debian, a Linux distribution.

Docker saves the result of each step and reuses it as long as that step's inputs haven't changed. That's why the Dockerfile installs the dependencies before copying RenderCV's own code: editing the code then reuses the slow installation step. `.dockerignore` lists files Docker shouldn't copy, such as `.venv` and build outputs. [uv's Docker guide](https://docs.astral.sh/uv/guides/integration/docker/) describes this pattern.

## Building and testing offline

The image promises that rendering works without downloading anything. To test that promise, build the image and render with the network switched off:

```bash
docker build -t rendercv:local .
mkdir -p docker-smoke
docker run --rm --network none -v "$PWD/docker-smoke":/work \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -w /work \
  rendercv:local new "Offline Test"
docker run --rm --network none -v "$PWD/docker-smoke":/work \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -w /work \
  rendercv:local render Offline_Test_CV.yaml
```

`docker build -t rendercv:local .` builds an image named `rendercv:local` from the current folder. Building needs the network, to download Python and the packages. `--network none` then cuts each container off from the network. If the PDF appears in `docker-smoke/rendercv_output/`, the image contains everything rendering needs. Two things still need the network by design: photos given as web addresses, and custom Typst code that imports other packages. The [test workflow](github_workflows.md#tests) runs this check on every proposed change.

## File ownership with Podman

The image's `rendercv` account has user and group number 1000. On Linux, if your own numbers are also 1000, you can leave out `--user`.

[Podman](https://podman.io/) is another program that runs the same images. It often runs **rootless**, meaning without administrator rights. In that mode it translates the account numbers inside a container into different numbers outside, so matching the numbers isn't enough. `keep-id` tells Podman to treat the container's `rendercv` account as you:

```bash
podman run --rm --network none --user rendercv \
  --userns=keep-id:uid=1000,gid=1000 \
  -v "$PWD":/work:Z -w /work \
  ghcr.io/rendercv/rendercv render Your_Name_CV.yaml
```

On Linux systems with SELinux, a security layer that restricts which files each program may touch, `:Z` labels the shared folder so the container may use it. Podman's [`--userns` documentation](https://docs.podman.io/en/latest/markdown/podman-run.1.html#userns-mode) has the details. You never need to make the folder writable by everyone.

## Publishing

A **registry** is an online store for images, as PyPI is for Python packages. When a release is published, the [release workflow](github_workflows.md#releases) builds the image and uploads it to GitHub Container Registry as `ghcr.io/rendercv/rendercv`. That's where `docker run` downloads it from.
