from pydantic_extra_types.color import Color as PydanticColor


class Color(PydanticColor):
    def __str__(self) -> str:
        """Convert color to RGB string for Typst rendering.

        Why:
            Typst templates need colors as rgb(r,g,b) strings. Override ensures
            Color objects serialize correctly in Jinja2 templates.

        Returns:
            RGB string like "rgb(255, 0, 0)".
        """
        return self.as_rgb()
