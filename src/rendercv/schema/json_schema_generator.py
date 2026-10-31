import json
import pathlib
from typing import Any

import pydantic
import pydantic_core

from rendercv import __description__

from .models.rendercv_model import RenderCVModel


class RenderCVSchemaGenerator(pydantic.json_schema.GenerateJsonSchema):
    """JSON Schema generator for the input file of RenderCV.

    Why:
        IDEs and validators need machine-readable schema for autocompletion
        and real-time validation. This generator adds RenderCV-specific
        metadata like title, description, and canonical schema URL, leaves out
        the docstrings of models, and writes paths the same on every operating
        system, so that the schema is the same everywhere.
    """

    def generate(
        self,
        schema: pydantic_core.CoreSchema,
        mode: pydantic.json_schema.JsonSchemaMode = "validation",
    ) -> pydantic.json_schema.JsonSchemaValue:
        json_schema = super().generate(schema, mode=mode)
        json_schema["title"] = "RenderCV"
        json_schema["description"] = __description__
        json_schema["$id"] = (
            "https://raw.githubusercontent.com/rendercv/rendercv/main/schema.json"
        )
        json_schema["$schema"] = "http://json-schema.org/draft-07/schema#"
        return json_schema

    def encode_default(self, dft: Any) -> Any:
        # Paths are written as in YAML files, with `/` on every operating system:
        if isinstance(dft, pathlib.PurePath):
            return dft.as_posix()
        return super().encode_default(dft)

    def tagged_union_schema(
        self, schema: pydantic_core.core_schema.TaggedUnionSchema
    ) -> pydantic.json_schema.JsonSchemaValue:
        json_schema = super().tagged_union_schema(schema)
        # A union whose branch a function chooses, like a photo's path or URL, has
        # no tag field, and its branches overlap (a URL is also text). `oneOf` would
        # then reject inputs matching several branches, so any of them may match:
        if "discriminator" not in json_schema and "oneOf" in json_schema:
            json_schema["anyOf"] = json_schema.pop("oneOf")
        return json_schema

    def model_schema(
        self, schema: pydantic_core.core_schema.ModelSchema
    ) -> pydantic.json_schema.JsonSchemaValue:
        # A model's docstring explains it to developers, so it's not the
        # description users see in their editors (fields have descriptions):
        json_schema = super().model_schema(schema)
        json_schema.pop("description", None)
        return json_schema


def generate_json_schema() -> dict:
    """Generate JSON Schema (Draft-07) from RenderCV Pydantic models.

    Returns:
        Draft-07 JSON Schema dictionary.
    """
    return RenderCVModel.model_json_schema(schema_generator=RenderCVSchemaGenerator)


def generate_json_schema_file(json_schema_path: pathlib.Path) -> None:
    """Generate and save JSON Schema to file.

    Args:
        json_schema_path: Target file path for schema output.
    """
    schema = generate_json_schema()
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
    json_schema_path.write_text(schema_json, encoding="utf-8")
