# Setup

## Prerequisites

You need two tools to develop RenderCV:

- **[uv](https://docs.astral.sh/uv/)**: Package and project manager. RenderCV uses uv to manage dependencies. It also handles Python installations, so you don't need to install Python separately.
- **[just](https://github.com/casey/just)**: Command runner. Development commands are defined in the `justfile`, and you need just to run them.

Install them by following their official installation guides:

- [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Install just](https://github.com/casey/just#installation)

## Setting Up the Development Environment

1. Clone the repository:

    ```bash
    git clone https://github.com/rendercv/rendercv.git
    ```

    and change to the repository directory:

    ```bash
    cd rendercv
    ```

2. Set up the development environment:

    ```bash
    just sync
    ```

    This command will:
    - Create a virtual environment (if it doesn't exist)
    - Install all dependencies including optional dependencies (`[full]`) and all development groups (`dev`, `docs`, `exe`)

3. Run `just test` to verify all tests pass and everything is set up correctly.

That's it! You're now ready to start developing RenderCV. 

## Available Commands

RenderCV uses `just` as a command runner. Here are the available commands:

### Development

- `just sync` - Sync all dependencies (including extras and dev groups)
- `just format` - Format code with black and ruff
- `just check` - Run all checks (ruff, pyright, pre-commit)

### Testing

- `just test` - Run tests with pytest
- `just test-coverage` - Run tests with coverage report
- `just update-testdata` - Update test data files (see [Testing](testing.md) for more details)

### Documentation

- `just build-docs` - Build documentation
- `just serve-docs` - Serve documentation locally with live reload

### Scripts

- `just update-schema` - Update JSON schema
- `just update-entry-figures` - Update entry figures for documentation
- `just update-examples` - Update example files
- `just create-executable` - Create standalone executable

### Utilities

- `just count-lines` - Count lines of Python code in the `src/` directory
