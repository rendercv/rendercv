# rendercv-fonts

A Python package containing the fonts bundled with [RenderCV](https://rendercv.com).
Install it with `uv pip install rendercv-fonts`, or install `rendercv[full]` to get
the CLI, renderer, and fonts together. Python 3.12 or newer is required.

Since RenderCV 2.9, this package is maintained in
[`rendercv/rendercv`](https://github.com/rendercv/rendercv/tree/main/packages/rendercv-fonts).
The former `rendercv/rendercv-fonts` repository is retired after the 2.9 release;
please send issues and pull requests to the monorepo. Its full Git history and
authorship are preserved here.

## Python API

```python
import rendercv_fonts

rendercv_fonts.available_font_families  # Primary families offered as design choices
rendercv_fonts.path_of["Source Sans 3"]  # Path to a family's directory
rendercv_fonts.paths_to_font_folders  # List of directories for a font search path
rendercv_fonts.paths_to_font_files  # List of all .ttf and .otf paths
rendercv_fonts.links_to_font_files  # Corresponding raw GitHub download URLs
```

The lists use a stable alphabetical order. The download URLs point to this
version's release tag, `rendercv-fonts-v<version>`, so they never change. Local
font files require no network access.

## Development and releases

This is a uv workspace member. From the repository root, run:

```sh
uv sync --frozen --all-extras
uv run --frozen --all-extras pytest tests/rendercv_fonts
uv build --package rendercv-fonts
```

Tests live in `tests/rendercv_fonts`, mirroring `src/rendercv_fonts` in this
package. Formatting, type checking, and CI use the root configuration.

The fonts package has its own version, in `pyproject.toml` and
`src/rendercv_fonts/__init__.py`, and its own releases: pushing the tag
`rendercv-fonts-v<version>` publishes it to PyPI. RenderCV requires the version
it's tested with, so after raising the version, raise the minimum in the root
`pyproject.toml`'s `full` extra and run `uv lock`. See
[Releases](https://docs.rendercv.com/developer_guide/github_workflows/#releases).

## Licenses

The Python package is MIT licensed; see [LICENSE](LICENSE). Font files retain
their own licenses and notices alongside each font family.
