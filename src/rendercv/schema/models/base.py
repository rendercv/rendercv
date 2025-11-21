import pydantic


class BaseModelWithoutExtraKeys(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid", validate_default=True)


class BaseModelWithExtraKeys(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow", validate_default=True)
