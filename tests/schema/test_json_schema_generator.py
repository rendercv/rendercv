import json
import pathlib

import jsonschema
import pytest

from rendercv.schema.json_schema_generator import (
    RenderCVSchemaGenerator,
    generate_json_schema,
    generate_json_schema_file,
)
from rendercv.schema.models.design.built_in_design import available_themes


def test_generate_json_schema():
    schema = generate_json_schema()
    assert isinstance(schema, dict)
    jsonschema.Draft7Validator.check_schema(schema)


def test_subsection_schema_accepts_recursive_groups_and_rejects_mixed_types():
    schema = generate_json_schema()
    entries = ["A paper."]
    for depth in range(8):
        entries = [{"title": f"Group {depth}", "entries": entries}]
    jsonschema.validate({"cv": {"sections": {"publications": entries}}}, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"cv": {"sections": {"publications": [*entries, "Mixed entry."]}}},
            schema,
        )


@pytest.mark.parametrize("theme", ["mytheme", "custom123"])
def test_custom_themes_accept_local_options(theme: str) -> None:
    jsonschema.validate(
        {"design": {"theme": theme, "custom_option": {"value": True}}},
        generate_json_schema(),
    )


@pytest.mark.parametrize(
    "theme", ["", "MyTheme", "my_theme", "my-theme", "../theme", "theme\n", "123"]
)
def test_custom_theme_name_rule_matches_runtime(theme: str) -> None:
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"design": {"theme": theme}}, generate_json_schema())


@pytest.mark.parametrize("theme", available_themes)
def test_custom_branch_does_not_relax_built_in_themes(theme: str) -> None:
    schema = generate_json_schema()
    jsonschema.validate({"design": {"theme": theme, "page": {"size": "a4"}}}, schema)
    for invalid in [{"custom_option": True}, {"page": {"size": "nonsense"}}]:
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate({"design": {"theme": theme, **invalid}}, schema)


def test_built_in_autocompletion_is_preserved() -> None:
    schema = generate_json_schema()
    built_in = schema["$defs"]["BuiltInDesign"]
    assert set(built_in["discriminator"]["mapping"]) == set(available_themes)
    for reference in built_in["oneOf"]:
        theme = schema["$defs"][reference["$ref"].split("/")[-1]]
        assert {"theme", "page", "typography", "templates"} <= theme[
            "properties"
        ].keys()


def test_generate_json_schema_file(tmp_path):
    schema_file_path = tmp_path / "schema.json"
    generate_json_schema_file(schema_file_path)

    assert schema_file_path.exists()

    schema_text = schema_file_path.read_text(encoding="utf-8")
    schema = json.loads(schema_text)

    assert isinstance(schema, dict)


def test_render_cv_schema_generator_writes_paths_the_same_on_every_system():
    generator = RenderCVSchemaGenerator()

    result = generator.encode_default(pathlib.PureWindowsPath("OUTPUT_FOLDER/cv.pdf"))

    assert result == "OUTPUT_FOLDER/cv.pdf"
