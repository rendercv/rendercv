import pathlib

from rendercv.schema.models.rendercv_model import RenderCVModel

from .templater.string_processor import substitute_placeholders


def resolve_rendercv_file_path(
    rendercv_model: RenderCVModel, file_path: pathlib.Path
) -> pathlib.Path:
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
    }
    file_name = substitute_placeholders(file_path.name, file_path_placeholders)
    resolved_file_path = file_path.parent / file_name
    resolved_file_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_file_path
