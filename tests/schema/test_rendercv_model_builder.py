import io
import pathlib
from datetime import date as Date

import pytest
import ruamel.yaml

from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.rendercv_model_builder import (
    build_rendercv_dictionary,
    build_rendercv_model,
    build_rendercv_model_from_dictionary,
)
from rendercv.schema.sample_generator import dictionary_to_yaml


@pytest.fixture
def minimal_input_dict():
    """Minimal valid input dictionary."""
    return {
        "cv": {"name": "John Doe"},
        "design": {"theme": "classic"},
    }


@pytest.fixture
def create_yaml_file_fixture(tmp_path):
    """Factory fixture to create temporary YAML files."""

    def create_file(name: str, dictionary: dict) -> pathlib.Path:
        file_path = tmp_path / name
        yaml_content = dictionary_to_yaml(dictionary)
        file_path.write_text(yaml_content, encoding="utf-8")
        return file_path

    return create_file


class TestBuildRendercvDictionary:
    @pytest.mark.parametrize(
        "input_type",
        ["string", "file"],
    )
    def test_basic_input_without_overlays(
        self, minimal_input_dict, create_yaml_file_fixture, input_type
    ):
        if input_type == "string":
            yaml_input = dictionary_to_yaml(minimal_input_dict)
        else:  # file
            yaml_input = create_yaml_file_fixture("input.yaml", minimal_input_dict)

        result = build_rendercv_dictionary(yaml_input)

        assert result["cv"]["name"] == "John Doe"
        assert result["design"]["theme"] == "classic"

    @pytest.mark.parametrize("input_type", ["string", "file"])
    @pytest.mark.parametrize(
        ("overlay_key", "overlay_content"),
        [
            ("design", {"design": {"theme": "engineeringresumes"}}),
            ("locale", {"locale": {"language": "turkish"}}),
            (
                "settings",
                {"settings": {"render_command": {"pdf_path": "custom.pdf"}}},
            ),
        ],
    )
    def test_single_overlay(
        self,
        minimal_input_dict,
        create_yaml_file_fixture,
        overlay_key,
        overlay_content,
        input_type,
    ):
        main_input = {
            **minimal_input_dict,
            "locale": {"language": "english"},
            "settings": {"original_setting": "original"},
        }

        main_yaml = dictionary_to_yaml(main_input)

        # Create overlay as string or file
        if input_type == "string":
            overlay_input = dictionary_to_yaml(overlay_content)
        else:  # file
            overlay_input = create_yaml_file_fixture(
                f"{overlay_key}.yaml", overlay_content
            )

        kwargs = {f"{overlay_key}_file_path_or_contents": overlay_input}
        result = build_rendercv_dictionary(main_yaml, **kwargs)  # pyright: ignore[reportArgumentType]
        # Verify overlay replaced the main input for that key
        assert result[overlay_key] == overlay_content[overlay_key]
        # Verify cv remains unchanged
        assert result["cv"]["name"] == "John Doe"

    def test_all_overlays_simultaneously(self, create_yaml_file_fixture):
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
            "locale": {"language": "english"},
            "settings": {"render_command": {"pdf_path": "original.pdf"}},
        }
        design_overlay = {"design": {"theme": "sb2nov"}}
        locale_overlay = {"locale": {"language": "turkish"}}
        settings_overlay = {
            "settings": {"render_command": {"pdf_path": "replaced.pdf"}}
        }

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        design_file = create_yaml_file_fixture("design.yaml", design_overlay)
        locale_file = create_yaml_file_fixture("locale.yaml", locale_overlay)
        settings_file = create_yaml_file_fixture("settings.yaml", settings_overlay)

        result = build_rendercv_dictionary(
            main_file,
            design_file_path_or_contents=design_file,
            locale_file_path_or_contents=locale_file,
            settings_file_path_or_contents=settings_file,
        )

        assert result["cv"]["name"] == "John Doe"
        assert result["design"]["theme"] == "sb2nov"
        assert result["locale"]["language"] == "turkish"
        assert result["settings"]["render_command"]["pdf_path"] == "replaced.pdf"

    @pytest.mark.parametrize(
        ("override_key", "override_value"),
        [
            ("typst_path", "custom.typ"),
            ("pdf_path", "output.pdf"),
            ("markdown_path", "output.md"),
            ("html_path", "output.html"),
            ("png_path", "output.png"),
            ("dont_generate_html", True),
            ("dont_generate_markdown", True),
            ("dont_generate_pdf", True),
            ("dont_generate_png", True),
        ],
    )
    def test_render_command_single_override(
        self, minimal_input_dict, override_key, override_value
    ):
        yaml_input = dictionary_to_yaml(minimal_input_dict)

        kwargs = {override_key: override_value}
        result = build_rendercv_dictionary(yaml_input, **kwargs)

        assert result["settings"]["render_command"][override_key] == override_value

    def test_render_command_multiple_overrides(self, minimal_input_dict):
        yaml_input = dictionary_to_yaml(minimal_input_dict)

        result = build_rendercv_dictionary(
            yaml_input,
            pdf_path="output.pdf",
            typst_path="output.typ",
            dont_generate_html=True,
            dont_generate_markdown=True,
        )

        render_cmd = result["settings"]["render_command"]
        assert render_cmd["pdf_path"] == "output.pdf"
        assert render_cmd["typst_path"] == "output.typ"
        assert render_cmd["dont_generate_html"] is True
        assert render_cmd["dont_generate_markdown"] is True

    def test_render_command_preserves_existing_settings(self):
        input_dict = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
            "settings": {
                "render_command": {"pdf_path": "existing.pdf"},
                "other_setting": "preserved",
            },
        }
        yaml_input = dictionary_to_yaml(input_dict)

        result = build_rendercv_dictionary(yaml_input, typst_path="new.typ")

        assert result["settings"]["render_command"]["typst_path"] == "new.typ"
        assert result["settings"]["other_setting"] == "preserved"

    def test_combined_overlays_and_render_overrides(self, create_yaml_file_fixture):
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
        }
        locale_overlay = {"locale": {"language": "turkish"}}

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        locale_file = create_yaml_file_fixture("locale.yaml", locale_overlay)

        result = build_rendercv_dictionary(
            main_file,
            locale_file_path_or_contents=locale_file,
            pdf_path="custom.pdf",
            dont_generate_png=True,
        )

        assert result["locale"]["language"] == "turkish"
        assert result["settings"]["render_command"]["pdf_path"] == "custom.pdf"
        assert result["settings"]["render_command"]["dont_generate_png"] is True


