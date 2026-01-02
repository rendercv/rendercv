import pathlib

from rendercv.schema.models.rendercv_model import RenderCVModel

from .templater.string_processor import substitute_placeholders


def resolve_rendercv_file_path(
    rendercv_model: RenderCVModel, file_path: pathlib.Path
) -> pathlib.Path:
    """Resolve output file path with placeholder substitution and directory creation.

    Why:
        Users specify output paths like `NAME_CV_YEAR.pdf` with placeholders
        for dynamic naming. Substitution uses current date and CV name to
        generate actual file names, creating parent directories if needed.

    Example:
        ```py
        # Given model with name="John Doe" and year=2025
        path = resolve_rendercv_file_path(
            model, pathlib.Path("output/NAME_IN_LOWER_SNAKE_CASE_CV_YEAR.pdf")
        )
        # Returns: pathlib.Path("output/john_doe_CV_2025.pdf")
        ```

    Args:
        rendercv_model: CV model containing name and date for substitution.
        file_path: Template path with placeholders.

    Returns:
        Resolved absolute path with substituted filename.
    """
    current_date = rendercv_model.settings.current_date
    current_date_month_index = current_date.month - 1
    file_path_placeholders = {
        "MONTH_NAME": rendercv_model.locale.month_names[current_date_month_index],
        "MONTH_ABBREVIATION": rendercv_model.locale.month_abbreviations[
            current_date_month_index
        ],
        "MONTH": str(current_date.month),
        "MONTH_IN_TWO_DIGITS": f"{current_date.month:02d}",
        "YEAR": str(current_date.year),
        "YEAR_IN_TWO_DIGITS": str(current_date.year)[-2:],
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
        "FILENAME": (
            rendercv_model._input_file_path.stem.replace(" ", "-")
            if rendercv_model._input_file_path
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
