import json
import pathlib

import pydantic

from .models.rendercv_model import RenderCVModel


def generate_json_schema() -> dict:
    """Generate JSON Schema (Draft-07) from RenderCV Pydantic models.

    Why:
        IDEs and validators need machine-readable schema for autocompletion
        and real-time validation. Custom generator adds RenderCV-specific
        metadata like title, description, and canonical schema URL.

    Returns:
        Draft-07 JSON Schema dictionary.
    """

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
    """Generate and save JSON Schema to file.

    Args:
        json_schema_path: Target file path for schema output.
    """
    schema = generate_json_schema()
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
    json_schema_path.write_text(schema_json, encoding="utf-8")
