"""SkillIconsEntry model for displaying skill icons from skillicons.dev."""

import functools
import pathlib
from typing import Literal

import pydantic

from .bases.entry import BaseEntry

type SkillIconsTheme = Literal["dark", "light"]
type SkillIconsAlign = Literal["left", "center", "right"]


class SkillIcons(pydantic.BaseModel):
    """Configuration for skill icons from https://skillicons.dev/.

    This model can be used standalone as an entry type (SkillIconsEntry)
    or embedded in other entries like NormalEntry.

    Example YAML:
        ```yaml
        skillicons:
          icons: python,js,ts
          theme: dark
          size: 24
        ```
    """

    # Internal field to store the local path of downloaded icon image
    _local_path: pathlib.Path | None = pydantic.PrivateAttr(default=None)

    icons: str | list[str] = pydantic.Field(
        description=(
            "The icon name(s) to display. Can be a single icon name, a comma-separated"
            " string of icon names, or a list of icon names. See"
            " https://github.com/tandpfun/skill-icons for available icons."
        ),
        examples=[
            "python",
            "python,js,ts,react",
            ["python", "js", "ts", "react"],
        ],
    )
    theme: SkillIconsTheme | None = pydantic.Field(
        default=None,
        description=(
            "The theme for the icons. 'dark' has a dark background, 'light' has a"
            " light background. If not specified, defaults to 'dark'."
        ),
        examples=["dark", "light"],
    )
    perline: int | None = pydantic.Field(
        default=None,
        ge=1,
        le=50,
        description=(
            "Number of icons per line. Must be between 1 and 50."
            " If not specified, defaults to 15."
        ),
        examples=[3, 6, 10, 15],
    )
    align: SkillIconsAlign = pydantic.Field(
        default="left",
        description=(
            "Horizontal alignment of the icons. Can be 'left', 'center', or 'right'."
            " Defaults to 'left'."
        ),
        examples=["left", "center", "right"],
    )
    size: int | None = pydantic.Field(
        default=None,
        ge=8,
        le=128,
        description=(
            "Size of each icon in pt (points). This determines the display size of"
            " each icon in the final PDF. Recommended values: 24-48pt for inline,"
            " 32-64pt for dedicated sections. If not specified, defaults to 32pt."
        ),
        examples=[24, 32, 48, 64],
    )

    @functools.cached_property
    def icons_list(self) -> list[str]:
        """Return icons as a list, regardless of input format."""
        if isinstance(self.icons, list):
            return self.icons
        return [icon.strip() for icon in self.icons.split(",")]

    @functools.cached_property
    def icons_string(self) -> str:
        """Return icons as a comma-separated string."""
        if isinstance(self.icons, list):
            return ",".join(self.icons)
        return self.icons

    @functools.cached_property
    def url(self) -> str:
        """Generate the full skillicons.dev URL for the icons."""
        base_url = "https://skillicons.dev/icons"
        params = [f"i={self.icons_string}"]

        if self.theme is not None:
            params.append(f"theme={self.theme}")

        if self.perline is not None:
            params.append(f"perline={self.perline}")

        return f"{base_url}?{'&'.join(params)}"

    @property
    def local_path(self) -> pathlib.Path | None:
        """Return the local path if the icon image has been downloaded."""
        return self._local_path

    @local_path.setter
    def local_path(self, value: pathlib.Path | None) -> None:
        """Set the local path after downloading the icon image."""
        self._local_path = value

    @functools.cached_property
    def image_filename(self) -> str:
        """Generate a unique filename for the icon image based on parameters."""
        safe_icons = self.icons_string.replace(",", "_")
        theme = self.theme or "dark"
        perline = self.perline or 15
        return f"skillicons_{safe_icons}_{theme}_{perline}.svg"

    @functools.cached_property
    def image_width(self) -> str:
        """Calculate the scaled width of the image for Typst.

        The SVG from skillicons.dev uses these proportions:
        - Icon size: 256px (unit square)
        - Gap between icons: 44px

        We calculate the total width based on the desired icon size in pt,
        maintaining the same proportions.
        """
        # Default size is 32pt if not specified
        size = int(self.size) if self.size is not None else 32

        # Calculate how many icons per row
        total_icons = len(self.icons_list)
        perline = int(self.perline) if self.perline is not None else 15
        icons_per_row = min(total_icons, perline)

        # Calculate gap proportionally (44/256 ratio from original SVG)
        gap_ratio = 44 / 256
        gap = size * gap_ratio

        # Total width = icons + gaps
        new_width = icons_per_row * size + (icons_per_row - 1) * gap

        return f"{new_width:.1f}pt"


class SkillIconsEntry(SkillIcons, BaseEntry):
    """Entry type for displaying skill icons from https://skillicons.dev/.

    This entry allows users to display technology/skill icons in their CV
    by specifying the icon names, theme, and icons per line.

    Example YAML:
        ```yaml
        skills:
          - icons: python,js,ts,react,vue,nodejs
            theme: dark
            perline: 6
        ```

    The above will generate an image URL like:
        https://skillicons.dev/icons?i=python,js,ts,react,vue,nodejs&theme=dark&perline=6
    """
