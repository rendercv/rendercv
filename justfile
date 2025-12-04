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

<<<<<<< HEAD
count-lines:
  wc -l `find src -name '*.py'`

=======
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

<<<<<<< HEAD
# Scipts
>>>>>>> ceea296 (Start working on new CLI)
=======
# Scripts:
>>>>>>> edab23f (Format, fix pre-commit errors)
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
<<<<<<< HEAD
  
src-tree:
  tree src/rendercv --gitignore
<<<<<<< HEAD

build-docs:
  uv run mkdocs build --clean --strict

serve-docs:
  uv run mkdocs serve

test:
  uv run pytest

test-with-coverage:
  uv run -- pytest --cov

report-coverage:
  uv run -- pytest --cov --cov-report=html

open video_path:
  uv run scripts/open.py {{video_path}}

profile target:
  sudo -E uv run py-spy record -o profile.svg python {{target}}

pull-data:
  uv run scripts/pull_data.py
=======
>>>>>>> ceea296 (Start working on new CLI)
=======
>>>>>>> 054905b (Start working on developer guide)
