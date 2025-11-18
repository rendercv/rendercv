from collections.abc import Callable
from typing import Literal

from rendercv.schema.models.cv.section import Entry
from rendercv.schema.models.rendercv_model import RenderCVModel

from .connections import compute_connections
from .date import compute_date_string
from .text_processor import make_keywords_bold


def process_fields(entry: Entry, processors: list[Callable[[str], str]]) -> Entry:
    skipped_fields = ["start_date", "end_date", "date"]
    for processor in processors:
        if isinstance(entry, str):
            entry = processor(entry)
        else:
            for field_name, field_value in vars(entry).items():
                if field_name in skipped_fields or field_name.startswith("_"):
                    continue

                if isinstance(field_value, str):
                    new_field_value = processor(field_value)
                elif isinstance(field_value, list):
                    new_field_value = [processor(item) for item in field_value]
                else:
                    message = f"Unhandled field type: {type(field_value)}"
                    raise ValueError(message)

                field_value = new_field_value  # NOQA: PLW2901

    return entry


def preprocess_model(
    rendercv_model: RenderCVModel, file_type: Literal["typst", "markdown"]
) -> RenderCVModel:
    rendercv_model.connections = compute_connections(rendercv_model, file_type)  # pyright: ignore[reportAttributeAccessIssue]

    if rendercv_model.cv.sections is None:
        return rendercv_model

    for section in rendercv_model.cv.rendercv_sections:
        for entry in section.entries:
            entry = process_fields(
                entry,
                [
                    lambda x: make_keywords_bold(
                        x, rendercv_model.rendercv_settings.bold_keywords
                    )
                ],
            )
            date_string = compute_date_string(entry)
            if date_string:
                entry.date_string = date_string  # pyright: ignore[reportAttributeAccessIssue]

    return rendercv_model
    # 1. Add date_string attribute to all entries
    # 2. Make keywords bold
    # (3.) Handle nested bullets in highlights
    # 4. Add connection computaiton to here!
    # Add templates as attributes to the entries!
