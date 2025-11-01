import pydantic


class BaseModelWithoutExtraKeys(pydantic.BaseModel):
    """Strict validation - rejects unknown fields. Use for fixed schemas."""

    model_config = pydantic.ConfigDict(extra="forbid", validate_default=True)


class BaseModelWithExtraKeys(pydantic.BaseModel):
    """Permissive validation - preserves unknown fields. Use for extensible user content."""

    model_config = pydantic.ConfigDict(extra="allow", validate_default=True)
