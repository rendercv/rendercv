"""Values prepared for templates, separate from validated user input.

Jinja supports both attribute and item access. Entry fields remain an open mapping
because custom entries can have arbitrary fields; the document structure is typed.
No rendered text is ever assigned to a schema model.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.design.classic_theme import ClassicTheme
from rendercv.schema.models.locale.english_locale import EnglishLocale
from rendercv.schema.models.settings.settings import Settings


@dataclass(frozen=True)
class RenderedEntry:
    """A read-only set of rendered fields, including custom fields and columns."""

    fields: Mapping[str, object]
    _main_column_heading_lines: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(self, "fields", MappingProxyType(dict(self.fields)))

    def __getitem__(self, name: str) -> object:
        return self.fields[name]

    def __getattr__(self, name: str) -> object:
        try:
            return self.fields[name]
        except KeyError as error:
            raise AttributeError(name) from error


@dataclass(frozen=True)
class RenderedSection:
    """A heading and either rendered entries or further sections."""

    title: str
    key: str
    entry_type: str
    entries: tuple[RenderedEntry | str | RenderedSection, ...]

    @property
    def snake_case_title(self) -> str:
        return (self.key or self.title).lower().replace(" ", "_")


@dataclass(frozen=True)
class RenderedCv:
    """Rendered content alongside unchanged contact data for custom templates."""

    source: Cv
    name: str | None
    headline: str | None
    photo: Path | None
    rendercv_sections: tuple[RenderedSection, ...]
    _plain_name: str | None
    _connections: tuple[str, ...]
    _top_note: str
    _footer: str

    def __getattr__(self, name: str) -> object:
        return getattr(self.source, name)


@dataclass(frozen=True)
class RenderContext:
    """The complete input to the layout templates of one output format."""

    cv: RenderedCv
    design: ClassicTheme
    locale: EnglishLocale
    settings: Settings
    _input_file_path: Path | None
