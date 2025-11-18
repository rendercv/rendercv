import json

from rendercv.schema.json_schema_generator import (
    generate_json_schema,
    generate_json_schema_file,
)


def test_generate_json_schema():
    schema = generate_json_schema()
    assert isinstance(schema, dict)


def test_generate_json_schema_file(tmp_path):
    schema_file_path = tmp_path / "schema.json"
    generate_json_schema_file(schema_file_path)

    assert schema_file_path.exists()

    schema_text = schema_file_path.read_text(encoding="utf-8")
    schema = json.loads(schema_text)

    assert isinstance(schema, dict)
