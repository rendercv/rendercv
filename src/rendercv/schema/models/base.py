"""Base models with different validation strategies."""

import pydantic


class BaseModelWithoutExtraKeys(pydantic.BaseModel):
    """Rejects unknown fields. Use for fixed schemas like settings and config."""

    model_config = pydantic.ConfigDict(extra="forbid", validate_default=True)


class BaseModelWithExtraKeys(pydantic.BaseModel):
    """Preserves unknown fields. Use for user content like CV entries."""

    model_config = pydantic.ConfigDict(extra="allow", validate_default=True)
