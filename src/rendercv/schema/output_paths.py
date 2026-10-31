"""Resolve and validate the complete set of outputs before writing any files."""

from __future__ import annotations

import pathlib
import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

from rendercv.document import build_document_placeholders
from rendercv.text import substitute_placeholders

from .models.settings.render_command import output_formats

if TYPE_CHECKING:
    from .models.rendercv_model import RenderCVModel

invalid_file_name_characters = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def resolve_output_folder_placeholder(
    file_path: pathlib.Path, output_folder: pathlib.Path
) -> pathlib.Path:
    """Replace the reserved OUTPUT_FOLDER path component with the selected folder."""
    parts = file_path.parts
    if "OUTPUT_FOLDER" not in parts:
        return file_path
    if parts.count("OUTPUT_FOLDER") != 1:
        raise ValueError("An output path can contain OUTPUT_FOLDER only once.")
    return output_folder.joinpath(*parts[parts.index("OUTPUT_FOLDER") + 1 :])


def resolve_output_path(model: RenderCVModel, path: pathlib.Path) -> pathlib.Path:
    """Expand a path without creating directories or modifying the model."""
    path = resolve_output_folder_placeholder(
        path, model.settings.render_command.output_folder
    )
    values = {
        name: invalid_file_name_characters.sub("_", value)
        for name, value in build_document_placeholders(model).items()
    }
    return (path.parent / substitute_placeholders(path.name, values)).resolve()


@dataclass(frozen=True)
class OutputPlan:
    """The output paths, and the name of the photo copied next to the Typst file."""

    paths: Mapping[str, pathlib.Path]
    photo: pathlib.Path | None


def build_output_plan(model: RenderCVModel) -> OutputPlan:
    """Reject collisions with inputs, other outputs, and exported photo assets.

    PNG and SVG paths reserve their complete numbered-page family. Disabled
    outputs reserve no files. All checks happen before any output is written.
    """
    command = model.settings.render_command
    paths = {
        kind: resolve_output_path(model, getattr(command, f"{kind}_path"))
        for kind in output_formats
    }
    enabled = {kind: paths[kind] for kind in command.enabled_outputs}
    inputs = [
        model._input_file_path,
        command.design,
        command.locale,
        *command.overlays,
        *model._input_paths,
    ]
    photo = model.cv.photo
    photo_name = None
    if isinstance(photo, pathlib.Path):
        inputs.append(photo)
        # The Typst file refers to its photo by this name:
        photo_name = pathlib.Path(f"{paths['typst'].stem}_photo{photo.suffix.lower()}")
        if "typst" in enabled:
            enabled["photo"] = paths["typst"].parent / photo_name

    def owns(kind: str, base: pathlib.Path, path: pathlib.Path) -> bool:
        if base == path:
            return True
        if (
            kind not in {"png", "svg"}
            or base.parent != path.parent
            or base.suffix != path.suffix
        ):
            return False
        return re.fullmatch(re.escape(base.stem) + r"_[0-9]+", path.stem) is not None

    for kind, path in enabled.items():
        for source in inputs:
            if source is not None and owns(kind, path, source.resolve()):
                if kind == "photo" and source == photo:
                    continue  # The photo is already where it would be copied to.
                msg = f"The {kind} output would overwrite an input file: {source}."
                raise ValueError(msg)
        for other, destination in enabled.items():
            if kind != other and (
                owns(kind, path, destination) or path in destination.parents
            ):
                msg = f"The {kind} and {other} outputs overlap: {destination}."
                raise ValueError(msg)
        for parent in (path, *path.parents):
            if parent.exists() and (
                (parent == path and parent.is_dir())
                or (parent != path and not parent.is_dir())
            ):
                msg = (
                    f"The {kind} output path conflicts with an existing file "
                    f"or directory: {parent}."
                )
                raise ValueError(msg)
    return OutputPlan(MappingProxyType(paths), photo_name)
