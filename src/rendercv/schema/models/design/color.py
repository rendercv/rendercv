from pydantic_extra_types.color import Color as PydanticColor


class Color(PydanticColor):
    """Accepts hex/rgb/hsl/named colors, outputs as rgb(r,g,b) string."""

    def __str__(self) -> str:
        return self.as_rgb()
