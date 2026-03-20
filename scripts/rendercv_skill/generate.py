#!/usr/bin/env python3
"""Generate the distributable AI agent skill SKILL.md from a Jinja2 template.

Why:
    The SKILL.md file contains dynamic data (themes, locales, Pydantic model
    source code, etc.) that must stay in sync with the rendercv package. This
    script extracts that data and renders the Jinja2 template to produce an
    always-current skill file.
"""

import ast
import io
import pathlib
import re
import zipfile

import jinja2
import ruamel.yaml

from rendercv import __version__
from rendercv.schema.models.locale.locale import available_locales
from rendercv.schema.sample_generator import (
    create_sample_cv_file,
    create_sample_design_file,
)

# Only include a subset of themes in the skill to keep context size manageable.
SKILL_THEMES: list[str] = [
    "classic",
    "harvard",
    "engineeringresumes",
    "engineeringclassic",
    "sb2nov",
    "moderncv",
]

repository_root = pathlib.Path(__file__).parent.parent.parent
script_directory = pathlib.Path(__file__).parent
template_path = script_directory / "skill_template.j2.md"
output_path = (
    repository_root
    / ".claude"
    / "skills"
    / "rendercv-skill"
    / "skills"
    / "rendercv"
    / "SKILL.md"
)
llms_txt_path = repository_root / "docs" / "llms.txt"
skill_zip_path = repository_root / "docs" / "assets" / "rendercv_skill.zip"

# Paths to key model source files for dynamic inclusion.
models_dir = repository_root / "src" / "rendercv" / "schema" / "models"

# These source files are included in the skill so agents can see the
# type-safe Pydantic schema for core models.
MODEL_SOURCE_FILES: dict[str, pathlib.Path] = {
    "rendercv_model": models_dir / "rendercv_model.py",
    "cv": models_dir / "cv" / "cv.py",
    "social_network": models_dir / "cv" / "social_network.py",
    "custom_connection": models_dir / "cv" / "custom_connection.py",
}


def is_type_adapter_assignment(node: ast.Assign) -> bool:
    """Check if an assignment creates a pydantic.TypeAdapter instance.

    Why:
        Type adapter instances (e.g., `email_validator = pydantic.TypeAdapter[...]`)
        are internal validation plumbing, not part of the user-facing schema.

    Args:
        node: An AST Assign node.

    Returns:
        True if the assignment is a TypeAdapter instantiation.
    """
    source = ast.unparse(node)
    return "TypeAdapter" in source


def is_private_attr(node: ast.AnnAssign) -> bool:
    """Check if an annotated assignment is a private attribute.

    Why:
        Private attributes (e.g., `_key_order: list[str] = pydantic.PrivateAttr()`)
        are internal state, not user-facing YAML fields.

    Args:
        node: An AST AnnAssign node.

    Returns:
        True if the field name starts with underscore.
    """
    target = ast.unparse(node.target)
    return target.startswith("_")


def is_model_config(node: ast.Assign) -> bool:
    """Check if an assignment is a model_config declaration.

    Args:
        node: An AST Assign node.

    Returns:
        True if assigning to model_config.
    """
    return any(ast.unparse(t) == "model_config" for t in node.targets)


def is_url_dictionary(node: ast.AnnAssign) -> bool:
    """Check if an annotated assignment is the social network URL dictionary.

    Why:
        The url_dictionary mapping (network name → URL prefix) is internal
        plumbing. Agents only need the SocialNetworkName type alias to know
        which networks are supported.

    Args:
        node: An AST AnnAssign node.

    Returns:
        True if the target is url_dictionary.
    """
    return ast.unparse(node.target) == "url_dictionary"


def strip_class_body(class_node: ast.ClassDef) -> ast.ClassDef:
    """Strip a class definition down to just field definitions.

    Why:
        Agents need field names, types, and defaults — not validators,
        serializers, or cached properties. Stripping methods removes
        ~50% of tokens from model-heavy files.

    Args:
        class_node: An AST ClassDef node.

    Returns:
        A new ClassDef with only field annotations (no methods).
    """
    new_body: list[ast.stmt] = []
    for child in class_node.body:
        if (isinstance(child, ast.AnnAssign) and not is_private_attr(child)) or (
            isinstance(child, ast.Assign) and not is_model_config(child)
        ):
            new_body.append(child)

    # If the body would be empty, add a `pass` statement
    if not new_body:
        new_body.append(ast.Pass())

    new_class = ast.ClassDef(
        name=class_node.name,
        bases=class_node.bases,
        keywords=class_node.keywords,
        body=new_body,
        decorator_list=[],
    )
    return ast.fix_missing_locations(new_class)


