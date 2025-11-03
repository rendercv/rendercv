"""JSON Schema generation for IDE autocomplete and validation."""

import json
import pathlib

import pydantic

from ..models.rendercv_model import RenderCVModel


def generate_json_schema() -> dict:
    """Generate JSON Schema (Draft-07) from RenderCV Pydantic models."""

    class RenderCVSchemaGenerator(pydantic.json_schema.GenerateJsonSchema):
        def generate(self, schema, mode="validation"):
            json_schema = super().generate(schema, mode=mode)
            json_schema["title"] = "RenderCV"
            json_schema["description"] = (
                "RenderCV allows you to version-control CVs/resumes as JSON or YAML"
                " files."
            )
            json_schema["$id"] = (
                "https://raw.githubusercontent.com/rendercv/rendercv/main/schema.json"
            )
            json_schema["$schema"] = "http://json-schema.org/draft-07/schema#"
            return json_schema

    return RenderCVModel.model_json_schema(schema_generator=RenderCVSchemaGenerator)


def generate_json_schema_file(json_schema_path: pathlib.Path) -> None:
    """Generate and save JSON Schema to file."""
    schema = generate_json_schema()
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
    json_schema_path.write_text(schema_json, encoding="utf-8")
