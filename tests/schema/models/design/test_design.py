import os
import shutil

import pydantic
import pytest

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


def test_custom_theme(testdata_directory_path):
    os.chdir(
        testdata_directory_path
        / "test_copy_theme_files_to_output_directory_custom_theme"
    )
    design = design_adapter.validate_python(
        {
            "theme": "dummytheme",
        }
    )

    assert design.theme == "dummytheme"


def test_custom_theme_without_init_file(tmp_path, testdata_directory_path):
    reference_custom_theme_path = (
        testdata_directory_path
        / "test_copy_theme_files_to_output_directory_custom_theme"
        / "dummytheme"
    )

    # copy the directory to tmp_path:
    custom_theme_path = tmp_path / "dummytheme"
    shutil.copytree(reference_custom_theme_path, custom_theme_path, dirs_exist_ok=True)

    # remove the __init__.py file:
    init_file = custom_theme_path / "__init__.py"
    init_file.unlink()

    os.chdir(tmp_path)
    data_model = design_adapter.validate_python(
        {
            "theme": "dummytheme",
        }
    )

    assert data_model.theme == "dummytheme"


def test_custom_theme_with_broken_init_file(tmp_path, testdata_directory_path):
    reference_custom_theme_path = (
        testdata_directory_path
        / "test_copy_theme_files_to_output_directory_custom_theme"
        / "dummytheme"
    )

    # copy the directory to tmp_path:
    custom_theme_path = tmp_path / "dummytheme"
    shutil.copytree(reference_custom_theme_path, custom_theme_path, dirs_exist_ok=True)

    # overwrite the __init__.py file (syntax error)
    init_file = custom_theme_path / "__init__.py"
    init_file.write_text("invalid python code", encoding="utf-8")

    os.chdir(tmp_path)
    with pytest.raises(pydantic.ValidationError):
        design_adapter.validate_python(
            {
                "theme": "dummytheme",
            }
        )

    # overwrite the __init__.py file (import error)
    init_file = custom_theme_path / "__init__.py"
    init_file.write_text("from ... import test", encoding="utf-8")

    os.chdir(tmp_path)
    with pytest.raises(pydantic.ValidationError):
        design_adapter.validate_python(
            {
                "theme": "dummytheme",
            }
        )
