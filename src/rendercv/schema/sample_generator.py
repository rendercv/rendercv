import io
import json
import pathlib
import re
from typing import overload

import ruamel.yaml

from rendercv import __version__
from rendercv.exception import RenderCVUserError

from .models.cv.cv import Cv
from .models.design.built_in_design import available_themes, built_in_design_adapter
from .models.locale.locale import available_locales, locale_adapter
from .models.rendercv_model import RenderCVModel
from .rendercv_model_builder import read_yaml


def dictionary_to_yaml(dictionary: dict) -> str:
    """Convert dictionary to formatted YAML string with multiline preservation.

    Why:
        Sample YAML generation must produce readable output with proper
        formatting for multiline strings. Custom representer ensures
        bullet points and descriptions use pipe syntax.

    Args:
        dictionary: Data structure to convert.

    Returns:
        Formatted YAML string.
    """

    # Source: https://gist.github.com/alertedsnake/c521bc485b3805aa3839aef29e39f376
    def str_representer(dumper, data):
        if len(data.splitlines()) > 1:  # check for multiline string
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml_object = ruamel.yaml.YAML()
    yaml_object.encoding = "utf-8"
    yaml_object.width = 9999
    yaml_object.indent(mapping=2, sequence=4, offset=2)
    yaml_object.representer.add_representer(str, str_representer)

    with io.StringIO() as string_stream:
        yaml_object.dump(dictionary, string_stream)
        return string_stream.getvalue()


def create_sample_rendercv_pydantic_model(
    *, name: str = "John Doe", theme: str = "classic", locale: str = "english"
) -> RenderCVModel:
    """Build sample CV model from sample content.

    Why:
        New users need working examples to understand structure. Sample content
        provides realistic content that validates successfully and renders
        to all output formats without errors.

    Args:
        name: Person's full name.
        theme: Design theme identifier.
        locale: Locale language identifier.

    Returns:
        Validated model with sample content.
    """
    sample_content = pathlib.Path(__file__).parent / "sample_content.yaml"
    sample_content_dictionary = read_yaml(sample_content)["cv"]
    cv = Cv(**sample_content_dictionary)

    cv.name = name

    design = built_in_design_adapter.validate_python({"theme": theme})
    validated_locale = locale_adapter.validate_python({"language": locale})

    return RenderCVModel(cv=cv, design=design, locale=validated_locale)


