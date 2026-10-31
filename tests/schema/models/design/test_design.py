import os
import pathlib
from unittest.mock import MagicMock, patch

import pydantic
import pytest

from rendercv.exception import RenderCVInternalError
from rendercv.schema.models.design.design import Design, find_missing_options
from rendercv.schema.models.validation_context import ValidationContext


class TestDesign:
    @pytest.fixture
    def design_adapter(self):
        return pydantic.TypeAdapter[Design](Design)

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

    def test_accepts_valid_custom_theme(self, design_adapter, tmp_path: pathlib.Path):
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
        assert (
            design_adapter.dump_python(design, warnings="error")["theme"]
            == "dummytheme"
        )
        assert b'"theme":"dummytheme"' in design_adapter.dump_json(
            design, warnings="error"
        )

    def test_template_only_custom_theme_applies_classic_options(
        self, design_adapter, tmp_path: pathlib.Path
    ):
        custom_theme_path = tmp_path / "dummytheme"
        custom_theme_path.mkdir()
        (custom_theme_path / "EducationEntry.j2.typ").touch()

        design = design_adapter.validate_python(
            {"theme": "dummytheme", "page": {"size": "a4"}},
            context={
                "context": ValidationContext(input_file_path=tmp_path / "input.yaml")
            },
        )

        assert design.page.size == "a4"

    def test_template_only_custom_theme_rejects_unknown_options(
        self, design_adapter, tmp_path: pathlib.Path
    ):
        custom_theme_path = tmp_path / "dummytheme"
        custom_theme_path.mkdir()
        (custom_theme_path / "EducationEntry.j2.typ").touch()

        with pytest.raises(pydantic.ValidationError):
            design_adapter.validate_python(
                {"theme": "dummytheme", "unknown_option": True},
                context={
                    "context": ValidationContext(
                        input_file_path=tmp_path / "input.yaml"
                    )
                },
            )

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
from typing import Literal

from rendercv.schema.models.design.classic_theme import ClassicTheme

