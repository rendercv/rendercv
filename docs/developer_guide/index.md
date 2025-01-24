# Developer Guide

All contributions to RenderCV are welcome!

The source code is thoroughly documented and well-commented, making it an enjoyable read and easy to understand. A detailed documentation of the source code is available in the [API reference](../reference/index.md).


## Getting Started

There are two ways of developing RenderCV: [locally](#develop-locally) or [with GitHub Codespaces](#develop-with-github-codespaces).

### Develop Locally

1. Install [Hatch](https://hatch.pypa.io/latest/). The installation guide for Hatch can be found [here](https://hatch.pypa.io/latest/install/#installation).
   
    Hatch is a Python project manager. It mainly allows you to define the virtual environments you need in [`pyproject.toml`](https://github.com/rendercv/rendercv/blob/main/pyproject.toml). Then, it takes care of the rest. Also, you don't need to install Python. Hatch will install it when you follow the steps below.

2. Clone the repository.
    ```
    git clone https://github.com/rendercv/rendercv.git
    ```
3. Go to the `rendercv` directory.
    ```
    cd rendercv
    ```
4. Start using one of the virtual environments by activating it in the terminal.

    Default development environment with Python 3.13:
    ```bash
    hatch shell default
    ```

    The same environment, but with Python 3.10 (or 3.11, 3.12, 3.13):
    ```bash
    hatch shell test.py3.10
    ```

5. Finally, activate the virtual environment in your integrated development environment (IDE). In Visual Studio Code:

    - Press `Ctrl+Shift+P`.
    - Type `Python: Select Interpreter`.
    - Select one of the virtual environments created by Hatch.


### Develop with GitHub Codespaces

1.  [Fork](https://github.com/rendercv/rendercv/fork) the repository.
2.  Navigate to the forked repository.
3.  Click the <> **Code** button, then click the **Codespaces** tab, and then click **Create codespace on main**.

Then, [Visual Studio Code for the Web](https://code.visualstudio.com/docs/editor/vscode-web) will be opened with a ready-to-use development environment.

This is done with [Development containers](https://containers.dev/), and the environment is defined in the [`.devcontainer/devcontainer.json`](https://github.com/rendercv/rendercv/blob/main/.devcontainer/devcontainer.json) file. Dev containers can also be run locally using various [supporting tools and editors](https://containers.dev/supporting).

## Available Commands

These commands are defined in the [`pyproject.toml`](https://github.com/rendercv/rendercv/blob/main/pyproject.toml) file.

- Format the code with [Black](https://github.com/psf/black) and [Ruff](https://github.com/astral-sh/ruff)
    ```bash
    hatch run format
    ```
- Lint the code with [Ruff](https://github.com/astral-sh/ruff)
    ```bash
    hatch run lint
    ```
- Run [pre-commit](https://pre-commit.com/)
    ```bash
    hatch run precommit
    ```
- Check the types with [Pyright](https://github.com/RobertCraigie/pyright-python)
    ```bash
    hatch run check-types
    ```
- Run the tests with Python 3.13
    ```bash
    hatch run test
    ```
- Run the tests with Python 3.13 and generate the coverage report
    ```bash
    hatch run test-and-report
    ```
- Preview the documentation as you write it
    ```bash
    hatch run docs:serve
    ```
- Build the documentation
    ```bash
    hatch run docs:build
    ```
- Update [schema.json](https://github.com/rendercv/rendercv/blob/main/schema.json)
    ```bash
    hatch run docs:update-schema
    ```
- Update [`examples`](https://github.com/rendercv/rendercv/tree/main/examples) folder
    ```bash
    hatch run docs:update-examples
    ```
- Update figures of the entry types in the "[Structure of the YAML Input File](../user_guide/structure_of_the_yaml_input_file.md)"
    ```bash
    hatch run docs:update-entry-figures
    ```

## About [`pyproject.toml`](https://github.com/rendercv/rendercv/blob/main/pyproject.toml)

[`pyproject.toml`](https://github.com/rendercv/rendercv/blob/main/pyproject.toml) contains the metadata, dependencies, and tools required for the project. Please read through the file to understand the project's technical details.
