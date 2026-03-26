import pydantic


class BaseModelWithoutExtraKeys(pydantic.BaseModel):
    """Pydantic base model that rejects unrecognized fields.

    Why:
        Most RenderCV models have fixed schemas. Forbidding extra keys
        catches typos and unsupported fields early during YAML validation,
        giving users clear error messages instead of silently ignoring
        misspelled options.
    """

    model_config = pydantic.ConfigDict(extra="forbid", validate_default=True)


class BaseModelWithExtraKeys(pydantic.BaseModel):
    """Pydantic base model that allows unrecognized fields.

    Why:
        Entry models need to accept extra keys so that template-generated
        fields (like rendered date strings) can be attached as dynamic
        attributes during processing without validation errors.
    """

    model_config = pydantic.ConfigDict(extra="allow", validate_default=True)
