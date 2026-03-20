---
name: rendercv-development-context
description: RenderCV codebase architecture, source code standards, and project references. Use when writing or reviewing RenderCV code.
---

# RenderCV Development Context

## Codebase references

- @docs/developer_guide/understanding_rendercv.md
- @docs/developer_guide/testing.md
- @docs/developer_guide/json_schema.md
- @src/rendercv/schema/
- @src/rendercv/renderer/
- @src/rendercv/cli/
- @tests/
- @pyproject.toml
- @justfile

## How-to guides

- @docs/developer_guide/how_to/add_theme.md
- @docs/developer_guide/how_to/add_locale.md
- @docs/developer_guide/how_to/add_social_network.md

## Source code standards

### Type annotations

Every function, variable, and class attribute must be strictly typed. No exceptions.

Use modern Python 3.12+ syntax:

- Type aliases with `type` statement
- PEP 695 type parameters (`[T]`, `[**P]`)
- Pipe unions (`str | int`, not `Union[str, int]`)
- Proper optional types (`str | None`, not `Optional[str]`)

### Linting and type checking

Always run `just check` and `just format` before committing. `just check` must show **zero errors**:

```bash
just format
just check
```

If there's absolutely no alternative, use `# ty: ignore[error-code]` or `#NOQA: error-code` to ignore typing or linting errors.

### Docstrings

Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings). Include a **"Why" section** and **"Example" section** when it adds value:

```python
def resolve_relative_path(
    path: pathlib.Path, info: pydantic.ValidationInfo, must_exist: bool = True
) -> pathlib.Path:
    """Convert relative path to absolute path based on input file location.

    Why:
        Users reference files like `photo: profile.jpg` relative to their CV
        YAML. This validator resolves such paths to absolute form and validates
        existence, enabling file access during rendering.

    Args:
        path: Path to resolve (may be relative or absolute).
        info: Validation context containing input file path.
        must_exist: Whether to raise error if path doesn't exist.

    Returns:
        Absolute path.
    """
```

Docstring order:

1. Brief description (one line)
2. Why section (when it adds value)
3. Example section (when it adds value)
4. Args section (mandatory)
5. Returns section (mandatory)
6. Raises section (mandatory if function raises exceptions)
