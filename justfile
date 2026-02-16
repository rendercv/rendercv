# Development:
sync:
  uv sync --frozen --all-extras --active

lock:
  uv lock

format:
  uv run --frozen --all-extras --active black src tests || true
  uv run --frozen --all-extras --active ruff check --fix src tests || true
  uv run --frozen --all-extras --active ruff format src tests

format-file target:
  uv run --frozen --all-extras --active black {{target}} || true
  uv run --frozen --all-extras --active ruff check --fix {{target}} || true
  uv run --frozen --all-extras --active ruff format {{target}}

check:
  uv run --frozen --all-extras --active ruff check src tests
  uv run --frozen --all-extras --active ty check src tests
  uv run --frozen --all-extras --active prek run --all-files

# Testing:
test:
  uv run --frozen --all-extras --active pytest

update-testdata:
  uv run --frozen --all-extras --active pytest --update-testdata

test-coverage:
  uv run --frozen --all-extras --active pytest --cov=src/rendercv --cov-report=term --cov-report=html --cov-report=markdown

# Docs:
build-docs:
  uv run --frozen --all-extras --active mkdocs build --clean --strict

serve-docs:
  uv run --frozen --all-extras --active mkdocs serve --watch-theme

# Scripts:
update-schema:
  uv run --frozen --all-extras --active scripts/update_schema.py

update-examples:
  uv run --frozen --all-extras --active scripts/update_examples.py

update-entry-figures:
  uv run --frozen --all-extras --active --group update-entry-figures scripts/update_entry_figures.py

create-executable:
  uv run --frozen --all-extras --active --no-default-groups --group create-executable scripts/create_executable.py

# Utilities:
count-lines:
  wc -l `find src -name '*.py'`
