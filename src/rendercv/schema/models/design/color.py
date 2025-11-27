from pydantic_extra_types.color import Color as PydanticColor


class Color(PydanticColor):
    

    def __str__(self) -> str:
        return self.as_rgb()
