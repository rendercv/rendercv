from typing import Literal

import pydantic


class DummythemeTheme(pydantic.BaseModel):
    theme: Literal["dummytheme"]
