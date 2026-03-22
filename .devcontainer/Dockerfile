FROM mcr.microsoft.com/devcontainers/base:debian
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