@overload
def create_sample_yaml_input_file(
    *,
    file_path: None,
    name: str = "John Doe",
    theme: str = "classic",
    locale: str = "english",
) -> str: ...
@overload
def create_sample_yaml_input_file(
    *,
    file_path: pathlib.Path,
    name: str = "John Doe",
    theme: str = "classic",
    locale: str = "english",
) -> None: ...
def create_sample_yaml_input_file(
    *,
    file_path: pathlib.Path | None = None,
    name: str = "John Doe",
    theme: str = "classic",
    locale: str = "english",
) -> str | None:
    """Generate formatted sample YAML with schema hint and commented design options.

    Why:
        New command provides users with immediately usable CV templates.
        JSON schema hint enables IDE autocompletion, commented design
        fields show customization options without overwhelming beginners.

    Example:
        ```py
        yaml_content = create_sample_yaml_input_file(
            file_path=pathlib.Path("John_Doe_CV.yaml"), name="John Doe", theme="classic"
        )
        # File written with schema hint, cv content, and commented design
        ```

    Args:
        file_path: Optional path to write file.
        name: Person's full name.
        theme: Design theme identifier.
        locale: Language/date format identifier.

    Returns:
        YAML string if file_path is None, otherwise None after writing file.
    """
    if theme not in available_themes:
        message = (
            f"The theme {theme} is not available. The available themes are:"
            f" {available_themes}"
        )
        raise RenderCVUserError(message)

    if locale not in available_locales:
        message = (
            f"The locale {locale} is not available. The available locales are:"
            f" {available_locales}. \n\nBut you can continue with `English`, and then"
            " write your own `locale` field in the input file."
        )
        raise RenderCVUserError(message)

    data_model = create_sample_rendercv_pydantic_model(
        name=name, theme=theme, locale=locale
    )

    data_model_as_dictionary = rendercv_model_to_dictionary(data_model)

    yaml_string = dictionary_to_yaml(data_model_as_dictionary)

    # Process for nested bullets:
    yaml_string = re.sub(r"(?<! ) - (?! )", "\n            - ", yaml_string)

    # Add a comment to the first line, for JSON Schema:
    comment_to_add = (
        "# yaml-language-server:"
        f" $schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v{__version__}/schema.json\n"
    )
    yaml_string = comment_to_add + yaml_string

    yaml_design_theme_part = f"design:\n  theme: {theme}\n"
    split_yaml_string = yaml_string.split(yaml_design_theme_part)
    yaml_cv_field = split_yaml_string[0]

    yaml_locale_part = f"locale:\n  language: {locale}\n"
    split_yaml_string = split_yaml_string[1].split(yaml_locale_part)
    below_design = split_yaml_string[0].replace(yaml_design_theme_part, "")
    below_design = [
        f"  {line.replace('  ', '# ', 1)}"
        for line in below_design.splitlines(keepends=False)
    ]
    yaml_design_field = yaml_design_theme_part + "\n".join(below_design) + "\n"

    # Handle locale field commenting (similar to design)
    locale_and_settings = split_yaml_string[1]
    settings_part = "settings:\n"
    split_by_settings = locale_and_settings.split(settings_part)
    below_locale = split_by_settings[0]
    below_locale_commented = [
        f"  {line.replace('  ', '# ', 1)}"
        for line in below_locale.splitlines(keepends=False)
    ]
    yaml_locale_field = yaml_locale_part + "\n".join(below_locale_commented) + "\n"
    yaml_settings_field = settings_part + split_by_settings[1]

    yaml_string = (
        yaml_cv_field + yaml_design_field + yaml_locale_field + yaml_settings_field
    )

    if file_path is not None:
        file_path.write_text(yaml_string, encoding="utf-8")

    return yaml_string


def rendercv_model_to_dictionary(data_model: RenderCVModel) -> dict:
    """Convert a RenderCVModel to a plain dictionary via JSON serialization.

    Why:
        The YAML library sometimes has problems with the dictionary returned by
        Pydantic's model_dump(). Converting through JSON first produces clean
        Python dicts that serialize reliably.

    Args:
        data_model: Validated RenderCV model.

    Returns:
        Plain dictionary representation of the model.
    """
    data_model_as_json = data_model.model_dump_json(
        exclude_none=False,
        by_alias=True,
    )
    return json.loads(data_model_as_json)


@overload
def create_sample_yaml_file(
    *,
    dictionary: dict,
    file_path: None,
) -> str: ...
@overload
def create_sample_yaml_file(
    *,
    dictionary: dict,
    file_path: pathlib.Path,
) -> None: ...
def create_sample_yaml_file(
    *,
    dictionary: dict,
    file_path: pathlib.Path | None = None,
) -> str | None:
    """Convert a dictionary to formatted YAML and optionally write to file.

    Why:
        Multiple sample file generators share the same conversion and
        file-writing logic. Centralizing it avoids duplication across
        create_sample_cv_file, create_sample_design_file, etc.

    Args:
        dictionary: Data structure to convert to YAML.
        file_path: Optional path to write file.

    Returns:
        YAML string if file_path is None, otherwise None after writing file.
    """
    yaml_string = dictionary_to_yaml(dictionary)

    # Process for nested bullets:
    yaml_string = re.sub(r"(?<! ) - (?! )", "\n            - ", yaml_string)

    if file_path is not None:
        file_path.write_text(yaml_string, encoding="utf-8")

    return yaml_string


