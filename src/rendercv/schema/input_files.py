"""Plan and load CV files for rendering, watch mode, and Python callers."""

import contextlib
import dataclasses
import pathlib
from collections.abc import Sequence
from typing import Unpack

from rendercv.exception import (
    RenderCVUserError,
    RenderCVUserValidationError,
    YamlSource,
)

from .models.rendercv_model import RenderCVModel
from .rendercv_model_builder import (
    BuildRendercvModelArguments,
    build_rendercv_dictionary_and_model,
    read_yaml_with_validation_errors,
)


@dataclasses.dataclass(frozen=True)
class InputFiles:
    """The files that a render reads.

    Args:
        input: The main YAML input file.
        design: The file of the `design` field.
        locale: The file of the `locale` field.
        settings: The file of the `settings` field.
        overlays: The files merged over the input, in order.
    """

    input: pathlib.Path
    design: pathlib.Path | None = None
    locale: pathlib.Path | None = None
    settings: pathlib.Path | None = None
    overlays: tuple[pathlib.Path, ...] = ()

    @property
    def paths(self) -> list[pathlib.Path]:
        """All the files, for watch mode to monitor."""
        files = (self.input, self.design, self.locale, self.settings, *self.overlays)
        return [path for path in files if path is not None]


def collect_input_file_paths(
    input_file_path: pathlib.Path,
    design: pathlib.Path | None = None,
    locale: pathlib.Path | None = None,
    settings: pathlib.Path | None = None,
    overlays: Sequence[pathlib.Path] = (),
) -> InputFiles:
    """Collect all input file paths involved in a render.

    Why:
        A render may involve multiple files: the main YAML, plus the files of
        the design/locale/settings fields and overlays, provided via CLI flags or
        referenced in settings.render_command. Watch mode needs this complete list
        to monitor all of them for changes, and the render pipeline needs the
        resolved paths to read their contents.

    Args:
        input_file_path: Path to the main YAML input file.
        design: CLI-provided design file path.
        locale: CLI-provided locale file path.
        settings: CLI-provided settings file path.
        overlays: CLI-provided overlay file paths, merged after the referenced ones.

    Returns:
        The input files.
    """
    files: dict[str, pathlib.Path | tuple[pathlib.Path, ...]] = {}
    if design:
        files["design"] = design
    if locale:
        files["locale"] = locale

    # Inspect the settings overlay before the main input: references are selected
    # per field, with CLI > settings overlay > main YAML precedence. Discovery is
    # tolerant so watch mode can monitor and recover from invalid/missing inputs;
    # the render itself reports all read/validation errors.
    selected = set(files)
    sources: list[tuple[pathlib.Path | None, YamlSource]] = [
        (settings, "settings_yaml_file"),
        (input_file_path, "main_yaml_file"),
    ]
    for source, yaml_source in sources:
        if source is None:
            continue
        with contextlib.suppress(
            OSError, RenderCVUserValidationError, RenderCVUserError
        ):
            document = read_yaml_with_validation_errors(
                source.read_text(encoding="utf-8"), yaml_source
            )
            settings_dict = document.get("settings")
            if not isinstance(settings_dict, dict):
                continue
            command = settings_dict.get("render_command")
            if not isinstance(command, dict):
                continue
            for role in ("design", "locale", "overlays"):
                if role in selected or role not in command:
                    continue
                selected.add(role)
                reference = command[role]
                if role == "overlays" and isinstance(reference, list):
                    files[role] = tuple(
                        (input_file_path.parent / item).resolve()
                        for item in reference
                        if isinstance(item, str) and item
                    )
                elif isinstance(reference, str) and reference:
                    files[role] = (input_file_path.parent / reference).resolve()

    referenced_overlays = files.get("overlays", ())
    design_file = files.get("design")
    locale_file = files.get("locale")
    return InputFiles(
        input=input_file_path,
        design=design_file if isinstance(design_file, pathlib.Path) else None,
        locale=locale_file if isinstance(locale_file, pathlib.Path) else None,
        settings=settings,
        overlays=(
            *(referenced_overlays if isinstance(referenced_overlays, tuple) else ()),
            *overlays,
        ),
    )


def load_rendercv_model(
    input_file_path: pathlib.Path,
    *,
    design: pathlib.Path | None = None,
    locale: pathlib.Path | None = None,
    settings: pathlib.Path | None = None,
    overlays: Sequence[pathlib.Path] = (),
    **kwargs: Unpack[BuildRendercvModelArguments],
) -> RenderCVModel:
    """Read one explicit load plan and validate the resulting document once.

    Named component files replace their component; general overlays modify values
    without loading more files. Relative YAML paths use the main input directory.
    The returned model and the watcher's file list use the same discovery rules.
    """
    files = collect_input_file_paths(
        input_file_path, design, locale, settings, overlays
    )
    if files.settings:
        kwargs["settings_yaml_file"] = files.settings.read_text(encoding="utf-8")
    if files.design:
        kwargs["design_yaml_file"] = files.design.read_text(encoding="utf-8")
        kwargs["design_path"] = files.design
    if files.locale:
        kwargs["locale_yaml_file"] = files.locale.read_text(encoding="utf-8")
        kwargs["locale_path"] = files.locale
    kwargs["overlay_yaml_files"] = [
        (str(path), path.read_text(encoding="utf-8")) for path in files.overlays
    ]
    kwargs["input_paths"] = tuple(files.paths)
    _, model = build_rendercv_dictionary_and_model(
        input_file_path.read_text(encoding="utf-8"),
        input_file_path=input_file_path,
        **kwargs,
    )
    return model
