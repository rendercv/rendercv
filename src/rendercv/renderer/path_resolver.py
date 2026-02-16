import pathlib

from rendercv.schema.models.rendercv_model import RenderCVModel

from .templater.date import build_date_placeholders
from .templater.string_processor import substitute_placeholders


def resolve_output_folder_placeholder(
    file_path: pathlib.Path, output_folder: pathlib.Path
) -> pathlib.Path:
    """Replace the OUTPUT_FOLDER directory component with the actual output folder.

    Why:
        Output file paths use OUTPUT_FOLDER as a placeholder directory so users
        can redirect all output via the single ``output_folder`` setting. Both
        paths are already absolute (resolved by PlannedPathRelativeToInput from
        the same base), so the replacement swaps the placeholder component and
        appends remaining path segments.

    Args:
        file_path: Absolute path potentially containing an OUTPUT_FOLDER component.
        output_folder: Absolute path to the actual output folder.

    Returns:
        Path with OUTPUT_FOLDER replaced, or original path if not present.
    """
    parts = file_path.parts
    if "OUTPUT_FOLDER" not in parts:
        return file_path

    idx = parts.index("OUTPUT_FOLDER")
    suffix_parts = parts[idx + 1 :]

    if suffix_parts:
        return output_folder / pathlib.Path(*suffix_parts)
    return output_folder


def resolve_rendercv_file_path(
    rendercv_model: RenderCVModel, file_path: pathlib.Path
) -> pathlib.Path:
    """Resolve output file path with placeholder substitution and directory creation.

    Why:
        Users specify output paths like ``OUTPUT_FOLDER/NAME_CV_YEAR.pdf`` with
        placeholders for dynamic naming. This function first resolves the
        OUTPUT_FOLDER directory component to the configured output folder, then
        substitutes name and date placeholders in the filename, and finally
        creates parent directories as needed.

    Example:
        ```py
        # Given model with name="John Doe", year=2025, output_folder=rendercv_output
        path = resolve_rendercv_file_path(
            model,
            pathlib.Path("/cv/OUTPUT_FOLDER/NAME_IN_LOWER_SNAKE_CASE_CV_YEAR.pdf"),
        )
        # Returns: pathlib.Path("/cv/rendercv_output/john_doe_CV_2025.pdf")
        ```

    Args:
        rendercv_model: CV model containing name, date, and output folder for
            substitution.
        file_path: Template path with placeholders.

    Returns:
        Resolved absolute path with substituted placeholders.
    """
    output_folder = rendercv_model.settings.render_command.output_folder
    file_path = resolve_output_folder_placeholder(file_path, output_folder)

    current_date = rendercv_model.settings.current_date
    file_path_placeholders = {
        **build_date_placeholders(current_date, locale=rendercv_model.locale),
        "NAME": rendercv_model.cv.name,
        "NAME_IN_SNAKE_CASE": (
            rendercv_model.cv.name.replace(" ", "_") if rendercv_model.cv.name else None
        ),
        "NAME_IN_LOWER_SNAKE_CASE": (
            rendercv_model.cv.name.replace(" ", "_").lower()
            if rendercv_model.cv.name
            else None
        ),
        "NAME_IN_UPPER_SNAKE_CASE": (
            rendercv_model.cv.name.replace(" ", "_").upper()
            if rendercv_model.cv.name
            else None
        ),
        "NAME_IN_KEBAB_CASE": (
            rendercv_model.cv.name.replace(" ", "-") if rendercv_model.cv.name else None
        ),
        "NAME_IN_LOWER_KEBAB_CASE": (
            rendercv_model.cv.name.replace(" ", "-").lower()
            if rendercv_model.cv.name
            else None
        ),
        "NAME_IN_UPPER_KEBAB_CASE": (
            rendercv_model.cv.name.replace(" ", "-").upper()
            if rendercv_model.cv.name
            else None
        ),
    }
    file_path_placeholders = {
        k: v for k, v in file_path_placeholders.items() if v is not None
    }
    file_name = substitute_placeholders(file_path.name, file_path_placeholders)
    resolved_file_path = file_path.parent / file_name
    resolved_file_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_file_path
