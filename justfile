format:
  uv run black src tests ; uv run ruff check --fix src tests ; uv run ruff format src tests

format-file target:
  uv run -- black {{target}}; uv run -- ruff check --fix {{target}}; uv run -- ruff format {{target}}

lint:
  uv run -- ruff check src tests

check-types:
  uv run -- pyright src tests

pre-commit:
  uv run -- pre-commit run --all-files

count-lines:
  wc -l `find src -name '*.py'`
  
update-schema:
  uv run scripts/update_schema.py

update-entry-figures:
  uv run scripts/update_entry_figures.py

update-examples:
  uv run scripts/update_examples.py

create-executable:
  uv run scripts/create_executable.py

profile-render-command:
  uv run -- python -m cProfile -o render_command.prof -m rendercv render examples/John_Doe_ClassicTheme_CV.yaml && snakeviz render_command.prof

src-tree:
  tree src/rendercv --gitignore

build-docs:
  uv run mkdocs build --clean --strict

serve-docs:
  uv run mkdocs serve

run-tests:
  uv run pytest

run-tests-coverage:
  uv run -- coverage run -m pytest

combine-coverage:
  uv run -- coverage combine

report-coverage:
  uv run -- coverage report && uv run -- coverage html --show-contexts

open video_path:
  uv run scripts/open.py {{video_path}}

profile target:
  sudo -E uv run py-spy record -o profile.svg python {{target}}

pull-data:
  uv run scripts/pull_data.py