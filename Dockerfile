# syntax=docker/dockerfile:1.7

ARG UID=1000
ARG GID=1000

FROM python:3.13-slim AS builder

WORKDIR /build

RUN python -m venv /opt/rendercv-venv \
    && /opt/rendercv-venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/rendercv-venv/bin/pip install --no-cache-dir "rendercv[full]"

FROM python:3.13-slim

ARG UID
ARG GID

RUN groupadd --gid ${GID} rendercv \
    && useradd --uid ${UID} --gid ${GID} --create-home rendercv

COPY --from=builder /opt/rendercv-venv /opt/rendercv-venv

ENV PATH="/opt/rendercv-venv/bin:${PATH}"

WORKDIR /rendercv

USER rendercv:rendercv

ENTRYPOINT ["/bin/bash"]