def strip_to_schema(source: str) -> str:
    """Strip a Python source file to only schema-relevant declarations.

    Why:
        Full Pydantic model source files contain imports, validators,
        serializers, helper functions, type adapters, and private
        attributes that are implementation internals. Agents only need
        type aliases, constants, and class field definitions to understand
        the YAML schema. AST-based stripping removes ~40% of tokens.

    Args:
        source: Complete Python source code.

    Returns:
        Stripped source containing only schema-relevant code.
    """
    tree = ast.parse(source)
    kept_nodes: list[ast.stmt] = []

    for node in ast.iter_child_nodes(tree):
        # Keep type aliases, module-level annotated assignments, and plain
        # assignments that are not TypeAdapter instances. Skip url_dictionary
        # (agents only need the SocialNetworkName type alias).
        if (
            isinstance(node, ast.TypeAlias)
            or (isinstance(node, ast.AnnAssign) and not is_url_dictionary(node))
            or (isinstance(node, ast.Assign) and not is_type_adapter_assignment(node))
        ):
            kept_nodes.append(node)

        # Keep class definitions (stripped to fields only)
        elif isinstance(node, ast.ClassDef):
            kept_nodes.append(strip_class_body(node))

        # Skip everything else: imports, functions, expressions

    # Reconstruct source from kept nodes
    lines: list[str] = []
    for node in kept_nodes:
        unparsed = ast.unparse(node)
        lines.append(unparsed)
        lines.append("")  # blank line between declarations

    result = "\n".join(lines)

    # Strip redundant "The default value is `X`." from descriptions
    result = re.sub(
        r"\s*The default value is `[^`]*`\.?",
        "",
        result,
    )

    # Clean up leftover empty string concatenations (e.g., `+ ''` or `+ ""`)
    result = re.sub(r"\s*\+\s*['\"]'?['\"]", "", result)

    # Strip verbose description= strings (info is covered in Important Patterns)
    result = re.sub(r", description='[^']{40,}'", "", result)
    result = re.sub(r', description="[^"]{40,}"', "", result)

    # Clean up multiple blank lines
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result.strip() + "\n"


def trim_sample_cv_sections(cv_yaml: str, max_entries: int = 2) -> str:
    """Trim CV sections to at most max_entries entries each.

    Why:
        The sample CV has 5 experience entries, 4 publications, etc. For the
        skill file, showing structure matters more than volume. Trimming to
        2 entries per section saves ~2000 tokens.

    Args:
        cv_yaml: YAML string containing the cv section.
        max_entries: Maximum entries per section.

    Returns:
        Trimmed YAML string.
    """
    yaml = ruamel.yaml.YAML()
    yaml.preserve_quotes = True
    data = yaml.load(cv_yaml)

    sections = data.get("cv", {}).get("sections")
    if sections:
        for section_name in sections:
            entries = sections[section_name]
            if isinstance(entries, list) and len(entries) > max_entries:
                sections[section_name] = entries[:max_entries]

    stream = io.StringIO()
    yaml.dump(data, stream)
    return stream.getvalue()


def build_template_context() -> dict:
    """Assemble all dynamic data for the Jinja2 template.

    Returns:
        Template context dictionary.
    """
    # Generate sample CV
    sample_cv = create_sample_cv_file(file_path=None)
    sample_cv = trim_sample_cv_sections(sample_cv)

    # Generate full classic sample design
    sample_classic_design = create_sample_design_file(file_path=None, theme="classic")

    # Read other theme override YAMLs (only the fields that differ from classic)
    # Strip the templates: section since it's mostly the same across themes
    # (noted once in the skill template instead).
    other_themes_dir = models_dir / "design" / "other_themes"
    theme_overrides: dict[str, str] = {}
    for theme in SKILL_THEMES:
        if theme == "classic":
            continue
        yaml_path = other_themes_dir / f"{theme}.yaml"
        if yaml_path.exists():
            yaml = ruamel.yaml.YAML()
            data = yaml.load(yaml_path.read_text(encoding="utf-8"))
            if "design" in data and "templates" in data["design"]:
                del data["design"]["templates"]
            stream = io.StringIO()
            yaml.dump(data, stream)
            theme_overrides[theme] = stream.getvalue().strip()

    # Read and strip core model source files
    model_sources: dict[str, str] = {}
    for name, path in MODEL_SOURCE_FILES.items():
        raw_source = path.read_text(encoding="utf-8")
        model_sources[name] = strip_to_schema(raw_source)

    return {
        "version": __version__,
        "available_themes": SKILL_THEMES,
        "available_locales": available_locales,
        "model_sources": model_sources,
        "sample_cv": sample_cv,
        "sample_classic_design": sample_classic_design,
        "theme_overrides": theme_overrides,
    }


def generate_skill_file() -> None:
    """Render the Jinja2 template and write SKILL.md, docs/llms.txt, and ZIP."""
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(script_directory),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_path.name)
    context = build_template_context()

    rendered = template.render(context)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    llms_txt_path.write_text(rendered, encoding="utf-8")

    # Generate ZIP for Claude Desktop skill upload
    # Use a fixed timestamp so the zip is reproducible across runs.
    fixed_date = (2025, 1, 1, 0, 0, 0)
    skill_zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(skill_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("rendercv/SKILL.md", date_time=fixed_date)
        zf.writestr(info, rendered)


if __name__ == "__main__":
    generate_skill_file()
    print("Skill generated successfully.")  # NOQA: T201
