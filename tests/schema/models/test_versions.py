"""Tests for the Version model."""

import pydantic
import pytest

from rendercv.schema.models.versions import Version


class TestVersionModel:
    """Tests for the Version model validation."""

    def test_version_with_include_only(self):
        """Test that a version with only include tags is valid."""
        version = Version(name="academic", include=["research", "publications"])
        assert version.name == "academic"
        assert version.include == ["research", "publications"]
        assert version.exclude is None

    def test_version_with_exclude_only(self):
        """Test that a version with only exclude tags is valid."""
        version = Version(name="industry", exclude=["academic"])
        assert version.name == "industry"
        assert version.include is None
        assert version.exclude == ["academic"]

    def test_version_with_both_include_and_exclude(self):
        """Test that a version with both include and exclude is valid."""
        version = Version(
            name="mixed",
            include=["relevant"],
            exclude=["outdated"],
        )
        assert version.name == "mixed"
        assert version.include == ["relevant"]
        assert version.exclude == ["outdated"]

    def test_version_without_include_or_exclude_raises_error(self):
        """Test that a version without include or exclude raises an error."""
        with pytest.raises(pydantic.ValidationError) as exc_info:
            Version(name="invalid")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "include" in str(errors[0]["msg"]) or "exclude" in str(errors[0]["msg"])

    def test_version_with_empty_include_and_exclude_raises_error(self):
        """Test that a version with empty include and None exclude raises error."""
        with pytest.raises(pydantic.ValidationError):
            Version(name="invalid", include=None, exclude=None)

    def test_version_name_is_required(self):
        """Test that the name field is required."""
        with pytest.raises(pydantic.ValidationError) as exc_info:
            Version(include=["tag"])  # type: ignore

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)
