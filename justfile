# Development:
sync:
  uv sync --frozen --all-extras

lock:
  uv lock

format:
  uv run --frozen --all-extras ruff check --fix src packages tests scripts docs || true
  uv run --frozen --all-extras ruff format src packages tests scripts docs

format-file target:
  uv run --frozen --all-extras ruff check --fix {{target}} || true
  uv run --frozen --all-extras ruff format {{target}}

check:
  uv run --frozen --all-extras prek run --all-files

# Testing:
test:
  uv run --frozen --all-extras pytest

update-testdata:
  uv run --frozen --all-extras pytest --update-testdata

test-coverage:
  uv run --frozen --all-extras pytest --cov --cov-report=term --cov-report=html --cov-report=markdown

# Docs:
build-docs:
  uv run --frozen --all-extras zensical build --clean --strict

serve-docs:
  uv run --frozen --all-extras zensical serve

# Scripts:
update-schema:
  uv run --frozen --all-extras scripts/update_schema.py

update-examples:
  uv run --frozen --all-extras scripts/update_examples.py

update-entry-figures:
  uv run --frozen --all-extras scripts/update_entry_figures.py

download-typst-packages:
  uv run --frozen --all-extras --no-default-groups scripts/download_typst_packages.py

create-executable: download-typst-packages
  uv run --frozen --all-extras --no-default-groups --group create-executable scripts/create_executable.py

# Utilities:
count-lines:
  wc -l `find src -name '*.py'`
