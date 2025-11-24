import typer

from rendercv.exception import RenderCVUserError


def parse_override_arguments(extra_arguments: typer.Context) -> dict[str, str]:
    """Parse extra arguments given to the `render` command as data model key and value
    pairs and return them as a dictionary.

    Args:
        extra_arguments: The extra arguments context.

    Returns:
        The key and value pairs.
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

        key_and_values[key] = value

    return key_and_values
