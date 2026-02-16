import pytest
import ruamel.yaml

from rendercv.exception import RenderCVUserError
from rendercv.schema.models.design.built_in_design import (
    available_cover_themes,
    available_themes,
)
from rendercv.schema.models.locale.locale import available_locales
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.sample_generator import (
    create_sample_rendercv_pydantic_model,
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
            name="John Doe",
            theme=theme,
            locale=locale,
            cover=(theme in available_cover_themes),
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
            file_path=dummy_file_path,
            theme=theme,
            locale=locale,
            cover=(theme in available_cover_themes),
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
