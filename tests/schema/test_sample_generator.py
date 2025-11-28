import pytest
import ruamel.yaml

from rendercv.exception import RenderCVUserError
from rendercv.schema.models.design.built_in_design import available_themes
from rendercv.schema.models.locale.locale import available_locales
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.sample_generator import (
    create_sample_rendercv_pydantic_model,
    create_sample_yaml_input_file,
    dictionary_to_yaml,
)


@pytest.mark.parametrize(
    "theme",
    available_themes,
)
@pytest.mark.parametrize(
    "locale",
    available_locales,
)
def test_create_sample_rendercv_pydantic_model(theme, locale):
    data_model = create_sample_rendercv_pydantic_model(
        name="John Doe", theme=theme, locale=locale
    )
    assert isinstance(data_model, RenderCVModel)


def test_create_sample_rendercv_pydantic_model_invalid_theme_or_locale():
    with pytest.raises(ValueError):  # NOQA: PT011
        create_sample_rendercv_pydantic_model(
            name="John Doe", theme="invalid", locale="english"
        )
    with pytest.raises(ValueError):  # NOQA: PT011
        create_sample_rendercv_pydantic_model(
            name="John Doe", theme="classic", locale="invalid"
        )


@pytest.mark.parametrize(
    "theme",
    available_themes,
)
@pytest.mark.parametrize(
    "locale",
    available_locales,
)
def test_create_a_sample_yaml_input_file(tmp_path, theme, locale):
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
def test_create_sample_yaml_input_file_invalid_theme_or_locale(key):
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

    # load the yaml string
    yaml_object = ruamel.yaml.YAML()
    output_dictionary = yaml_object.load(yaml_string)

    assert input_dictionary == output_dictionary