class TestBuildRendercvModelFromDictionary:
    def test_basic_model_creation_without_optionals(self, minimal_input_dict):
        model = build_rendercv_model_from_dictionary(minimal_input_dict)

        assert isinstance(model, RenderCVModel)
        assert model.cv.name == "John Doe"
        assert model._input_file_path is None

    def test_with_input_file_path(self, minimal_input_dict, tmp_path):
        input_file_path = tmp_path / "test.yaml"

        model = build_rendercv_model_from_dictionary(
            minimal_input_dict, input_file_path
        )

        assert isinstance(model, RenderCVModel)
        assert model._input_file_path == input_file_path

    def test_without_input_file_path(self, minimal_input_dict):
        model = build_rendercv_model_from_dictionary(minimal_input_dict)

        assert model._input_file_path is None

    @pytest.mark.parametrize(
        "settings",
        [
            # Custom date provided
            {"current_date": Date(2023, 6, 15)},
            # No settings at all
            None,
            # Empty settings
            {},
        ],
    )
    def test_validation_context_current_date(self, minimal_input_dict, settings):
        input_dict = minimal_input_dict.copy()

        if settings is not None:
            input_dict["settings"] = settings

        # Should create model successfully regardless of current_date source
        model = build_rendercv_model_from_dictionary(input_dict)

        assert isinstance(model, RenderCVModel)
        # We can't directly verify the context after validation,
        # but the model should be created successfully

    def test_validation_context_with_input_file_path(
        self, minimal_input_dict, tmp_path
    ):
        input_file_path = tmp_path / "test.yaml"
        custom_date = Date(2024, 3, 10)

        input_dict = {
            **minimal_input_dict,
            "settings": {"current_date": custom_date},
        }

        model = build_rendercv_model_from_dictionary(input_dict, input_file_path)

        assert isinstance(model, RenderCVModel)
        assert model._input_file_path == input_file_path


