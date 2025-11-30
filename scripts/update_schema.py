import pathlib

from rendercv.schema.json_schema_generator import generate_json_schema_file

json_schema_file_path = pathlib.Path(__file__).parent.parent / "schema.json"
generate_json_schema_file(json_schema_file_path)
print("Schema generated successfully.")  # NOQA: T201
