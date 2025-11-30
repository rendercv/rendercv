import os
import pathlib

import pydantic
import pytest

from rendercv.schema.models.context import ValidationContext
from rendercv.schema.models.design.design import Design


class TestValidateDesign:
    @pytest.fixture
    def design_adapter(self):
        return pydantic.TypeAdapter(Design)

    def test_rejects_nonexistent_custom_theme(self, design_adapter):
        with pytest.raises(pydantic.ValidationError):
            design_adapter.validate_python({"theme": "pathdoesntexist"})

    def test_rejects_custom_theme_with_invalid_name(self, design_adapter, tmp_path):
        theme_name = "path_exist_but_invalid"
        custom_theme_path = tmp_path / theme_name
        custom_theme_path.mkdir()
        (custom_theme_path / "EducationEntry.j2.typ").touch()
        os.chdir(tmp_path)

        with pytest.raises(pydantic.ValidationError):
            design_adapter.validate_python({"theme": theme_name})

    def test_rejects_custom_theme_with_missing_files(self, design_adapter, tmp_path):
        theme_name = "customtheme"
        custom_theme_path = tmp_path / theme_name
        custom_theme_path.mkdir()
        os.chdir(tmp_path)

        with pytest.raises(pydantic.ValidationError):
            design_adapter.validate_python({"theme": theme_name})

    def test_accepts_valid_custom_theme(
        self, design_adapter, tmp_path: pathlib.Path
    ):
        custom_theme_path = tmp_path / "dummytheme"
        custom_theme_path.mkdir()
        (custom_theme_path / "EducationEntry.j2.typ").touch()

        design = design_adapter.validate_python(
            {"theme": custom_theme_path.name},
            context={
                "context": ValidationContext(input_file_path=tmp_path / "input.yaml")
            },
        )

        assert design.theme == "dummytheme"

    def test_rejects_custom_theme_with_broken_init_file(self, design_adapter, tmp_path):
        custom_theme_path = tmp_path / "dummytheme"
        custom_theme_path.mkdir()
        (custom_theme_path / "EducationEntry.j2.typ").touch()

        init_file = custom_theme_path / "__init__.py"
        init_file.write_text("invalid python code", encoding="utf-8")

        with pytest.raises(pydantic.ValidationError):
            design_adapter.validate_python(
                {"theme": "dummytheme"},
                context={
                    "context": ValidationContext(
                        input_file_path=tmp_path / "input.yaml"
                    )
                },
            )

        init_file.write_text("from ... import test", encoding="utf-8")

        with pytest.raises(pydantic.ValidationError):
            design_adapter.validate_python(
                {"theme": "dummytheme"},
                context={
                    "context": ValidationContext(
                        input_file_path=tmp_path / "input.yaml"
                    )
                },
            )

    def test_accepts_custom_theme_with_valid_init_file(self, design_adapter, tmp_path):
        custom_theme_path = tmp_path / "mytheme"
        custom_theme_path.mkdir()
        (custom_theme_path / "EducationEntry.j2.typ").touch()

        init_file = custom_theme_path / "__init__.py"
        init_file.write_text(
            """
from pydantic import BaseModel

class MythemeTheme(BaseModel):
    theme: str
    custom_option: str = "default_value"
""",
            encoding="utf-8",
        )

        design = design_adapter.validate_python(
            {"theme": "mytheme", "custom_option": "test_value"},
            context={
                "context": ValidationContext(input_file_path=tmp_path / "input.yaml")
            },
        )

        assert design.theme == "mytheme"
        assert design.custom_option == "test_value"

    def test_rejects_custom_theme_with_missing_model_class(
        self, design_adapter, tmp_path
    ):
        custom_theme_path = tmp_path / "mytheme"
        custom_theme_path.mkdir()
        (custom_theme_path / "EducationEntry.j2.typ").touch()

        init_file = custom_theme_path / "__init__.py"
        init_file.write_text(
            """
from pydantic import BaseModel

class SomeOtherClass(BaseModel):
    pass
""",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="does not have a MythemeTheme class"):
            design_adapter.validate_python(
                {"theme": "mytheme"},
                context={
                    "context": ValidationContext(
                        input_file_path=tmp_path / "input.yaml"
                    )
                },
            )

    def test_rejects_invalid_built_in_theme_options(self, design_adapter):
        with pytest.raises(pydantic.ValidationError):
            design_adapter.validate_python(
                {"theme": "classic", "colors": "invalid_value_not_a_dict"}
            )
