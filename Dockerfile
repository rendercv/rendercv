# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.15-trixie-slim AS builder

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Use the same system interpreter as the runtime image.
ENV UV_PYTHON_DOWNLOADS=0

# Install the project's dependencies using the lockfile and settings
# This layer is cached separately from the project code for faster rebuilds
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-workspace --no-editable --extra full --no-default-groups

# Then, add the rest of the project source code and install it, with the Typst
# packages that it ships. Installing separately from its dependencies allows optimal
# layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv run --no-sync scripts/download_typst_packages.py \
 && uv sync --locked --no-editable --extra full --no-default-groups

# Final stage
FROM python:3.15-slim-trixie

# Setup a non-root user
RUN groupadd --gid 1000 rendercv \
 && useradd --gid 1000 --uid 1000 --create-home rendercv

# Set working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder --chown=rendercv:rendercv /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Use the non-root user to run our application
USER rendercv

# Set the entrypoint to the rendercv CLI (installed via pyproject.toml entry point)
ENTRYPOINT ["rendercv"]

# Default command shows help
CMD ["--help"]
