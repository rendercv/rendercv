import io
import pathlib
from datetime import date as Date

import pytest
import ruamel.yaml

from rendercv.exception import RenderCVUserError
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.rendercv_model_builder import (
    build_rendercv_dictionary,
    build_rendercv_dictionary_and_model,
    build_rendercv_model_from_commented_map,
)
from rendercv.schema.sample_generator import dictionary_to_yaml


@pytest.fixture
def minimal_input_dict():
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
        if input_type == "string" or overlay_key == "settings":
            overlay_input = dictionary_to_yaml(overlay_content)
        else:  # file
            overlay_input = create_yaml_file_fixture(
                f"{overlay_key}.yaml", overlay_content
            )

        kwargs = {f"{overlay_key}_file_path_or_contents": overlay_input}
        result = build_rendercv_dictionary(main_yaml, **kwargs)  # pyright: ignore[reportArgumentType]

        # Behavior differs based on input type:
        # - String: merges immediately into the dictionary
        # - Path: stores reference in settings.render_command for later loading
        if input_type == "string" or overlay_key == "settings":
            assert result[overlay_key] == overlay_content[overlay_key]
        else:  # file
            assert result["settings"]["render_command"][overlay_key] == overlay_input

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

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        design_file = create_yaml_file_fixture("design.yaml", design_overlay)
        locale_file = create_yaml_file_fixture("locale.yaml", locale_overlay)

        result = build_rendercv_dictionary(
            main_file,
            design_file_path_or_contents=design_file,
            locale_file_path_or_contents=locale_file,
        )

        assert result["cv"]["name"] == "John Doe"
        # File overlays are stored as paths in settings.render_command
        assert result["settings"]["render_command"]["design"] == design_file
        assert result["settings"]["render_command"]["locale"] == locale_file
        # Original values remain unchanged when using file overlays
        assert result["design"]["theme"] == "classic"
        assert result["locale"]["language"] == "english"

    def test_settings_overlay_without_render_command_allows_design_path_overlay(
        self, create_yaml_file_fixture
    ):
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
        }
        settings_overlay = {"settings": {"current_date": "2024-01-01"}}
        design_overlay = {"design": {"theme": "sb2nov"}}

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        settings_file = create_yaml_file_fixture("settings.yaml", settings_overlay)
        design_file = create_yaml_file_fixture("design.yaml", design_overlay)

        result = build_rendercv_dictionary(
            main_file,
            settings_file_path_or_contents=settings_file,
            design_file_path_or_contents=design_file,
        )

        assert result["settings"]["current_date"] == "2024-01-01"
        assert result["settings"]["render_command"]["design"] == design_file

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

        # File overlay is stored as path in settings.render_command
        assert result["settings"]["render_command"]["locale"] == locale_file
        assert result["settings"]["render_command"]["pdf_path"] == "custom.pdf"
        assert result["settings"]["render_command"]["dont_generate_png"] is True

    @pytest.mark.parametrize(
        ("overrides", "expected_checks"),
        [
            (
                {"cv.name": "Jane Doe"},
                [("cv", "name", "Jane Doe")],
            ),
            (
                {"design.theme": "sb2nov"},
                [("design", "theme", "sb2nov")],
            ),
            (
                {"cv.name": "Jane Doe", "design.theme": "engineeringresumes"},
                [("cv", "name", "Jane Doe"), ("design", "theme", "engineeringresumes")],
            ),
        ],
    )
    def test_overrides_parameter(self, minimal_input_dict, overrides, expected_checks):
        yaml_input = dictionary_to_yaml(minimal_input_dict)

        result = build_rendercv_dictionary(yaml_input, overrides=overrides)

        for path_and_value in expected_checks:
            value = result
            for key in path_and_value[:-1]:
                value = value[key]
            assert value == path_and_value[-1]

    def test_overrides_with_nested_paths(self, minimal_input_dict):
        input_dict = {
            **minimal_input_dict,
            "cv": {
                "name": "John Doe",
                "sections": {"education": [{"institution": "MIT", "degree": "PhD"}]},
            },
        }
        yaml_input = dictionary_to_yaml(input_dict)

        result = build_rendercv_dictionary(
            yaml_input,
            overrides={
                "cv.sections.education.0.institution": "Harvard",
                "cv.sections.education.0.degree": "MS",
            },
        )

        assert result["cv"]["sections"]["education"][0]["institution"] == "Harvard"
        assert result["cv"]["sections"]["education"][0]["degree"] == "MS"
        assert result["cv"]["name"] == "John Doe"


