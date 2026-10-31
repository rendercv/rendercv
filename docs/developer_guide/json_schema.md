---
toc_depth: 2
---

# JSON Schema

A text editor can tell that a file is valid YAML, but it doesn't know what RenderCV expects: which fields exist, what they mean, and which values they accept. Given a description of that structure, an editor can suggest field names as you type, show each field's explanation, and underline mistakes before you run RenderCV.

[JSON Schema](https://json-schema.org/learn/getting-started-step-by-step) is the standard format for such a description. This one describes an object with one required text field called `name`:

```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string", "description": "Your full name"}
  },
  "required": ["name"]
}
```

An editor using it suggests `name`, shows "Your full name" next to it, and flags `name: 42` as wrong. The schema itself is written in JSON, another text format for structured data, but editors apply it to YAML files too, because both formats describe the same kind of structure.

RenderCV publishes [`schema.json`](https://github.com/rendercv/rendercv/blob/main/schema.json) for CV files:

![JSON Schema of RenderCV](../assets/images/json_schema.gif)

## Generating the schema

RenderCV's [Pydantic models](understanding_rendercv.md#validating-the-data) already define every field, its type, and its description. Pydantic's `model_json_schema()` converts them to JSON Schema, so there is no second, hand-written list of fields that could disagree with the code.

After changing a model, run:

```bash
just update-schema
```

It adjusts the generated schema for editors and writes `schema.json`; commit that file with the model change. Tests check that the file is up to date, that each built-in theme accepts only its own options, and that custom themes, whose options the schema can't know in advance, are accepted.

The same schema also describes separate design, locale, and settings files, so none of its top-level fields is required. An editor's check is a convenience. RenderCV still validates everything before rendering, including what a schema can't express: whether a photo file exists, the options of a custom theme, and rules that connect several fields.

## Telling the editor which schema to use

`rendercv new` starts each new file with a comment pointing to the schema of the installed RenderCV version. For an existing file, add the comment yourself:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/rendercv/rendercv/v<< rendercv_version >>/schema.json

cv:
  name: John Doe
```

Keep the version in that address the same as your installed RenderCV, so the editor suggests exactly the fields that version understands. VS Code needs the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) to read the comment.

[SchemaStore](https://github.com/SchemaStore/schemastore) is a public catalog that tells editors which schema belongs to which kind of file. Through it, editors pick RenderCV's schema automatically for files whose names end in `_CV.yaml`. The comment takes precedence when you need a particular version.

[Pydantic's JSON Schema documentation](https://docs.pydantic.dev/latest/concepts/json_schema/) describes the generation in detail.
