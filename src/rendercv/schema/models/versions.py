"""The `rendercv.schema.models.versions` module contains the `Version` model.

The Version model defines filtering rules for generating different versions of a CV
based on entry tags.
"""

import pydantic

from .base import BaseModelWithoutExtraKeys


class Version(BaseModelWithoutExtraKeys):
    """A version definition for generating filtered CVs.

    Each version specifies which entries to include or exclude based on their tags.
    Entries without tags are always included (permissive filtering).

    Example:
        ```yaml
        versions:
          - name: academic
            include: [research, publications, teaching]
          - name: industry
            exclude: [academic-only]
        ```
    """

    name: str = pydantic.Field(
        title="Version Name",
        description="The unique name of this version. Used with --version CLI flag.",
        examples=["academic", "industry", "devops"],
    )

    include: list[str] | None = pydantic.Field(
        default=None,
        title="Include Tags",
        description=(
            "List of tags to include. Only entries with at least one of these tags "
            "will be included. Entries without any tags are always included."
        ),
        examples=[["research", "publications"], ["machine-learning", "deep-learning"]],
    )

    exclude: list[str] | None = pydantic.Field(
        default=None,
        title="Exclude Tags",
        description=(
            "List of tags to exclude. Entries with any of these tags will be excluded. "
            "Applied after include filter if both are specified."
        ),
        examples=[["internal", "draft"], ["outdated"]],
    )

    @pydantic.model_validator(mode="after")
    def validate_include_or_exclude_provided(self) -> "Version":
        """Ensure at least one of include or exclude is provided.

        Why:
            A version without any filtering rules is pointless. This validation
            ensures users don't accidentally create empty versions.

        Returns:
            Validated Version instance.

        Raises:
            ValueError: If neither include nor exclude is provided.
        """
        if self.include is None and self.exclude is None:
            raise ValueError(
                "At least one of 'include' or 'exclude' must be provided for a version."
            )
        return self