class TestBuildRendercvModelFromDictionary:
    def test_basic_model_creation_without_optionals(self, minimal_input_dict):
        model = build_rendercv_model_from_commented_map(minimal_input_dict)

        assert isinstance(model, RenderCVModel)
        assert model.cv.name == "John Doe"
        assert model._input_file_path is None

    def test_with_input_file_path(self, minimal_input_dict, tmp_path):
        input_file_path = tmp_path / "test.yaml"

        model = build_rendercv_model_from_commented_map(
            minimal_input_dict, input_file_path
        )

        assert isinstance(model, RenderCVModel)
        assert model._input_file_path == input_file_path

    def test_without_input_file_path(self, minimal_input_dict):
        model = build_rendercv_model_from_commented_map(minimal_input_dict)

        assert model._input_file_path is None

    @pytest.mark.parametrize(
        "settings",
        [
            {"current_date": Date(2023, 6, 15)},
            None,
            {},
        ],
    )
    def test_validation_context_current_date(self, minimal_input_dict, settings):
        input_dict = minimal_input_dict.copy()

        if settings is not None:
            input_dict["settings"] = settings

        model = build_rendercv_model_from_commented_map(input_dict)

        assert isinstance(model, RenderCVModel)

    def test_validation_context_with_input_file_path(
        self, minimal_input_dict, tmp_path
    ):
        input_file_path = tmp_path / "test.yaml"
        custom_date = Date(2024, 3, 10)

        input_dict = {
            **minimal_input_dict,
            "settings": {"current_date": custom_date},
        }

        model = build_rendercv_model_from_commented_map(input_dict, input_file_path)  # pyright: ignore[reportArgumentType]

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

        _, model = build_rendercv_dictionary_and_model(yaml_input)

        assert isinstance(model, RenderCVModel)
        assert model.cv.name == "John Doe"
        assert model._input_file_path == expected_file_path

    @pytest.mark.parametrize(
        ("overlay_type", "overlay_key"),
        [
            ("string", "design"),
            ("string", "locale"),
            ("string", "settings"),
            ("file", "design"),
            ("file", "locale"),
            # Note: settings overlay via file is not supported
        ],
    )
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
        _, model = build_rendercv_dictionary_and_model(main_yaml, **kwargs)  # pyright: ignore[reportArgumentType]

        assert isinstance(model, RenderCVModel)

    def test_with_all_overlays(self, create_yaml_file_fixture):
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
            "locale": {"language": "english"},
        }
        design_overlay = {"design": {"theme": "sb2nov"}}
        locale_overlay = {"locale": {"language": "turkish"}}

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        design_file = create_yaml_file_fixture("design.yaml", design_overlay)
        locale_file = create_yaml_file_fixture("locale.yaml", locale_overlay)

        _, model = build_rendercv_dictionary_and_model(
            main_file,
            design_file_path_or_contents=design_file,
            locale_file_path_or_contents=locale_file,
        )

        assert isinstance(model, RenderCVModel)
        assert model.cv.name == "John Doe"
        # File overlays should be loaded and applied
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

        _, model = build_rendercv_dictionary_and_model(main_yaml, **overrides)

        assert isinstance(model, RenderCVModel)
        for key, value in overrides.items():
            model_value = getattr(model.settings.render_command, key)
            if isinstance(value, str) and key.endswith("_path"):
                assert model_value == pathlib.Path(value).resolve()
            else:
                assert model_value == value

    def test_combined_overlays_and_overrides(
        self, minimal_input_dict, create_yaml_file_fixture
    ):
        locale_overlay = {"locale": {"language": "turkish"}}

        main_file = create_yaml_file_fixture("main.yaml", minimal_input_dict)
        locale_file = create_yaml_file_fixture("locale.yaml", locale_overlay)

        _, model = build_rendercv_dictionary_and_model(
            main_file,
            locale_file_path_or_contents=locale_file,
            pdf_path="output.pdf",
            dont_generate_html=True,
        )

        assert isinstance(model, RenderCVModel)
        assert model._input_file_path == main_file
        assert model.settings.render_command.pdf_path.name == "output.pdf"
        assert model.settings.render_command.dont_generate_html is True

    @pytest.mark.parametrize(
        ("overrides", "expected_name"),
        [
            ({"cv.name": "Jane Doe"}, "Jane Doe"),
            ({"cv.name": "Bob Smith"}, "Bob Smith"),
        ],
    )
    def test_with_overrides_parameter(
        self, minimal_input_dict, overrides, expected_name
    ):
        yaml_input = dictionary_to_yaml(minimal_input_dict)

        _, model = build_rendercv_dictionary_and_model(yaml_input, overrides=overrides)

        assert isinstance(model, RenderCVModel)
        assert model.cv.name == expected_name

    def test_with_fixture_input_file(self, input_file_path):
        _, model = build_rendercv_dictionary_and_model(input_file_path)
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

        _, model = build_rendercv_dictionary_and_model(yaml_string)
        assert isinstance(model, RenderCVModel)

    def test_invalid_file_extension_raises_error(self, tmp_path):
        invalid_file_path = tmp_path / "invalid.extension"
        invalid_file_path.write_text("dummy content", encoding="utf-8")

        with pytest.raises(RenderCVUserError):
            build_rendercv_dictionary_and_model(invalid_file_path)

    def test_nonexistent_file_raises_error(self, tmp_path):
        non_existent_file_path = tmp_path / "non_existent_file.yaml"

        with pytest.raises(RenderCVUserError):
            build_rendercv_dictionary_and_model(non_existent_file_path)

    def test_design_file_overlay_loads_and_applies(self, create_yaml_file_fixture):
        """Test that design file overlay is loaded from settings.render_command.design and applied to model."""
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
        }
        design_overlay = {"design": {"theme": "sb2nov"}}

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        design_file = create_yaml_file_fixture("design.yaml", design_overlay)

        dictionary, model = build_rendercv_dictionary_and_model(
            main_file,
            design_file_path_or_contents=design_file,
        )

        # Dictionary should have file path stored, not the overlay content
        assert dictionary["settings"]["render_command"]["design"] == design_file
        assert dictionary["design"]["theme"] == "classic"  # Original unchanged

        # Model should have the design from the file applied
        assert model.design.theme == "sb2nov"

    def test_design_overlay_applies_with_settings_overlay(
        self, create_yaml_file_fixture
    ):
        """Ensure design overlay applies even when settings overlay is provided."""
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
        }
        settings_overlay = {
            "settings": {
                "render_command": {
                    "typst_path": "rendercv_output/NAME_IN_SNAKE_CASE_CV.typ",
                    "pdf_path": "rendercv_output/NAME_IN_SNAKE_CASE_CV.pdf",
                    "markdown_path": "rendercv_output/NAME_IN_SNAKE_CASE_CV.md",
                    "html_path": "rendercv_output/NAME_IN_SNAKE_CASE_CV.html",
                    "png_path": "rendercv_output/NAME_IN_SNAKE_CASE_CV.png",
                    "dont_generate_markdown": False,
                    "dont_generate_html": False,
                    "dont_generate_typst": False,
                    "dont_generate_pdf": False,
                    "dont_generate_png": False,
                }
            }
        }
        design_overlay = {"design": {"theme": "sb2nov"}}

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        settings_file = create_yaml_file_fixture("settings.yaml", settings_overlay)
        design_file = create_yaml_file_fixture("design.yaml", design_overlay)

        _, model = build_rendercv_dictionary_and_model(
            main_file,
            settings_file_path_or_contents=settings_file,
            design_file_path_or_contents=design_file,
        )

        assert model.design.theme != "classic"

    def test_locale_file_overlay_loads_and_applies(self, create_yaml_file_fixture):
        """Test that locale file overlay is loaded from settings.render_command.locale and applied to model."""
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
            "locale": {"language": "english"},
        }
        locale_overlay = {"locale": {"language": "turkish"}}

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        locale_file = create_yaml_file_fixture("locale.yaml", locale_overlay)

        dictionary, _ = build_rendercv_dictionary_and_model(
            main_file,
            locale_file_path_or_contents=locale_file,
        )

        # Dictionary should have file path stored, not the overlay content
        assert dictionary["settings"]["render_command"]["locale"] == locale_file
        assert dictionary["locale"]["language"] == "english"  # Original unchanged

        # Model should have the locale from the file applied
        # Note: locale is validated and merged, so we just verify it's applied

    def test_both_design_and_locale_file_overlays_load_and_apply(
        self, create_yaml_file_fixture
    ):
        """Test that both design and locale file overlays are loaded and applied together."""
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
            "locale": {"language": "english"},
        }
        design_overlay = {"design": {"theme": "engineeringresumes"}}
        locale_overlay = {"locale": {"language": "turkish"}}

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        design_file = create_yaml_file_fixture("design.yaml", design_overlay)
        locale_file = create_yaml_file_fixture("locale.yaml", locale_overlay)

        dictionary, model = build_rendercv_dictionary_and_model(
            main_file,
            design_file_path_or_contents=design_file,
            locale_file_path_or_contents=locale_file,
        )

        # Dictionary should have file paths stored
        assert dictionary["settings"]["render_command"]["design"] == design_file
        assert dictionary["settings"]["render_command"]["locale"] == locale_file
        assert dictionary["design"]["theme"] == "classic"  # Original unchanged
        assert dictionary["locale"]["language"] == "english"  # Original unchanged

        # Model should have both overlays applied
        assert model.design.theme == "engineeringresumes"

    def test_string_overlay_merges_immediately(self, create_yaml_file_fixture):
        """Test that string overlays are merged immediately into dictionary."""
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
        }
        design_overlay = {"design": {"theme": "sb2nov"}}

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        design_yaml = dictionary_to_yaml(design_overlay)

        dictionary, model = build_rendercv_dictionary_and_model(
            main_file,
            design_file_path_or_contents=design_yaml,
        )

        # Dictionary should have overlay content merged directly
        assert dictionary["design"]["theme"] == "sb2nov"
        # No file path should be stored
        assert "design" not in dictionary["settings"]["render_command"]

        # Model should have the design from the string overlay
        assert model.design.theme == "sb2nov"

    def test_mixed_string_and_file_overlays(self, create_yaml_file_fixture):
        """Test that string and file overlays can be used together."""
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
            "locale": {"language": "english"},
        }
        design_overlay = {"design": {"theme": "sb2nov"}}
        locale_overlay = {"locale": {"language": "turkish"}}

        main_file = create_yaml_file_fixture("main.yaml", main_input)
        design_yaml = dictionary_to_yaml(design_overlay)  # String
        locale_file = create_yaml_file_fixture("locale.yaml", locale_overlay)  # File

        dictionary, model = build_rendercv_dictionary_and_model(
            main_file,
            design_file_path_or_contents=design_yaml,
            locale_file_path_or_contents=locale_file,
        )

        # Design string overlay should be merged directly
        assert dictionary["design"]["theme"] == "sb2nov"
        assert "design" not in dictionary["settings"]["render_command"]

        # Locale file overlay should be stored as path
        assert dictionary["settings"]["render_command"]["locale"] == locale_file
        assert dictionary["locale"]["language"] == "english"  # Original unchanged

        # Both should be applied in the model
        assert model.design.theme == "sb2nov"
