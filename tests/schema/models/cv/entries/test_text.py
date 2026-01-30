"""Tests for the TextEntry model."""

import pydantic
import pytest

from rendercv.schema.models.cv.entries.text import TextEntry


class TestTextEntry:
    """Tests for the TextEntry model."""

    def test_text_entry_with_content_only(self):
        """Test creating a TextEntry with only content."""
        entry = TextEntry(content="This is a text entry.")
        assert entry.content == "This is a text entry."
        assert entry.tags is None

    def test_text_entry_with_content_and_tags(self):
        """Test creating a TextEntry with content and tags."""
        entry = TextEntry(
            content="This is a tagged text entry.",
            tags=["research", "academic"],
        )
        assert entry.content == "This is a tagged text entry."
        assert entry.tags == ["research", "academic"]

    def test_text_entry_content_is_required(self):
        """Test that content is required."""
        with pytest.raises(pydantic.ValidationError) as exc_info:
            TextEntry(tags=["tag"])  # type: ignore

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("content",) for error in errors)

    def test_text_entry_empty_tags_list(self):
        """Test creating a TextEntry with an empty tags list."""
        entry = TextEntry(content="Content", tags=[])
        assert entry.content == "Content"
        assert entry.tags == []

    def test_text_entry_inherits_from_base_entry(self):
        """Test that TextEntry has the entry_type_in_snake_case property."""
        entry = TextEntry(content="Test")
        assert entry.entry_type_in_snake_case == "text_entry"
