# Development:
sync:
  uv sync --frozen --all-extras

lock:
  uv lock

format:
  uv run --frozen --all-extras black src tests || true
  uv run --frozen --all-extras ruff check --fix src tests || true
  uv run --frozen --all-extras ruff format src tests

format-file target:
  uv run --frozen --all-extras black {{target}} || true
  uv run --frozen --all-extras ruff check --fix {{target}} || true
  uv run --frozen --all-extras ruff format {{target}}

check:
  uv run --frozen --all-extras ruff check src tests
  uv run --frozen --all-extras ty check src tests
  uv run --frozen --all-extras pre-commit run --all-files

# Testing:
test:
  uv run --frozen --all-extras pytest

update-testdata:
  uv run --frozen --all-extras pytest --update-testdata

test-coverage:
  uv run --frozen --all-extras pytest --cov=src/rendercv --cov-report=term --cov-report=html --cov-report=markdown

# Docs:
build-docs:
  uv run --frozen --all-extras mkdocs build --clean --strict

serve-docs:
  uv run --frozen --all-extras mkdocs serve --watch-theme

# Scripts:
update-schema:
  uv run --frozen --all-extras scripts/update_schema.py

update-examples:
  uv run --frozen --all-extras scripts/update_examples.py

update-entry-figures:
  uv run --frozen --all-extras --group update-entry-figures scripts/update_entry_figures.py

create-executable:
  uv run --frozen --all-extras --no-default-groups --group create-executable scripts/create_executable.py

# Utilities:
count-lines:
  wc -l `find src -name '*.py'`
