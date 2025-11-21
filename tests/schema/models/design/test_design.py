import os
import pathlib

import pydantic
import pytest

from rendercv.schema.models.context import ValidationContext
from rendercv.schema.models.design.design import Design

design_adapter = pydantic.TypeAdapter(Design)


def test_custom_theme_that_doesnt_exist():
    with pytest.raises(pydantic.ValidationError):
        design_adapter.validate_python({"theme": "pathdoesntexist"})


def test_custom_theme_with_invalid_name(tmp_path):
    theme_name = "path_exist_but_invalid"
    custom_theme_path = tmp_path / theme_name
    custom_theme_path.mkdir()
    (custom_theme_path / "EducationEntry.j2.typ").touch()
    os.chdir(tmp_path)
    with pytest.raises(pydantic.ValidationError):
        design_adapter.validate_python({"theme": theme_name})


def test_custom_theme_with_missing_files(tmp_path):
    theme_name = "customtheme"
    custom_theme_path = tmp_path / theme_name
    custom_theme_path.mkdir()
    os.chdir(tmp_path)
    with pytest.raises(pydantic.ValidationError):
        design_adapter.validate_python(
            {
                "theme": theme_name,
            }
        )


def test_custom_theme(tmp_path: pathlib.Path):
    custom_theme_path = tmp_path / "dummytheme"
    custom_theme_path.mkdir()
    (custom_theme_path / "EducationEntry.j2.typ").touch()
    design = design_adapter.validate_python(
        {
            "theme": custom_theme_path.name,
        },
        context={"context": ValidationContext(input_file_path=tmp_path / "input.yaml")},
    )
    assert design.theme == "dummytheme"


def test_custom_theme_with_broken_init_file(tmp_path):
    custom_theme_path = tmp_path / "dummytheme"
    custom_theme_path.mkdir()
    (custom_theme_path / "EducationEntry.j2.typ").touch()

    # overwrite the __init__.py file (syntax error)
    init_file = custom_theme_path / "__init__.py"
    init_file.write_text("invalid python code", encoding="utf-8")

    with pytest.raises(pydantic.ValidationError):
        design_adapter.validate_python(
            {
                "theme": "dummytheme",
            },
            context={
                "context": ValidationContext(input_file_path=tmp_path / "input.yaml")
            },
        )

    # overwrite the __init__.py file (import error)
    init_file = custom_theme_path / "__init__.py"
    init_file.write_text("from ... import test", encoding="utf-8")

    with pytest.raises(pydantic.ValidationError):
        design_adapter.validate_python(
            {
                "theme": "dummytheme",
            },
            context={
                "context": ValidationContext(input_file_path=tmp_path / "input.yaml")
            },
        )
