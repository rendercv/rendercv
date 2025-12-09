# Development:
sync:
  uv sync --frozen --all-extras

format:
  uv run --frozen black src tests
  uv run --frozen ruff check --fix src tests
  uv run --frozen ruff format src tests

format-file target:
  uv run --frozen black {{target}}
  uv run --frozen ruff check --fix {{target}}
  uv run --frozen ruff format {{target}}

check:
  uv run --frozen ruff check src tests
  uv run --frozen pyright src tests
  uv run --frozen pre-commit run --all-files

lock:
  uv lock

# Testing:
test:
  uv run --frozen pytest

update-testdata:
  uv run --frozen pytest --update-testdata

test-coverage:
  uv run --frozen pytest --cov=src/rendercv --cov-report=term --cov-report=html --cov-report=markdown

# Docs:
build-docs:
  uv run --frozen mkdocs build --clean --strict

serve-docs:
  uv run --frozen mkdocs serve --watch-theme

# Scripts:
update-schema:
  uv run --frozen scripts/update_schema.py

update-entry-figures:
  uv run --frozen --all-groups scripts/update_entry_figures.py

update-examples:
  uv run --frozen scripts/update_examples.py

create-executable:
  uv run --frozen --all-groups scripts/create_executable.py

# Utilities:
count-lines:
  wc -l `find src -name '*.py'`