@overload
def create_sample_cv_file(
    *,
    file_path: None,
    name: str = "John Doe",
) -> str: ...
@overload
def create_sample_cv_file(
    *,
    file_path: pathlib.Path,
    name: str = "John Doe",
) -> None: ...
def create_sample_cv_file(
    *,
    file_path: pathlib.Path | None = None,
    name: str = "John Doe",
) -> str | None:
    """Generate a sample YAML file containing only the CV section.

    Why:
        Standalone CV files let users focus on content separately from
        design, locale, and settings configuration.

    Args:
        file_path: Optional path to write file.
        name: Person's full name.

    Returns:
        YAML string if file_path is None, otherwise None after writing file.
    """
    data_model = create_sample_rendercv_pydantic_model(name=name)
    dictionary = rendercv_model_to_dictionary(data_model)
    return create_sample_yaml_file(
        dictionary={"cv": dictionary["cv"]}, file_path=file_path
    )


@overload
def create_sample_design_file(
    *,
    file_path: None,
    theme: str = "classic",
) -> str: ...
@overload
def create_sample_design_file(
    *,
    file_path: pathlib.Path,
    theme: str = "classic",
) -> None: ...
def create_sample_design_file(
    *,
    file_path: pathlib.Path | None = None,
    theme: str = "classic",
) -> str | None:
    """Generate a sample YAML file containing only the design section.

    Why:
        Standalone design files let users explore all theme options
        without mixing in CV content or locale settings.

    Args:
        file_path: Optional path to write file.
        theme: Design theme identifier.

    Returns:
        YAML string if file_path is None, otherwise None after writing file.
    """
    if theme not in available_themes:
        message = (
            f"The theme {theme} is not available. The available themes are:"
            f" {available_themes}"
        )
        raise RenderCVUserError(message)

    data_model = create_sample_rendercv_pydantic_model(theme=theme)
    dictionary = rendercv_model_to_dictionary(data_model)
    return create_sample_yaml_file(
        dictionary={"design": dictionary["design"]}, file_path=file_path
    )


@overload
def create_sample_locale_file(
    *,
    file_path: None,
    locale: str = "english",
) -> str: ...
@overload
def create_sample_locale_file(
    *,
    file_path: pathlib.Path,
    locale: str = "english",
) -> None: ...
def create_sample_locale_file(
    *,
    file_path: pathlib.Path | None = None,
    locale: str = "english",
) -> str | None:
    """Generate a sample YAML file containing only the locale section.

    Why:
        Standalone locale files let users customize language and date
        formatting independently from CV content and design.

    Args:
        file_path: Optional path to write file.
        locale: Language/date format identifier.

    Returns:
        YAML string if file_path is None, otherwise None after writing file.
    """
    if locale not in available_locales:
        message = (
            f"The locale {locale} is not available. The available locales are:"
            f" {available_locales}. \n\nBut you can continue with `English`, and then"
            " write your own `locale` field in the input file."
        )
        raise RenderCVUserError(message)

    data_model = create_sample_rendercv_pydantic_model(locale=locale)
    dictionary = rendercv_model_to_dictionary(data_model)
    return create_sample_yaml_file(
        dictionary={"locale": dictionary["locale"]}, file_path=file_path
    )


@overload
def create_sample_settings_file(
    *,
    file_path: None,
) -> str: ...
@overload
def create_sample_settings_file(
    *,
    file_path: pathlib.Path,
) -> None: ...
def create_sample_settings_file(
    *,
    file_path: pathlib.Path | None = None,
) -> str | None:
    """Generate a sample YAML file containing only the settings section.

    Why:
        Standalone settings files let users configure render options
        independently from CV content, design, and locale.

    Args:
        file_path: Optional path to write file.

    Returns:
        YAML string if file_path is None, otherwise None after writing file.
    """
    data_model = create_sample_rendercv_pydantic_model()
    dictionary = rendercv_model_to_dictionary(data_model)
    return create_sample_yaml_file(
        dictionary={"settings": dictionary["settings"]}, file_path=file_path
    )
