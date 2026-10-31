import pathlib

import typer

from rendercv.exception import RenderCVUserError
from rendercv.schema.models.cv.cv import photo_kind
from rendercv.schema.models.settings.render_command import output_formats


def parse_override_arguments(extra_arguments: typer.Context) -> dict[str, str]:
    """Parse CLI override arguments into dotted-path dictionary.

    Why:
        Users need quick field overrides without editing YAML. We need to parse
        `--cv.phone "123"` style arguments.

    Example:
        ```py
        # From: rendercv render cv.yaml --cv.name "Jane" --cv.phone "456"
        args = parse_override_arguments(ctx)
        # Returns: {"cv.name": "Jane", "cv.phone": "456"}
        ```

    Args:
        extra_arguments: Typer context containing unparsed arguments.

    Returns:
        Map of dotted paths to override values.
    """
    key_and_values: dict[str, str] = {}

    # `extra_arguments.args` is a list of arbitrary arguments that haven't been
    # specified in `cli_render_command` function's definition. They are used to allow
    # users to edit their data model in CLI. The elements with even indexes in this list
    # are keys that start with double dashed, such as
    # `--cv.sections.education.0.institution`. The following elements are the
    # corresponding values of the key, such as `"Bogazici University"`. The for loop
    # below parses `ctx.args` accordingly.

    if len(extra_arguments.args) % 2 != 0:
        message = (
            "There is a problem with the extra arguments"
            f" ({','.join(extra_arguments.args)})! Each key should have a corresponding"
            " value."
        )
        raise RenderCVUserError(message)

    for i in range(0, len(extra_arguments.args), 2):
        key = extra_arguments.args[i]
        value = extra_arguments.args[i + 1]
        if not key.startswith("--"):
            message = f"The key ({key}) should start with double dashes!"
            raise RenderCVUserError(message)

        key = key.replace("--", "")

        if key in {
            f"settings.render_command.{role}"
            for role in ("design", "locale", "overlays")
        }:
            raise RenderCVUserError(
                "Use --design, --locale-catalog, or --overlay to select input files."
            )
        path_fields = {
            f"settings.render_command.{kind}_path" for kind in output_formats
        }
        path_fields.add("settings.render_command.output_folder")
        if key in path_fields or (key == "cv.photo" and photo_kind(value) == "path"):
            value = str(pathlib.Path(value).absolute())

        key_and_values[key] = value

    return key_and_values