class MythemeTheme(ClassicTheme):
    theme: Literal["mytheme"] = "mytheme"
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
        dumped = design_adapter.dump_python(design, warnings="error")
        assert dumped["theme"] == "mytheme"
        assert dumped["custom_option"] == "test_value"
        assert b'"custom_option":"test_value"' in design_adapter.dump_json(
            design, warnings="error"
        )

    def test_rejects_custom_theme_lacking_classic_options(
        self, design_adapter, tmp_path
    ):
        # An `__init__.py` from an older `rendercv create-theme` lacks the options
        # added since. Rendering it would crash, so validation names them:
        custom_theme_path = tmp_path / "mytheme"
        custom_theme_path.mkdir()
        (custom_theme_path / "Header.j2.typ").touch()
        (custom_theme_path / "__init__.py").write_text(
            """
from typing import Literal

import pydantic

from rendercv.schema.models.design.classic_theme import ClassicTheme, Templates

OldTemplates = pydantic.create_model(
    "OldTemplates",
    **{
        name: (field.annotation, field)
        for name, field in Templates.model_fields.items()
        if name != "time_span"
    },
)

class MythemeTheme(ClassicTheme):
    theme: Literal["mytheme"] = "mytheme"
    templates: OldTemplates = OldTemplates()
""",
            encoding="utf-8",
        )

        with pytest.raises(pydantic.ValidationError) as exc:
            design_adapter.validate_python(
                {"theme": "mytheme"},
                context={
                    "context": ValidationContext(input_file_path=tmp_path / "cv.yaml")
                },
            )

        error = exc.value.errors()[0]
        assert error["type"] == "rendercv_other_error"
        assert error["ctx"]["missing_options"] == "templates.time_span"

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

    def test_raises_internal_error_when_spec_is_none(self, design_adapter, tmp_path):
        custom_theme_path = tmp_path / "mytheme"
        custom_theme_path.mkdir()
        (custom_theme_path / "EducationEntry.j2.typ").touch()
        (custom_theme_path / "__init__.py").write_text("# empty", encoding="utf-8")

        with (
            patch(
                "rendercv.schema.models.design.design.importlib.util"
                ".spec_from_file_location",
                return_value=None,
            ),
            pytest.raises(RenderCVInternalError, match="Failed to load spec"),
        ):
            design_adapter.validate_python(
                {"theme": "mytheme"},
                context={
                    "context": ValidationContext(
                        input_file_path=tmp_path / "input.yaml"
                    )
                },
            )

    def test_raises_internal_error_when_spec_loader_is_none(
        self, design_adapter, tmp_path
    ):
        custom_theme_path = tmp_path / "mytheme"
        custom_theme_path.mkdir()
        (custom_theme_path / "EducationEntry.j2.typ").touch()
        (custom_theme_path / "__init__.py").write_text("# empty", encoding="utf-8")

        mock_spec = MagicMock()
        mock_spec.name = "theme"
        mock_spec.loader = None
        mock_spec.submodule_search_locations = None

        with (
            patch(
                "rendercv.schema.models.design.design.importlib.util"
                ".spec_from_file_location",
                return_value=mock_spec,
            ),
            pytest.raises(RenderCVInternalError, match=r"spec\.loader is None"),
        ):
            design_adapter.validate_python(
                {"theme": "mytheme"},
                context={
                    "context": ValidationContext(
                        input_file_path=tmp_path / "input.yaml"
                    )
                },
            )

    def test_rejects_a_design_that_is_not_a_mapping(self, design_adapter):
        with pytest.raises(pydantic.ValidationError) as exc:
            design_adapter.validate_python("classic")
        assert exc.value.errors()[0]["type"] == "model_attributes_type"

    @pytest.mark.parametrize(
        "design",
        [
            {},
            {"theme": None},
            {"theme": 123},
            {"theme": ["classic"]},
            {"theme": "bad_name"},
            {"theme": "valid\n"},
        ],
    )
    def test_rejects_bad_selectors_at_theme(self, design_adapter, design):
        with pytest.raises(pydantic.ValidationError) as exc:
            design_adapter.validate_python(design)
        assert exc.value.errors()[0]["loc"] == ("theme",)

    def test_routing_does_not_consult_discriminator_errors(
        self, design_adapter, tmp_path
    ):
        folder = tmp_path / "mytheme"
        folder.mkdir()
        (folder / "Entry.j2.typ").touch()
        with patch(
            "rendercv.schema.models.design.design.built_in_design_adapter.validate_python",
            side_effect=AssertionError("No union probe"),
        ):
            assert (
                design_adapter.validate_python({"theme": "classic"}).theme == "classic"
            )
            design = design_adapter.validate_python(
                {"theme": "mytheme"},
                context={
                    "context": ValidationContext(input_file_path=tmp_path / "cv.yaml")
                },
            )
            assert design.theme == "mytheme"
            with pytest.raises(pydantic.ValidationError):
                design_adapter.validate_python({"theme": "classic", "colors": 3})

    @pytest.mark.parametrize(
        "definition", ["MythemeTheme = 42", "class MythemeTheme: pass", "# no class"]
    )
    def test_invalid_model_definition_is_a_domain_error(
        self, design_adapter, tmp_path, definition
    ):
        folder = tmp_path / "mytheme"
        folder.mkdir()
        (folder / "Entry.j2.typ").touch()
        (folder / "__init__.py").write_text(definition, encoding="utf-8")
        with pytest.raises(pydantic.ValidationError) as exc:
            design_adapter.validate_python(
                {"theme": "mytheme"},
                context={
                    "context": ValidationContext(input_file_path=tmp_path / "cv.yaml")
                },
            )
        assert exc.value.errors()[0]["type"] == "rendercv_other_error"

    def test_custom_model_receives_context_and_preserves_field_errors(
        self, design_adapter, tmp_path
    ):
        folder = tmp_path / "mytheme"
        folder.mkdir()
        (folder / "Entry.j2.typ").touch()
        (folder / "__init__.py").write_text(
            """
from pydantic import BaseModel, model_validator
class MythemeTheme(BaseModel):
    theme: str
    interests: int

    @model_validator(mode="before")
    @classmethod
    def check_context(cls, data, info):
        assert info.context["marker"] == "received"
        return data
""",
            encoding="utf-8",
        )
        with pytest.raises(pydantic.ValidationError) as exc:
            design_adapter.validate_python(
                {"theme": "mytheme", "interests": "bad"},
                context={
                    "marker": "received",
                    "context": ValidationContext(input_file_path=tmp_path / "cv.yaml"),
                },
            )
        assert exc.value.errors()[0]["loc"] == ("interests",)
        assert exc.value.errors()[0]["type"] == "int_parsing"

    def test_template_only_theme_validates_and_applies_options(
        self, design_adapter, tmp_path
    ):
        folder = tmp_path / "mytheme"
        folder.mkdir()
        (folder / "Entry.j2.typ").touch()
        context = {"context": ValidationContext(input_file_path=tmp_path / "cv.yaml")}
        design = design_adapter.validate_python(
            {"theme": "mytheme", "colors": {"body": "red"}}, context=context
        )
        assert str(design.colors.body) == "rgb(255, 0, 0)"
        with pytest.raises(pydantic.ValidationError) as exc:
            design_adapter.validate_python(
                {"theme": "mytheme", "interests": "bad"}, context=context
            )
        assert exc.value.errors()[0]["loc"] == ("interests",)


def test_find_missing_options_lists_nested_paths():
    class Inner(pydantic.BaseModel):
        kept: int = 1
        added: int = 2

    class Reference(pydantic.BaseModel):
        theme: str = "reference"
        inner: Inner = Inner()
        added_section: Inner = Inner()

    class OldInner(pydantic.BaseModel):
        kept: int = 1

    class Old(pydantic.BaseModel):
        theme: str = "old"
        inner: OldInner = OldInner()

    assert find_missing_options(Old(), Reference) == ["inner.added", "added_section"]
