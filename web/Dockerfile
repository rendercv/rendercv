# The web editor: one image serving the frontend and the API on one origin.
#
# Not to be confused with the repository root's `Dockerfile`, which packages
# upstream RenderCV's command-line tool and has a different job entirely.
#
# Why one image rather than a frontend host plus an API host: the session
# cookie is `SameSite=Lax`, so a browser withholds it from any `fetch` to a
# different site. Split across two hosts, sign-in succeeds and the session is
# gone on the next request -- and no CORS setting fixes it, because CORS lets
# the request through while `SameSite` keeps the cookie back.
#
# **The build context is the repository root, not `web/`**, because the
# backend depends on the core as an editable path dependency and needs its
# source. The context must include the
# `src/rendercv/renderer/typst_fontawesome` submodule; without it every PDF
# render fails looking for `lib.typ`.
#
#     git submodule update --init --recursive
#     docker build -f web/Dockerfile -t rendercv-web .

# --- Stage 1: the frontend ------------------------------------------------
FROM node:22-slim AS frontend

WORKDIR /build

# Copied before the sources so the dependency layer survives edits to them.
COPY web/frontend/package.json web/frontend/package-lock.json ./
RUN npm ci

COPY web/frontend/ ./

# `build:wasm-assets` is deliberately not run. It assembles ~30 MB of
# Pyodide, fonts and a Typst wasm binary for the client-side preview, which
# is off by default (`isWasmPreviewEnabled`), and it shells out to
# `uv build` -- so running it here would mean putting the Python toolchain
# in this stage to produce something nobody has switched on. Turning that
# flag on in a deployment built this way gives a preview engine with no
# assets to load; see `web/README.md`.
RUN npm run build

# --- Stage 2: the backend, serving that build -----------------------------
FROM python:3.12-slim AS runtime

COPY --from=ghcr.io/astral-sh/uv:0.10.3 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

# The account is created before anything is copied so that every `COPY` can
# name it. The previous version copied as root and ran `chown -R` at the
# end, which cost 291 MB: changing a file's owner rewrites it into a new
# layer, so that one command duplicated nearly everything under `/app`.
RUN groupadd --system --gid 999 rendercv \
 && useradd --system --gid 999 --uid 999 --no-create-home rendercv

WORKDIR /app

# The core first: the backend declares it as an editable path dependency, so
# its source tree has to be here before `uv sync` runs.
COPY --chown=rendercv:rendercv pyproject.toml uv.lock README.md ./
COPY --chown=rendercv:rendercv src/ ./src/

# `GET /api/schema` reads this file from the repository root, and the four
# form editors are generated from what it returns. Left out of the image,
# the endpoint answers 500 and the whole form mode is dead -- which is easy
# to miss, because the editor opens in YAML mode and everything else works.
COPY --chown=rendercv:rendercv schema.json ./

# `README.md` is not documentation ballast here: the backend's
# `pyproject.toml` declares it as the package readme, so the build fails
# without it.
COPY --chown=rendercv:rendercv web/backend/pyproject.toml web/backend/uv.lock web/backend/README.md ./web/backend/
COPY --chown=rendercv:rendercv web/backend/alembic.ini ./web/backend/
COPY --chown=rendercv:rendercv web/backend/src/ ./web/backend/src/
COPY --chown=rendercv:rendercv web/backend/migrations/ ./web/backend/migrations/

WORKDIR /app/web/backend

# `--extra postgres` installs the psycopg driver. Without it the process
# dies at startup the moment `RENDERCV_WEB_DATABASE_URL` names Postgres,
# which is the intended configuration for anything deployed -- SQLite in a
# container is lost on every restart.
# `--no-cache` because the cache is of no use once the environment exists,
# and it stays in the image otherwise: 219 MB of the same wheels the
# `.venv` already holds. It costs nothing at build time either -- each
# build on the host starts from an empty cache regardless.
#
# `--chown` on the venv: `uv` runs as root here, and the app reads the
# environment as `rendercv`.
RUN uv sync --frozen --extra postgres --no-dev --no-cache \
 && chown -R rendercv:rendercv /app/web/backend/.venv

# Prove the schema is loadable rather than merely present: this runs the
# same function the endpoint runs, so a missing, truncated or unparsable
# file fails the build instead of the first person who opens the form.
RUN uv run --frozen --no-dev python -c \
    "from rendercv_web.schema import load_schema; load_schema()"

COPY --from=frontend --chown=rendercv:rendercv /build/build/ /app/web/frontend-build/

# Read by `rendercv_web.frontend`. Left unset, the backend serves the API
# only and every page 404s -- which is correct in development, where Vite
# serves the frontend and proxies `/api` here.
ENV RENDERCV_WEB_FRONTEND_DIR=/app/web/frontend-build \
    PATH="/app/web/backend/.venv/bin:$PATH"

# Nothing here needs root, and a container that drops it limits what a
# compromise of the render pipeline could reach. Following the root
# Dockerfile's lead. The account itself was created above, before the
# copies, so that no recursive `chown` is needed to hand `/app` over.
USER rendercv

# Render and most container hosts inject the port to listen on. The default
# matches the local dev backend, so `docker run -p 8000:8000` needs no
# arguments.
ENV PORT=8000
EXPOSE 8000

# Schema migrations run in the app's lifespan on startup, so there is no
# separate release command to forget.
CMD ["sh", "-c", "uvicorn rendercv_web.app:app --host 0.0.0.0 --port ${PORT}"]
