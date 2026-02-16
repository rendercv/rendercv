"""The `rendercv.schema.models.cv.entries.text` module contains the `TextEntry` model.

TextEntry allows plain text entries to have optional tags for filtering.
For backward compatibility, sections can accept either plain strings or TextEntry objects.
"""

import pydantic

from .bases.entry import BaseEntry


class TextEntry(BaseEntry):
    """A text entry with optional tags for filtering.

    This model allows text entries to participate in tag-based filtering
    while maintaining backward compatibility with plain string entries.

    Example:
        ```yaml
        # Plain string (backward compatible)
        - "This is a simple text entry"

        # TextEntry with tags
        - content: "This entry has tags for filtering"
          tags: [academic, research]
        ```
    """

    content: str = pydantic.Field(
        title="Content",
        description="The text content of the entry.",
        examples=["This is a text entry with optional tags."],
    )