class TestBuildRendercvModel:
    @pytest.mark.parametrize(
        "input_type",
        ["string", "file"],
    )
    def test_basic_model_creation(
        self, minimal_input_dict, create_yaml_file_fixture, input_type
    ):
        if input_type == "string":
            yaml_input = dictionary_to_yaml(minimal_input_dict)
            expected_file_path = None
        else:  # file
            yaml_input = create_yaml_file_fixture("input.yaml", minimal_input_dict)
            expected_file_path = yaml_input

        model = build_rendercv_model(yaml_input)

        assert isinstance(model, RenderCVModel)
        assert model.cv.name == "John Doe"
        assert model._input_file_path == expected_file_path

    @pytest.mark.parametrize("overlay_type", ["string", "file"])
    @pytest.mark.parametrize("overlay_key", ["design", "locale", "settings"])
    def test_with_single_overlay(
        self, minimal_input_dict, create_yaml_file_fixture, overlay_type, overlay_key
    ):
        overlay_content = {
            "design": {"design": {"theme": "sb2nov"}},
            "locale": {"locale": {"language": "turkish"}},
            "settings": {"settings": {"render_command": {"pdf_path": "custom.pdf"}}},
        }[overlay_key]

        main_yaml = dictionary_to_yaml(minimal_input_dict)

        if overlay_type == "string":
            overlay_input = dictionary_to_yaml(overlay_content)
        else:  # file
            overlay_input = create_yaml_file_fixture(
                f"{overlay_key}.yaml", overlay_content
            )

        kwargs = {f"{overlay_key}_file_path_or_contents": overlay_input}
        model = build_rendercv_model(main_yaml, **kwargs)  # pyright: ignore[reportArgumentType]

        assert isinstance(model, RenderCVModel)

    def test_with_all_overlays(self, create_yaml_file_fixture):
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
            "locale": {"language": "english"},
        }
        design_overlay = {"design": {"theme": "sb2nov"}}
        locale_overlay = {"locale": {"language": "turkish"}}
        settings_overlay = {
            "settings": {"render_command": {"markdown_path": "custom.md"}}
        }

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        design_file = create_yaml_file_fixture("design.yaml", design_overlay)
        locale_file = create_yaml_file_fixture("locale.yaml", locale_overlay)
        settings_file = create_yaml_file_fixture("settings.yaml", settings_overlay)

        model = build_rendercv_model(
            main_file,
            design_file_path_or_contents=design_file,
            locale_file_path_or_contents=locale_file,
            settings_file_path_or_contents=settings_file,
        )

        assert isinstance(model, RenderCVModel)
        assert model.cv.name == "John Doe"
        assert model.design.theme == "sb2nov"
        assert model._input_file_path == main_file

    @pytest.mark.parametrize(
        "overrides",
        [
            {"pdf_path": "custom.pdf"},
            {"typst_path": "custom.typ", "markdown_path": "custom.md"},
            {"dont_generate_html": True, "dont_generate_pdf": True},
            {
                "pdf_path": "all.pdf",
                "typst_path": "all.typ",
                "dont_generate_png": True,
            },
        ],
    )
    def test_with_render_command_overrides(self, minimal_input_dict, overrides):
        main_yaml = dictionary_to_yaml(minimal_input_dict)

        model = build_rendercv_model(main_yaml, **overrides)

        assert isinstance(model, RenderCVModel)
        # Verify overrides are in the model
        for key, value in overrides.items():
            model_value = getattr(model.settings.render_command, key)
            # Path fields are converted to Path objects
            if isinstance(value, str) and key.endswith("_path"):
                assert model_value == pathlib.Path(value)
            else:
                assert model_value == value

    def test_combined_overlays_and_overrides(
        self, minimal_input_dict, create_yaml_file_fixture
    ):
        locale_overlay = {"locale": {"language": "turkish"}}

        main_file = create_yaml_file_fixture("main.yaml", minimal_input_dict)
        locale_file = create_yaml_file_fixture("locale.yaml", locale_overlay)

        model = build_rendercv_model(
            main_file,
            locale_file_path_or_contents=locale_file,
            pdf_path="output.pdf",
            dont_generate_html=True,
        )

        assert isinstance(model, RenderCVModel)
        assert model._input_file_path == main_file
        # When using file path, paths are resolved relative to input file
        assert model.settings.render_command.pdf_path.name == "output.pdf"
        assert model.settings.render_command.dont_generate_html is True

    def test_with_fixture_input_file(self, input_file_path):
        model = build_rendercv_model(input_file_path)
        assert isinstance(model, RenderCVModel)

    def test_with_yaml_string_using_ruamel(self):
        input_dictionary = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
        }

        yaml_object = ruamel.yaml.YAML()
        yaml_object.width = 60
        yaml_object.indent(mapping=2, sequence=4, offset=2)
        with io.StringIO() as string_stream:
            yaml_object.dump(input_dictionary, string_stream)
            yaml_string = string_stream.getvalue()

        model = build_rendercv_model(yaml_string)
        assert isinstance(model, RenderCVModel)

    def test_invalid_file_extension_raises_error(self, tmp_path):
        invalid_file_path = tmp_path / "invalid.extension"
        invalid_file_path.write_text("dummy content", encoding="utf-8")

        with pytest.raises(ValueError):  # noqa: PT011
            build_rendercv_model(invalid_file_path)

    def test_nonexistent_file_raises_error(self, tmp_path):
        non_existent_file_path = tmp_path / "non_existent_file.yaml"

        with pytest.raises(FileNotFoundError):
            build_rendercv_model(non_existent_file_path)
