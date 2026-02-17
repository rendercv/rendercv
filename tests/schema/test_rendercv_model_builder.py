import io
import pathlib
from datetime import date as Date

import pytest
import ruamel.yaml

from rendercv.exception import RenderCVUserError, RenderCVUserValidationError
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


class TestBuildRendercvDictionary:
    def test_basic_input(self, minimal_input_dict):
        yaml_input = dictionary_to_yaml(minimal_input_dict)

        result, _ = build_rendercv_dictionary(yaml_input)

        assert result["cv"]["name"] == "John Doe"
        assert result["design"]["theme"] == "classic"

    def test_ensures_settings_and_render_command_exist(self, minimal_input_dict):
        yaml_input = dictionary_to_yaml(minimal_input_dict)

        result, _ = build_rendercv_dictionary(yaml_input)

        assert "settings" in result
        assert "render_command" in result["settings"]

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
    def test_single_overlay(self, minimal_input_dict, overlay_key, overlay_content):
        main_input = {
            **minimal_input_dict,
            "locale": {"language": "english"},
            "settings": {"original_setting": "original"},
        }
        main_yaml = dictionary_to_yaml(main_input)
        overlay_yaml = dictionary_to_yaml(overlay_content)

        kwargs = {f"{overlay_key}_yaml_file": overlay_yaml}
        result, _ = build_rendercv_dictionary(main_yaml, **kwargs)  # pyright: ignore[reportArgumentType]

        assert result[overlay_key] == overlay_content[overlay_key]
        assert result["cv"]["name"] == "John Doe"

    def test_design_overlay_replaces_original(self, minimal_input_dict):
        main_yaml = dictionary_to_yaml(minimal_input_dict)
        design_yaml = dictionary_to_yaml({"design": {"theme": "sb2nov"}})

        result, _ = build_rendercv_dictionary(main_yaml, design_yaml_file=design_yaml)

        assert result["design"]["theme"] == "sb2nov"

    def test_locale_overlay_replaces_original(self, minimal_input_dict):
        main_input = {**minimal_input_dict, "locale": {"language": "english"}}
        main_yaml = dictionary_to_yaml(main_input)
        locale_yaml = dictionary_to_yaml({"locale": {"language": "turkish"}})

        result, _ = build_rendercv_dictionary(main_yaml, locale_yaml_file=locale_yaml)

        assert result["locale"]["language"] == "turkish"

    def test_all_overlays_simultaneously(self, minimal_input_dict):
        main_input = {
            **minimal_input_dict,
            "locale": {"language": "english"},
            "settings": {"render_command": {"pdf_path": "original.pdf"}},
        }
        design_overlay = {"design": {"theme": "sb2nov"}}
        locale_overlay = {"locale": {"language": "turkish"}}

        main_yaml = dictionary_to_yaml(main_input)
        design_yaml = dictionary_to_yaml(design_overlay)
        locale_yaml = dictionary_to_yaml(locale_overlay)

        result, _ = build_rendercv_dictionary(
            main_yaml,
            design_yaml_file=design_yaml,
            locale_yaml_file=locale_yaml,
        )

        assert result["cv"]["name"] == "John Doe"
        assert result["design"]["theme"] == "sb2nov"
        assert result["locale"]["language"] == "turkish"

    def test_settings_overlay_with_design_overlay(self, minimal_input_dict):
        main_yaml = dictionary_to_yaml(minimal_input_dict)
        settings_yaml = dictionary_to_yaml({"settings": {"current_date": "2024-01-01"}})
        design_yaml = dictionary_to_yaml({"design": {"theme": "sb2nov"}})

        result, _ = build_rendercv_dictionary(
            main_yaml,
            settings_yaml_file=settings_yaml,
            design_yaml_file=design_yaml,
        )

        assert result["settings"]["current_date"] == "2024-01-01"
        assert result["design"]["theme"] == "sb2nov"

    def test_none_overlays_are_ignored(self, minimal_input_dict):
        yaml_input = dictionary_to_yaml(minimal_input_dict)

        result, _ = build_rendercv_dictionary(
            yaml_input,
            design_yaml_file=None,
            locale_yaml_file=None,
            settings_yaml_file=None,
        )

        assert result["cv"]["name"] == "John Doe"
        assert result["design"]["theme"] == "classic"

    def test_invalid_main_yaml_raises_validation_error(self):
        invalid_main_yaml = "cv:\n  name: John Doe\n   phone: 123"

        with pytest.raises(RenderCVUserValidationError) as exc_info:
            build_rendercv_dictionary(invalid_main_yaml)

        assert len(exc_info.value.validation_errors) == 1
        error = exc_info.value.validation_errors[0]
        assert error.schema_location is None
        assert error.yaml_source == "main_yaml_file"
        assert error.yaml_location is not None

    def test_invalid_overlay_yaml_raises_validation_error(self, minimal_input_dict):
        main_yaml = dictionary_to_yaml(minimal_input_dict)
        invalid_design_yaml = "design:\n  theme: classic\n   show_timespan_in: bad"

        with pytest.raises(RenderCVUserValidationError) as exc_info:
            build_rendercv_dictionary(main_yaml, design_yaml_file=invalid_design_yaml)

        assert len(exc_info.value.validation_errors) == 1
        error = exc_info.value.validation_errors[0]
        assert error.schema_location is None
        assert error.yaml_source == "design_yaml_file"
        assert error.yaml_location is not None

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
        result, _ = build_rendercv_dictionary(yaml_input, **kwargs)

        assert result["settings"]["render_command"][override_key] == override_value

    def test_render_command_multiple_overrides(self, minimal_input_dict):
        yaml_input = dictionary_to_yaml(minimal_input_dict)

        result, _ = build_rendercv_dictionary(
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

        result, _ = build_rendercv_dictionary(yaml_input, typst_path="new.typ")

        assert result["settings"]["render_command"]["typst_path"] == "new.typ"
        assert result["settings"]["other_setting"] == "preserved"

    def test_combined_overlays_and_render_overrides(self, minimal_input_dict):
        main_yaml = dictionary_to_yaml(minimal_input_dict)
        locale_yaml = dictionary_to_yaml({"locale": {"language": "turkish"}})

        result, _ = build_rendercv_dictionary(
            main_yaml,
            locale_yaml_file=locale_yaml,
            pdf_path="custom.pdf",
            dont_generate_png=True,
        )

        assert result["locale"]["language"] == "turkish"
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

        result, _ = build_rendercv_dictionary(yaml_input, overrides=overrides)

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

        result, _ = build_rendercv_dictionary(
            yaml_input,
            overrides={
                "cv.sections.education.0.institution": "Harvard",
                "cv.sections.education.0.degree": "MS",
            },
        )

        assert result["cv"]["sections"]["education"][0]["institution"] == "Harvard"
        assert result["cv"]["sections"]["education"][0]["degree"] == "MS"
        assert result["cv"]["name"] == "John Doe"

    @pytest.mark.parametrize(
        ("overlay_key", "main_value", "overlay_value"),
        [
            (
                "design",
                {"design": {"theme": "classic"}},
                {"design": {"theme": "sb2nov"}},
            ),
            (
                "locale",
                {"locale": {"language": "english"}},
                {"locale": {"language": "turkish"}},
            ),
            (
                "settings",
                {"settings": {"render_command": {"pdf_path": "original.pdf"}}},
                {"settings": {"render_command": {"pdf_path": "overlay.pdf"}}},
            ),
        ],
    )
    def test_overlay_fully_replaces_main_section(
        self, minimal_input_dict, overlay_key, main_value, overlay_value
    ):
        main_input = {**minimal_input_dict, **main_value}
        main_yaml = dictionary_to_yaml(main_input)
        overlay_yaml = dictionary_to_yaml(overlay_value)

        kwargs = {f"{overlay_key}_yaml_file": overlay_yaml}
        result, _ = build_rendercv_dictionary(main_yaml, **kwargs)  # pyright: ignore[reportArgumentType]

        assert result[overlay_key] == overlay_value[overlay_key]

    def test_overlay_replaces_not_merges(self, minimal_input_dict):
        main_input = {
            **minimal_input_dict,
            "design": {"theme": "classic", "font_size": "12pt"},
        }
        main_yaml = dictionary_to_yaml(main_input)
        design_yaml = dictionary_to_yaml({"design": {"theme": "sb2nov"}})

        result, _ = build_rendercv_dictionary(main_yaml, design_yaml_file=design_yaml)

        assert result["design"] == {"theme": "sb2nov"}
        assert "font_size" not in result["design"]


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

    def test_invalid_input_raises_validation_error(self):
        invalid_dict = {"cv": {"name": 123}, "design": {"theme": "nonexistent_theme"}}

        with pytest.raises(RenderCVUserValidationError):
            build_rendercv_model_from_commented_map(invalid_dict)


class TestBuildRendercvModel:
    def test_basic_model_creation(self, minimal_input_dict):
        yaml_input = dictionary_to_yaml(minimal_input_dict)

        _, model = build_rendercv_dictionary_and_model(yaml_input)

        assert isinstance(model, RenderCVModel)
        assert model.cv.name == "John Doe"
        assert model._input_file_path is None

    def test_basic_model_creation_with_input_file_path(
        self, minimal_input_dict, tmp_path
    ):
        yaml_input = dictionary_to_yaml(minimal_input_dict)
        file_path = tmp_path / "input.yaml"

        _, model = build_rendercv_dictionary_and_model(
            yaml_input, input_file_path=file_path
        )

        assert isinstance(model, RenderCVModel)
        assert model._input_file_path == file_path

    @pytest.mark.parametrize(
        "overlay_key",
        ["design", "locale", "settings"],
    )
    def test_with_single_overlay(self, minimal_input_dict, overlay_key):
        overlay_content = {
            "design": {"design": {"theme": "sb2nov"}},
            "locale": {"locale": {"language": "turkish"}},
            "settings": {"settings": {"render_command": {"pdf_path": "custom.pdf"}}},
        }[overlay_key]

        main_yaml = dictionary_to_yaml(minimal_input_dict)
        overlay_yaml = dictionary_to_yaml(overlay_content)

        kwargs = {f"{overlay_key}_yaml_file": overlay_yaml}
        _, model = build_rendercv_dictionary_and_model(main_yaml, **kwargs)  # ty: ignore[invalid-argument-type]

        assert isinstance(model, RenderCVModel)

    def test_with_all_overlays(self):
        main_input = {
            "cv": {"name": "John Doe"},
            "design": {"theme": "classic"},
            "locale": {"language": "english"},
        }
        main_yaml = dictionary_to_yaml(main_input)
        design_yaml = dictionary_to_yaml({"design": {"theme": "sb2nov"}})
        locale_yaml = dictionary_to_yaml({"locale": {"language": "turkish"}})

        _, model = build_rendercv_dictionary_and_model(
            main_yaml,
            design_yaml_file=design_yaml,
            locale_yaml_file=locale_yaml,
        )

        assert isinstance(model, RenderCVModel)
        assert model.cv.name == "John Doe"
        assert model.design.theme == "sb2nov"

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

    def test_combined_overlays_and_overrides(self, minimal_input_dict):
        main_yaml = dictionary_to_yaml(minimal_input_dict)
        locale_yaml = dictionary_to_yaml({"locale": {"language": "turkish"}})

        _, model = build_rendercv_dictionary_and_model(
            main_yaml,
            locale_yaml_file=locale_yaml,
            pdf_path="output.pdf",
            dont_generate_html=True,
        )

        assert isinstance(model, RenderCVModel)
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
        yaml_content = input_file_path.read_text(encoding="utf-8")
        _, model = build_rendercv_dictionary_and_model(
            yaml_content, input_file_path=input_file_path
        )
        assert isinstance(model, RenderCVModel)
        assert model._input_file_path == input_file_path

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

    def test_empty_yaml_raises_error(self):
        with pytest.raises(RenderCVUserError):
            build_rendercv_dictionary_and_model("")

    def test_invalid_yaml_raises_error(self):
        with pytest.raises(RenderCVUserValidationError):
            build_rendercv_dictionary_and_model("cv:\n  name: 123\n")

    def test_design_overlay_merges_into_dictionary_and_model(self, minimal_input_dict):
        main_yaml = dictionary_to_yaml(minimal_input_dict)
        design_yaml = dictionary_to_yaml({"design": {"theme": "sb2nov"}})

        dictionary, model = build_rendercv_dictionary_and_model(
            main_yaml,
            design_yaml_file=design_yaml,
        )

        # Overlay content should be merged directly into dictionary
        assert dictionary["design"]["theme"] == "sb2nov"
        # No file path should be stored in settings.render_command
        assert "design" not in dictionary["settings"]["render_command"]
        # Model should reflect the overlay
        assert model.design.theme == "sb2nov"

    def test_design_overlay_with_settings_overlay(self, minimal_input_dict):
        main_yaml = dictionary_to_yaml(minimal_input_dict)
        settings_yaml = dictionary_to_yaml(
            {
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
        )
        design_yaml = dictionary_to_yaml({"design": {"theme": "sb2nov"}})

        _, model = build_rendercv_dictionary_and_model(
            main_yaml,
            settings_yaml_file=settings_yaml,
            design_yaml_file=design_yaml,
        )

        assert model.design.theme == "sb2nov"

    def test_locale_overlay_merges_into_dictionary_and_model(self, minimal_input_dict):
        main_input = {**minimal_input_dict, "locale": {"language": "english"}}
        main_yaml = dictionary_to_yaml(main_input)
        locale_yaml = dictionary_to_yaml({"locale": {"language": "turkish"}})

        dictionary, model = build_rendercv_dictionary_and_model(
            main_yaml,
            locale_yaml_file=locale_yaml,
        )

        # Overlay content should be merged directly into dictionary
        assert dictionary["locale"]["language"] == "turkish"
        # No file path should be stored in settings.render_command
        assert "locale" not in dictionary["settings"]["render_command"]
        # Model should reflect the overlay
        assert model.locale.language == "turkish"

    def test_both_design_and_locale_overlays(self, minimal_input_dict):
        main_input = {**minimal_input_dict, "locale": {"language": "english"}}
        main_yaml = dictionary_to_yaml(main_input)
        design_yaml = dictionary_to_yaml({"design": {"theme": "engineeringresumes"}})
        locale_yaml = dictionary_to_yaml({"locale": {"language": "turkish"}})

        dictionary, model = build_rendercv_dictionary_and_model(
            main_yaml,
            design_yaml_file=design_yaml,
            locale_yaml_file=locale_yaml,
        )

        assert dictionary["design"]["theme"] == "engineeringresumes"
        assert dictionary["locale"]["language"] == "turkish"
        assert model.design.theme == "engineeringresumes"
        assert model.locale.language == "turkish"

    def test_design_overlay_independent_of_locale_overlay(self, minimal_input_dict):
        """Design and locale overlays should merge independently."""
        main_input = {**minimal_input_dict, "locale": {"language": "english"}}
        main_yaml = dictionary_to_yaml(main_input)
        design_yaml = dictionary_to_yaml({"design": {"theme": "sb2nov"}})

        dictionary, model = build_rendercv_dictionary_and_model(
            main_yaml,
            design_yaml_file=design_yaml,
        )

        # Design should be overridden
        assert dictionary["design"]["theme"] == "sb2nov"
        assert model.design.theme == "sb2nov"
        # Locale should remain original
        assert dictionary["locale"]["language"] == "english"

    @pytest.mark.parametrize(
        ("overlay_key", "main_section", "overlay_section", "check"),
        [
            (
                "design",
                {"theme": "classic"},
                {"theme": "sb2nov"},
                lambda m: m.design.theme == "sb2nov",
            ),
            (
                "locale",
                {"language": "english"},
                {"language": "turkish"},
                lambda m: m.locale.language == "turkish",
            ),
        ],
    )
    def test_overlay_overrides_main_in_model(
        self, minimal_input_dict, overlay_key, main_section, overlay_section, check
    ):
        main_input = {**minimal_input_dict, overlay_key: main_section}
        main_yaml = dictionary_to_yaml(main_input)
        overlay_yaml = dictionary_to_yaml({overlay_key: overlay_section})

        kwargs = {f"{overlay_key}_yaml_file": overlay_yaml}
        _, model = build_rendercv_dictionary_and_model(main_yaml, **kwargs)  # ty: ignore[invalid-argument-type]

        assert check(model)
