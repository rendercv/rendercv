"""Generate docs/llms.txt from schema.json using a Jinja2 template."""

import json
import pathlib
import re

import jinja2

repository_root = pathlib.Path(__file__).parent.parent.parent
schema_path = repository_root / "schema.json"
example_path = repository_root / "examples" / "John_Doe_EngineeringclassicTheme_CV.yaml"
template_dir = pathlib.Path(__file__).parent
output_path = repository_root / "docs" / "llms.txt"


def resolve_ref(ref: str, defs: dict) -> dict:
    """Resolve a JSON Schema $ref string to its definition.

    Why: $ref strings like "#/$defs/PageSize" need to be looked up in the
    schema's $defs dictionary.

    Args:
        ref: The $ref string (e.g., "#/$defs/PageSize").
        defs: The $defs dictionary from the schema.

    Returns:
        The resolved definition dictionary.
    """
    key = ref.removeprefix("#/$defs/")
    return defs[key]


def simplify_type(prop_schema: dict, defs: dict) -> str:
    """Convert a JSON Schema property definition to a human-readable type string.

    Why: JSON Schema types are verbose and nested. LLMs need simple type
    descriptions like "string", "boolean", "list of strings", etc.

    Args:
        prop_schema: The property schema fragment.
        defs: The $defs dictionary for resolving references.

    Returns:
        A simplified type string.
    """
    if "anyOf" in prop_schema:
        # Filter out null types
        non_null = [
            branch for branch in prop_schema["anyOf"] if branch != {"type": "null"}
        ]
        if len(non_null) == 1:
            return simplify_type(non_null[0], defs)
        # Multiple non-null types (e.g., ArbitraryDate = string | integer)
        return " or ".join(simplify_type(branch, defs) for branch in non_null)

    if "$ref" in prop_schema:
        resolved = resolve_ref(prop_schema["$ref"], defs)
        ref_key = prop_schema["$ref"].removeprefix("#/$defs/")

        if "enum" in resolved:
            return "one of: " + ", ".join(f'"{v}"' for v in resolved["enum"])

        if ref_key == "TypstDimension":
            return "dimension (e.g., 0.7in, 1.2em, 10pt)"

        if ref_key in ("ArbitraryDate", "ExactDate"):
            return "date (YYYY-MM-DD, YYYY-MM, YYYY, or custom text)"

        if ref_key in (
            "ExistingPathRelativeToInput",
            "PlannedPathRelativeToInput",
        ):
            return "file path"

        # If it has properties, it's a nested object
        if "properties" in resolved:
            return "object"

        return simplify_type(resolved, defs)

    if "const" in prop_schema:
        return f'"{prop_schema["const"]}"'

    schema_type = prop_schema.get("type", "string")

    if schema_type == "array":
        items = prop_schema.get("items", {})
        if "$ref" in items:
            resolved = resolve_ref(items["$ref"], defs)
            item_title = resolved.get("title", "object")
            return f"list of {item_title}"
        item_type = items.get("type", "string")
        return f"list of {item_type}s"

    if prop_schema.get("format") == "date":
        return "date (YYYY-MM-DD)"

    if prop_schema.get("format") == "uri":
        return "URL"

    return schema_type


def clean_description(description: str | None) -> str | None:
    """Clean up a schema description for use in llms.txt.

    Why: Schema descriptions contain verbose content like "The default value
    is ..." and "Available placeholders:" lists that are redundant when shown
    alongside defaults and in a separate placeholders section.

    Args:
        description: The raw description string from the schema.

    Returns:
        A cleaned description string, or None if empty.
    """
    if not description:
        return None

    # Remove "The default value is ..." wherever it appears
    description = re.sub(
        r"\s*The default value is `.+?`\.?",
        "",
        description,
    )

    # Remove "Available placeholders:" sections and everything after
    description = re.sub(
        r"\s*Available placeholders:.*",
        "",
        description,
        flags=re.DOTALL,
    )

    # Remove "The following placeholders can be used:" sections
    description = re.sub(
        r"\s*The following placeholders can be used:.*",
        "",
        description,
        flags=re.DOTALL,
    )

    # Collapse multiple whitespace/newlines into single space
    description = re.sub(r"\s+", " ", description).strip().rstrip(".")

    return description if description else None


def extract_fields(definition: dict, defs: dict) -> list[dict]:
    """Extract field information from a JSON Schema definition.

    Why: Entry types, CV model, and design sub-models all have properties
    that need to be documented with their names, types, and metadata.

    Args:
        definition: A JSON Schema definition with "properties".
        defs: The $defs dictionary for resolving references.

    Returns:
        A list of field info dicts with keys: name, required, type,
        description, default, examples.
    """
    properties = definition.get("properties", {})
    required_fields = definition.get("required", [])
    fields = []

    for prop_name, prop_schema in properties.items():
        field_type = simplify_type(prop_schema, defs)
        description = clean_description(prop_schema.get("description"))

        default = prop_schema.get("default")
        examples = prop_schema.get("examples")

        fields.append(
            {
                "name": prop_name,
                "required": prop_name in required_fields,
                "type": field_type,
                "description": description,
                "default": default,
                "examples": examples,
            }
        )

    return fields


