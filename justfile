# Development:
sync:
  uv sync --all-extras --all-groups

format:
  uv run --locked black src tests
  uv run --locked ruff check --fix src tests
  uv run --locked ruff format src tests

format-file target:
  uv run --locked black {{target}}
  uv run --locked ruff check --fix {{target}}
  uv run --locked ruff format {{target}}

check:
  uv run --locked ruff check src tests
  uv run --locked pyright src tests
  uv run --locked pre-commit run --all-files

# Testing:
test:
  uv run --locked pytest

update-testdata:
  uv run --locked pytest --update-testdata

test-coverage:
  uv run --locked pytest --cov=src/rendercv --cov-report=term --cov-report=html --cov-report=markdown

# Docs:
build-docs:
  uv run --locked mkdocs build --clean --strict

serve-docs:
  uv run --locked mkdocs serve --watch-theme

# Scripts:
update-schema:
  uv run --locked scripts/update_schema.py

update-entry-figures:
  uv run --locked scripts/update_entry_figures.py

update-examples:
  uv run --locked scripts/update_examples.py

create-executable:
  uv run --locked scripts/create_executable.py

# Utilities:
count-lines:
  wc -l `find src -name '*.py'`
