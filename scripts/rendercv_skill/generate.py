"""Write the rendercv/rendercv-skill repository: the AI agent skill and its README.

The skill's references (JSON Schema, CLI options, example CV, and theme defaults) come
from RenderCV itself, so they always describe the version that generates them. The
release workflow runs this script in a checkout of rendercv/rendercv-skill:

    uv run scripts/rendercv_skill/generate.py <directory>
"""

import json
import pathlib
import sys

import jinja2
import typer.main
from typer.core import TyperGroup, TyperOption

from rendercv import __version__
from rendercv.cli.app import app
from rendercv.schema.json_schema_generator import generate_json_schema
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.locale.locale import available_locales
from rendercv.schema.sample_generator import (
    create_sample_design_file,
    create_sample_yaml_input_file,
)

template_directory = pathlib.Path(__file__).parent


def cli_reference() -> str:
    """Describe every option of every command, from the CLI's own definitions."""
    root = typer.main.get_command(app)
    if not isinstance(root, TyperGroup):
        raise TypeError("RenderCV's CLI must be a command group.")
    lines = [f"# RenderCV {__version__} command reference\n"]
    for name, command in sorted(root.commands.items()):
        lines.extend([f"## rendercv {name}\n", "| Option | Meaning |", "| --- | --- |"])
        for parameter in command.params:
            if isinstance(parameter, TyperOption):
                options = ", ".join(f"`{option}`" for option in parameter.opts)
                help_text = (
                    (parameter.help or "").replace("|", "\\|").replace("\n", " ")
                )
                lines.append(f"| {options} | {help_text} |")
        lines.append("")
    return "\n".join(lines)


def build_skill_repository() -> dict[str, str]:
    """Return the contents of the skill repository, by path.

    Returns:
        A mapping from each file's path in the repository to its text.
    """
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_directory), keep_trailing_newline=True
    )
    context = {
        "version": __version__,
        "available_themes": available_themes,
        "available_locales": available_locales,
    }
    skill = pathlib.PurePosixPath("skills/rendercv")
    files = {
        "README.md": environment.get_template("readme_template.j2.md").render(context),
        f"{skill}/SKILL.md": environment.get_template("skill_template.j2.md").render(
            context
        ),
        f"{skill}/references/schema.json": json.dumps(
            generate_json_schema(), ensure_ascii=False, indent=2
        )
        + "\n",
        f"{skill}/references/cli.md": cli_reference(),
        f"{skill}/references/example.yaml": create_sample_yaml_input_file(
            file_path=None, name="John Doe"
        ),
    }
    for theme in available_themes:
        files[f"{skill}/references/themes/{theme}.yaml"] = create_sample_design_file(
            file_path=None, theme=theme
        )
    return files


if __name__ == "__main__":
    directory = pathlib.Path(sys.argv[1])
    for relative_path, content in build_skill_repository().items():
        path = directory / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