def extract_entry_types(defs: dict) -> list[dict]:
    """Extract all entry types from the ListOfEntries definition.

    Why: Entry types are the core building blocks for CV sections. The
    ListOfEntries.anyOf array lists all valid entry types.

    Args:
        defs: The $defs dictionary from the schema.

    Returns:
        A list of entry type dicts with keys: name, fields.
    """
    entry_types = []

    # Human-readable descriptions for each entry type (stable, rarely changes)
    descriptions = {
        "TextEntry": "Plain text without structure. Just write a string.",
        "EducationEntry": "For academic credentials.",
        "ExperienceEntry": "For work history and professional roles.",
        "PublicationEntry": "For papers, articles, and other publications.",
        "NormalEntry": (
            "A flexible entry for projects, awards, certifications, or anything else."
        ),
        "OneLineEntry": (
            "For compact key-value pairs, ideal for skills or technical proficiencies."
        ),
        "BulletEntry": "A single bullet point. Use for simple lists.",
        "NumberedEntry": "An automatically numbered entry.",
        "ReversedNumberedEntry": (
            "A numbered entry that counts down (useful for publication"
            " lists where recent items come first)."
        ),
    }

    for entry_variant in defs["ListOfEntries"]["anyOf"]:
        items = entry_variant.get("items", {})

        if items.get("type") == "string":
            # TextEntry — plain strings
            entry_types.append(
                {
                    "name": "TextEntry",
                    "description": descriptions["TextEntry"],
                    "fields": [],
                }
            )
            continue

        if "$ref" not in items:
            continue

        ref_key = items["$ref"].removeprefix("#/$defs/")
        definition = defs[ref_key]
        name = definition.get("title", ref_key.split("__")[-1])

        fields = extract_fields(definition, defs)

        entry_types.append(
            {
                "name": name,
                "description": descriptions.get(name, ""),
                "fields": fields,
            }
        )

    return entry_types


def extract_cv_fields(defs: dict) -> list[dict]:
    """Extract CV header fields from the Cv definition.

    Why: The CV model has personal information fields (name, email, etc.)
    that need to be documented.

    Args:
        defs: The $defs dictionary from the schema.

    Returns:
        A list of field info dicts (excluding 'sections' which is documented
        separately).
    """
    cv_def = defs["Cv"]
    fields = extract_fields(cv_def, defs)
    return [f for f in fields if f["name"] != "sections"]


def extract_design_section(
    section_name: str,
    section_schema: dict,
    defs: dict,
) -> dict:
    """Extract a design sub-section's fields, handling nested $ref objects.

    Why: Design sub-models (page, colors, typography, etc.) may contain
    nested objects (e.g., typography.font_family, header.connections) that
    need to be extracted as sub-sections.

    Args:
        section_name: The name of the design sub-section.
        section_schema: The schema for this sub-section (may be a $ref).
        defs: The $defs dictionary from the schema.

    Returns:
        A dict with keys: name, fields, sub_sections.
    """
    # Resolve $ref if present
    if "$ref" in section_schema:
        definition = resolve_ref(section_schema["$ref"], defs)
    else:
        definition = section_schema

    if "properties" not in definition:
        return {"name": section_name, "fields": [], "sub_sections": []}

    properties = definition.get("properties", {})
    required_fields = definition.get("required", [])
    fields = []
    sub_sections = []

    for prop_name, prop_schema in properties.items():
        # Check if this property references a nested object (not an enum)
        ref_key = None
        resolved = None

        if "$ref" in prop_schema:
            ref_key = prop_schema["$ref"].removeprefix("#/$defs/")
            resolved = defs.get(ref_key, {})
        elif "anyOf" in prop_schema:
            non_null = [b for b in prop_schema["anyOf"] if b != {"type": "null"}]
            if len(non_null) == 1 and "$ref" in non_null[0]:
                ref_key = non_null[0]["$ref"].removeprefix("#/$defs/")
                resolved = defs.get(ref_key, {})

        # If it resolves to an object with properties (not an enum), treat
        # as a sub-section
        if resolved and "properties" in resolved and "enum" not in resolved:
            sub_fields = extract_fields(resolved, defs)
            sub_sections.append(
                {
                    "name": prop_name,
                    "fields": sub_fields,
                }
            )
        else:
            field_type = simplify_type(prop_schema, defs)
            description = clean_description(prop_schema.get("description"))
            default = prop_schema.get("default")

            fields.append(
                {
                    "name": prop_name,
                    "required": prop_name in required_fields,
                    "type": field_type,
                    "description": description,
                    "default": default,
                }
            )

    return {
        "name": section_name,
        "fields": fields,
        "sub_sections": sub_sections,
    }


