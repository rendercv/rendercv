import json
import pathlib

import pydantic

from ..models.rendercv_model import RenderCVModel


def generate_json_schema() -> dict:
    """Generate the JSON schema of RenderCV.

    JSON schema is generated for the users to make it easier for them to write the input
    file. The JSON Schema of RenderCV is saved in the root directory of the repository
    (`schema.json`).

    Returns:
        The JSON schema of RenderCV as a dictionary.
    """

    class RenderCVSchemaGenerator(pydantic.json_schema.GenerateJsonSchema):
        def generate(self, schema, mode="validation"):
            json_schema = super().generate(schema, mode=mode)

            # Basic information about the schema:
            json_schema["title"] = "RenderCV"
            json_schema["description"] = "RenderCV data model."
            json_schema["$id"] = (
                "https://raw.githubusercontent.com/rendercv/rendercv/main/schema.json"
            )
            json_schema["$schema"] = "http://json-schema.org/draft-07/schema#"

            # Loop through $defs and remove docstring descriptions and fix optional
            # fields
            for _, value in json_schema["$defs"].items():
                for _, field in value["properties"].items():
                    if "anyOf" in field:
                        field["oneOf"] = field["anyOf"]
                        del field["anyOf"]

                if "description" in value and value["description"].startswith(
                    "This class is"
                ):
                    del value["description"]

            return json_schema

    return RenderCVModel.model_json_schema(schema_generator=RenderCVSchemaGenerator)


def generate_json_schema_file(json_schema_path: pathlib.Path):
    """Generate the JSON schema of RenderCV and save it to a file.

    Args:
        json_schema_path: The path to save the JSON schema.
    """
    schema = generate_json_schema()
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
    json_schema_path.write_text(schema_json, encoding="utf-8")
