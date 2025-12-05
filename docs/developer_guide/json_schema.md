---
toc_depth: 3
---

# JSON Schema

## The Problem

You've encountered this everywhere, even if you didn't realize it was the same problem:

**VS Code settings** (`settings.json`):
```json
{
  "editor.fontSize": 14,
  "editor.tabSiz": 4  // ← Typo! VS Code highlights it red immediately
}
```

**GitHub Actions workflows** (`.github/workflows/test.yaml`):
```yaml
on:
  push:
    branchs:  # ← Typo! Your editor underlines it, suggests "branches"
      - main
```

**These files are completely different - VS Code settings, GitHub workflows. But you get autocomplete and validation in both.** How?

VS Code doesn't just "know" what's valid in `settings.json`. GitHub Actions workflows don't magically get autocomplete.

**Someone had to tell your editor:** "Here are all the valid fields, their types, and what they mean."

That "someone" is **JSON Schema**.

## What is JSON Schema?

JSON Schema is a **standard way to describe the structure of JSON/YAML documents**.

Think of it as a specification - a formal description of what's valid:

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Your full name"
    },
    "age": {
      "type": "integer",
      "minimum": 0,
      "description": "Your age in years"
    },
    "email": {
      "type": "string",
      "format": "email"
    }
  },
  "required": ["name"]
}
```

This schema says:

- A valid document is an object
- It must have a `name` field (string, required)
- It can have an `age` field (non-negative integer, optional)
- It can have an `email` field (string matching email format, optional)

**Why does JSON Schema exist?**

Because JSON and YAML files are **everywhere** - configuration files, API requests/responses, CI/CD workflows, application settings, data files. They all share the same problem:

**How do you communicate what's valid?**

You could write documentation: "The `name` field is required and must be a string. The `age` field is optional and must be a non-negative integer." But **documentation is for humans to read, not machines**.

JSON Schema is the **same information in machine-readable format** - so editors can understand it.

Once your editor has a schema, it can provide autocomplete, catch typos, and show inline documentation as you type.

This is why:

- **Microsoft publishes a JSON Schema for VS Code settings** - your editor fetches it and provides autocomplete
- **GitHub publishes a JSON Schema for Actions workflows** - that's how you get field suggestions
- **Thousands of tools do the same** - Kubernetes, Docker, Terraform, ESLint, package.json, tsconfig.json, the list goes on

JSON Schema is **infrastructure for editor tooling**.

## RenderCV's JSON Schema

RenderCV has the same problem. Users write their CVs in YAML, and we want them to have a smooth editor experience - autocomplete, typo detection, inline documentation.

**Solution:** Publish a JSON Schema for RenderCV YAML files.

![JSON Schema of RenderCV](../assets/images/json_schema.gif)

That's why [`schema.json`](https://github.com/rendercv/rendercv/blob/main/schema.json) exists in the repository - same universal problem, same universal solution.

## How the Schema is Generated

We don't write `schema.json` by hand. **It's automatically generated from Pydantic models.**

RenderCV's entire data structure is defined using Pydantic models (see [Understanding RenderCV](understanding_rendercv.md) for details). Pydantic has a built-in feature: `model_json_schema()` - it generates JSON Schema from your models.

That's what [`src/rendercv/schema/json_schema_generator.py`](https://github.com/rendercv/rendercv/blob/main/src/rendercv/schema/json_schema_generator.py) does - calls `model_json_schema()` on our top-level model and writes the result to `schema.json`.

## How Editors Know to Use RenderCV's Schema

There are two ways editors discover and use RenderCV's schema:

### 1. Manual Declaration

Add a special comment at the top of your YAML file:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.4/schema.json

cv:
  name: John Doe
```

This tells the editor: "Use RenderCV's schema for this file." Note the version tag in the URL - this ensures you get the schema matching your RenderCV version.

**Requirements:** Your editor needs to support this. For VS Code, install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml).

### 2. Schema Store (Automatic)

RenderCV's schema is listed in [SchemaStore](https://github.com/SchemaStore/schemastore) - a central registry of schemas that most IDEs use.

In SchemaStore, RenderCV's schema is configured to automatically activate for files ending with `_CV.yaml`. This means:

- If your file is named `John_Doe_CV.yaml`
- And your editor uses SchemaStore (VS Code with YAML extension does)
- You get autocomplete automatically - no comment needed

## When is the Schema Generated?

During development, whenever data models change, run:

```bash
just update-schema
```

This runs [`scripts/update_schema.py`](https://github.com/rendercv/rendercv/blob/main/scripts/update_schema.py), which regenerates `schema.json`.

## Learn More

- [Pydantic JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/) - How Pydantic generates schemas from models