def extract_design_sections(defs: dict) -> list[dict]:
    """Extract all design sub-sections from the ClassicTheme definition.

    Why: ClassicTheme is the canonical theme. Its sub-sections (page, colors,
    typography, etc.) define all available design options.

    Args:
        defs: The $defs dictionary from the schema.

    Returns:
        A list of design section dicts.
    """
    classic = defs["ClassicTheme"]
    properties = classic.get("properties", {})
    sections = []

    for prop_name, prop_schema in properties.items():
        if prop_name == "theme":
            continue  # Skip the theme discriminator field
        section = extract_design_section(prop_name, prop_schema, defs)
        sections.append(section)

    return sections


def extract_path_placeholders(defs: dict) -> list[dict]:
    """Extract path placeholders from the RenderCommand definition.

    Why: Output path fields support placeholders like NAME, YEAR, etc. These
    are documented in the description of path fields.

    Args:
        defs: The $defs dictionary from the schema.

    Returns:
        A list of placeholder dicts with keys: name, description.
    """
    render_command = defs["RenderCommand"]
    # Get the typst_path description which lists all placeholders
    typst_desc = render_command["properties"]["typst_path"].get("description", "")

    placeholders = []
    for line in typst_desc.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- ") and ":" in stripped:
            parts = stripped[2:].split(":", 1)
            placeholders.append(
                {
                    "name": parts[0].strip(),
                    "description": parts[1].strip(),
                }
            )

    return placeholders


def uncomment_yaml(text: str) -> str:
    """Uncomment commented-out YAML lines (e.g., '  # key: value' → '  key: value').

    Why: The example YAML files have optional sections commented out. For llms.txt,
    we want to show all options as active YAML so LLMs can see the full structure.

    Args:
        text: The YAML text with commented lines.

    Returns:
        The YAML text with comment markers removed.
    """
    lines = text.split("\n")
    result = []
    for line in lines:
        # Match lines like "  # key: value" — indented comment that is YAML content
        uncommented = re.sub(r"^(\s*)# ", r"\1", line)
        result.append(uncommented)
    return "\n".join(result)


def main() -> None:
    """Generate docs/llms.txt from schema.json and the Jinja2 template."""
    schema = json.loads(schema_path.read_text())
    defs = schema["$defs"]

    # Extract all data from schema
    entry_types = extract_entry_types(defs)
    cv_fields = extract_cv_fields(defs)
    themes = list(defs["BuiltInDesign"]["discriminator"]["mapping"].keys())
    social_networks = defs["SocialNetworkName"]["enum"]
    locales = list(defs["Locale"]["discriminator"]["mapping"].keys())

    # Locale customizable fields from EnglishLocale (excluding "language")
    locale_fields = [
        f
        for f in extract_fields(defs["EnglishLocale"], defs)
        if f["name"] != "language"
    ]

    enums = {
        "page_sizes": defs["PageSize"]["enum"],
        "alignments": defs["Alignment"]["enum"],
        "bullets": defs["Bullet"]["enum"],
        "section_title_types": defs["SectionTitleType"]["enum"],
        "phone_number_formats": defs["PhoneNumberFormatType"]["enum"],
    }

    design_sections = extract_design_sections(defs)

    # Settings fields
    settings_fields = extract_fields(defs["Settings"], defs)

    # RenderCommand fields
    render_command_fields = extract_fields(defs["RenderCommand"], defs)

    path_placeholders = extract_path_placeholders(defs)

    # Read the example YAML (generated by scripts/update_examples.py)
    complete_example = example_path.read_text()
    # Strip the yaml-language-server schema comment (first line)
    if complete_example.startswith("# yaml-language-server"):
        complete_example = complete_example.split("\n", 1)[1]
    # Uncomment all commented-out sections so LLMs see the full structure
    complete_example = uncomment_yaml(complete_example)

    # Build context
    context = {
        "entry_types": entry_types,
        "cv_fields": cv_fields,
        "themes": themes,
        "social_networks": social_networks,
        "locales": locales,
        "locale_fields": locale_fields,
        "enums": enums,
        "design_sections": design_sections,
        "settings_fields": settings_fields,
        "render_command_fields": render_command_fields,
        "path_placeholders": path_placeholders,
        "complete_example": complete_example,
    }

    # Render template
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("template.j2.md")
    output = template.render(**context)

    # Clean up excessive blank lines (more than 2 consecutive)
    output = re.sub(r"\n{4,}", "\n\n\n", output)

    output_path.write_text(output)
    print("llms.txt generated successfully.")  # NOQA: T201


if __name__ == "__main__":
    main()
