import pathlib
from datetime import date as Date

from .models.rendercv_model import RenderCVModel
from .context import ValidationContext
from .yaml_reader import read_yaml


def read_input_file(file_path_or_contents: pathlib.Path | str) -> RenderCVModel:
    """Read the input file (YAML or JSON) and return them as an instance of
    `RenderCVDataModel`, which is a Pydantic data model of RenderCV's data format.

    Args:
        file_path_or_contents: The path to the input file or the contents of the input
            file as a string.

    Returns:
        The data model.
    """
    input_as_dictionary = read_yaml(file_path_or_contents)

    return validate_input_dictionary_and_return_rendercv_pydantic_model(
        input_as_dictionary
    )


def validate_input_dictionary_and_return_rendercv_pydantic_model(
    input_dictionary: dict,
    input_file_path: pathlib.Path | None = None,
) -> RenderCVModel:
    """Validate the input dictionary by creating an instance of `RenderCVModel`,
    which is a Pydantic data model of RenderCV's data format.

    Args:
        input_dictionary: The input dictionary.
        input_file_path: The path to the input file, to pass to the validation context.

    Returns:
        The data model.
    """
    return RenderCVModel.model_validate(
        input_dictionary,
        context={
            "context": ValidationContext(
                input_file_path=input_file_path or pathlib.Path(),
                date_today=input_dictionary.get("rendercv_settings", {}).get(
                    "date", Date.today()
                ),
            )
        },
    )
