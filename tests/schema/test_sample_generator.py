import pytest
import ruamel.yaml

from rendercv.exception import RenderCVUserError
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.locale.locale import available_locales
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.sample_generator import (
    create_sample_cv_file,
    create_sample_design_file,
    create_sample_locale_file,
    create_sample_rendercv_pydantic_model,
    create_sample_settings_file,
    create_sample_yaml_file,
    create_sample_yaml_input_file,
    dictionary_to_yaml,
)


class TestCreateSampleRendercvPydanticModel:
    @pytest.mark.parametrize(
        "theme",
        available_themes,
    )
    @pytest.mark.parametrize(
        "locale",
        available_locales,
    )
    def test_creates_valid_model_for_all_themes_and_locales(self, theme, locale):
        data_model = create_sample_rendercv_pydantic_model(
            name="John Doe", theme=theme, locale=locale
        )
        assert isinstance(data_model, RenderCVModel)

    def test_rejects_invalid_theme_or_locale(self):
        with pytest.raises(ValueError):  # NOQA: PT011
            create_sample_rendercv_pydantic_model(
                name="John Doe", theme="invalid", locale="english"
            )
        with pytest.raises(ValueError):  # NOQA: PT011
            create_sample_rendercv_pydantic_model(
                name="John Doe", theme="classic", locale="invalid"
            )

    def test_creates_model_with_unicode_name(self):
        name = "Matías"
        data_model = create_sample_rendercv_pydantic_model(name=name)
        assert data_model.cv.name == name


class TestCreateSampleYamlInputFile:
    @pytest.mark.parametrize(
        "theme",
        available_themes,
    )
    @pytest.mark.parametrize(
        "locale",
        available_locales,
    )
    def test_creates_valid_yaml_file_for_all_themes_and_locales(
        self, tmp_path, theme, locale
    ):
        dummy_file_path = tmp_path / "dummy.yaml"
        yaml_contents = create_sample_yaml_input_file(
            file_path=dummy_file_path, theme=theme, locale=locale
        )

        assert dummy_file_path.exists()
        assert yaml_contents == dummy_file_path.read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        "key",
        ["theme", "locale"],
    )
    def test_rejects_invalid_theme_or_locale(self, key):
        with pytest.raises(RenderCVUserError):
            create_sample_yaml_input_file(file_path=None, **{key: "invalid"})


class TestCreateSampleYamlFile:
    def test_writes_file_and_returns_matching_content(self, tmp_path):
        dictionary = {"key": "value", "list": [1, 2, 3]}
        file_path = tmp_path / "test.yaml"
        result = create_sample_yaml_file(dictionary=dictionary, file_path=file_path)

        assert file_path.exists()
        assert result == file_path.read_text(encoding="utf-8")

    def test_returns_string_without_file(self):
        dictionary = {"key": "value"}
        result = create_sample_yaml_file(dictionary=dictionary, file_path=None)

        yaml_object = ruamel.yaml.YAML()
        assert yaml_object.load(result) == dictionary


class TestCreateSampleCvFile:
    def test_creates_valid_yaml_with_only_cv_key(self, tmp_path):
        file_path = tmp_path / "cv.yaml"
        result = create_sample_cv_file(file_path=file_path, name="Jane Smith")

        assert file_path.exists()
        assert result == file_path.read_text(encoding="utf-8")

        yaml_object = ruamel.yaml.YAML()
        data = yaml_object.load(result)
        assert list(data.keys()) == ["cv"]
        assert data["cv"]["name"] == "Jane Smith"


class TestCreateSampleDesignFile:
    @pytest.mark.parametrize(
        "theme",
        available_themes,
    )
    def test_creates_valid_yaml_for_all_themes(self, tmp_path, theme):
        file_path = tmp_path / "design.yaml"
        result = create_sample_design_file(file_path=file_path, theme=theme)

        assert file_path.exists()
        assert result == file_path.read_text(encoding="utf-8")

        yaml_object = ruamel.yaml.YAML()
        data = yaml_object.load(result)
        assert list(data.keys()) == ["design"]
        assert data["design"]["theme"] == theme

    def test_rejects_invalid_theme(self):
        with pytest.raises(RenderCVUserError):
            create_sample_design_file(file_path=None, theme="invalid")


class TestCreateSampleLocaleFile:
    @pytest.mark.parametrize(
        "locale",
        available_locales,
    )
    def test_creates_valid_yaml_for_all_locales(self, tmp_path, locale):
        file_path = tmp_path / "locale.yaml"
        result = create_sample_locale_file(file_path=file_path, locale=locale)

        assert file_path.exists()
        assert result == file_path.read_text(encoding="utf-8")

        yaml_object = ruamel.yaml.YAML()
        data = yaml_object.load(result)
        assert list(data.keys()) == ["locale"]
        assert data["locale"]["language"] == locale

    def test_rejects_invalid_locale(self):
        with pytest.raises(RenderCVUserError):
            create_sample_locale_file(file_path=None, locale="invalid")


class TestCreateSampleSettingsFile:
    def test_creates_valid_yaml_with_only_settings_key(self, tmp_path):
        file_path = tmp_path / "settings.yaml"
        result = create_sample_settings_file(file_path=file_path)

        assert file_path.exists()
        assert result == file_path.read_text(encoding="utf-8")

        yaml_object = ruamel.yaml.YAML()
        data = yaml_object.load(result)
        assert list(data.keys()) == ["settings"]


def test_dictionary_to_yaml():
    input_dictionary = {
        "test_list": [
            "a",
            "b",
            "c",
        ],
        "test_dict": {
            "a": 1,
            "b": 2,
        },
    }
    yaml_string = dictionary_to_yaml(input_dictionary)

    yaml_object = ruamel.yaml.YAML()
    output_dictionary = yaml_object.load(yaml_string)

    assert input_dictionary == output_dictionary
