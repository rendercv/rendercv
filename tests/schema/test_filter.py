"""Tests for the filter module."""

import pytest

from rendercv.exception import RenderCVUserError
from rendercv.schema.filter import (filter_entries,
                                    filter_rendercv_model_by_version,
                                    find_version, get_entry_tags,
                                    should_include_entry)
from rendercv.schema.models.cv.cv import Cv
from rendercv.schema.models.cv.entries.bullet import BulletEntry
from rendercv.schema.models.cv.entries.experience import ExperienceEntry
from rendercv.schema.models.cv.entries.text import TextEntry
from rendercv.schema.models.rendercv_model import RenderCVModel
from rendercv.schema.models.versions import Version


class TestGetEntryTags:
    """Tests for the get_entry_tags function."""

    def test_get_tags_from_bullet_entry_with_tags(self):
        """Test extracting tags from a BulletEntry with tags."""
        entry = BulletEntry(bullet="Test bullet", tags=["tag1", "tag2"])
        assert get_entry_tags(entry) == ["tag1", "tag2"]

    def test_get_tags_from_bullet_entry_without_tags(self):
        """Test extracting tags from a BulletEntry without tags."""
        entry = BulletEntry(bullet="Test bullet")
        assert get_entry_tags(entry) is None

    def test_get_tags_from_text_entry_with_tags(self):
        """Test extracting tags from a TextEntry with tags."""
        entry = TextEntry(content="Test content", tags=["research"])
        assert get_entry_tags(entry) == ["research"]

    def test_get_tags_from_plain_string(self):
        """Test that plain strings return None for tags."""
        assert get_entry_tags("Plain text entry") is None


class TestShouldIncludeEntry:
    """Tests for the should_include_entry function."""

    def test_entry_without_tags_always_included(self):
        """Test that entries without tags are always included (permissive)."""
        entry = BulletEntry(bullet="No tags")
        assert should_include_entry(entry, include_tags=["specific"], exclude_tags=None)
        assert should_include_entry(entry, include_tags=None, exclude_tags=["any"])
        assert should_include_entry(
            entry, include_tags=["specific"], exclude_tags=["any"]
        )

    def test_entry_with_matching_include_tag_included(self):
        """Test that entries with matching include tags are included."""
        entry = BulletEntry(bullet="Tagged", tags=["research", "ml"])
        assert should_include_entry(entry, include_tags=["research"], exclude_tags=None)
        assert should_include_entry(entry, include_tags=["ml"], exclude_tags=None)
        assert should_include_entry(
            entry, include_tags=["research", "other"], exclude_tags=None
        )

    def test_entry_without_matching_include_tag_excluded(self):
        """Test that entries without matching include tags are excluded."""
        entry = BulletEntry(bullet="Tagged", tags=["research"])
        assert not should_include_entry(
            entry, include_tags=["different"], exclude_tags=None
        )

    def test_entry_with_matching_exclude_tag_excluded(self):
        """Test that entries with matching exclude tags are excluded."""
        entry = BulletEntry(bullet="Tagged", tags=["internal", "draft"])
        assert not should_include_entry(
            entry, include_tags=None, exclude_tags=["internal"]
        )
        assert not should_include_entry(entry, include_tags=None, exclude_tags=["draft"])

    def test_entry_without_matching_exclude_tag_included(self):
        """Test that entries without matching exclude tags are included."""
        entry = BulletEntry(bullet="Tagged", tags=["public"])
        assert should_include_entry(entry, include_tags=None, exclude_tags=["internal"])

    def test_include_then_exclude_applied_in_order(self):
        """Test that include is applied first, then exclude."""
        entry = BulletEntry(bullet="Tagged", tags=["research", "outdated"])

        # Has research (include), but also outdated (exclude) → excluded
        assert not should_include_entry(
            entry, include_tags=["research"], exclude_tags=["outdated"]
        )

        # Has research (include), no exclude match → included
        assert should_include_entry(
            entry, include_tags=["research"], exclude_tags=["internal"]
        )

    def test_plain_string_always_included(self):
        """Test that plain strings are always included (no tags)."""
        assert should_include_entry("Plain text", include_tags=["any"], exclude_tags=None)
        assert should_include_entry("Plain text", include_tags=None, exclude_tags=["any"])


class TestFilterEntries:
    """Tests for the filter_entries function."""

    def test_filter_entries_with_include(self):
        """Test filtering entries with include tags."""
        entries = [
            BulletEntry(bullet="Entry 1", tags=["ml"]),
            BulletEntry(bullet="Entry 2", tags=["web"]),
            BulletEntry(bullet="Entry 3"),  # No tags
        ]
        filtered = filter_entries(entries, include_tags=["ml"], exclude_tags=None)
        assert len(filtered) == 2  # Entry 1 (matched) + Entry 3 (no tags)
        assert filtered[0].bullet == "Entry 1"
        assert filtered[1].bullet == "Entry 3"

    def test_filter_entries_with_exclude(self):
        """Test filtering entries with exclude tags."""
        entries = [
            BulletEntry(bullet="Entry 1", tags=["public"]),
            BulletEntry(bullet="Entry 2", tags=["internal"]),
            BulletEntry(bullet="Entry 3"),  # No tags
        ]
        filtered = filter_entries(entries, include_tags=None, exclude_tags=["internal"])
        assert len(filtered) == 2  # Entry 1 + Entry 3
        assert filtered[0].bullet == "Entry 1"
        assert filtered[1].bullet == "Entry 3"

    def test_filter_entries_empty_list(self):
        """Test filtering an empty list."""
        filtered = filter_entries([], include_tags=["any"], exclude_tags=None)
        assert filtered == []


class TestFindVersion:
    """Tests for the find_version function."""

    def test_find_existing_version(self):
        """Test finding an existing version."""
        model = RenderCVModel(
            cv=Cv(name="Test"),
            versions=[
                Version(name="academic", include=["research"]),
                Version(name="industry", exclude=["academic"]),
            ],
        )
        version = find_version(model, "academic")
        assert version.name == "academic"
        assert version.include == ["research"]

    def test_find_nonexistent_version_raises_error(self):
        """Test that finding a nonexistent version raises an error."""
        model = RenderCVModel(
            cv=Cv(name="Test"),
            versions=[Version(name="academic", include=["research"])],
        )
        with pytest.raises(RenderCVUserError) as exc_info:
            find_version(model, "nonexistent")

        assert exc_info.value.message is not None
        assert "nonexistent" in exc_info.value.message
        assert "academic" in exc_info.value.message  # Shows available versions

    def test_find_version_when_no_versions_defined(self):
        """Test that finding a version when none are defined raises an error."""
        model = RenderCVModel(cv=Cv(name="Test"))
        with pytest.raises(RenderCVUserError) as exc_info:
            find_version(model, "any")

        assert exc_info.value.message is not None
        assert "No versions are defined" in exc_info.value.message


class TestFilterRendercvModelByVersion:
    """Tests for the filter_rendercv_model_by_version function."""

    def test_filter_model_with_include_version(self):
        """Test filtering a model with an include-based version."""
        model = RenderCVModel(
            cv=Cv(
                name="Test Person",
                sections={
                    "experience": [
                        ExperienceEntry(
                            company="Company A",
                            position="Engineer",
                            tags=["ml"],
                        ),
                        ExperienceEntry(
                            company="Company B",
                            position="Developer",
                            tags=["web"],
                        ),
                    ],
                    "skills": [
                        BulletEntry(bullet="Python", tags=["ml"]),
                        BulletEntry(bullet="JavaScript", tags=["web"]),
                        BulletEntry(bullet="Git"),  # No tags
                    ],
                },
            ),
            versions=[Version(name="ml-focused", include=["ml"])],
        )

        filtered = filter_rendercv_model_by_version(model, "ml-focused")

        assert filtered.cv.sections is not None
        # Experience section should have only Company A
        assert len(filtered.cv.sections["experience"]) == 1
        experience_entry = filtered.cv.sections["experience"][0]
        assert hasattr(experience_entry, "company")
        assert experience_entry.company == "Company A"

        # Skills section should have Python and Git (Git has no tags)
        assert len(filtered.cv.sections["skills"]) == 2
        skills_entries = filtered.cv.sections["skills"]
        bullets = [e.bullet for e in skills_entries if hasattr(e, "bullet")]
        assert "Python" in bullets
        assert "Git" in bullets
        assert "JavaScript" not in bullets

    def test_filter_model_removes_empty_sections(self):
        """Test that sections with no entries after filtering are removed."""
        model = RenderCVModel(
            cv=Cv(
                name="Test Person",
                sections={
                    "experience": [
                        ExperienceEntry(
                            company="Company A",
                            position="Engineer",
                            tags=["ml"],
                        ),
                    ],
                    "hobbies": [
                        BulletEntry(bullet="Reading", tags=["personal"]),
                    ],
                },
            ),
            versions=[Version(name="professional", include=["ml"])],
        )

        filtered = filter_rendercv_model_by_version(model, "professional")

        assert filtered.cv.sections is not None
        # Experience should remain
        assert "experience" in filtered.cv.sections
        # Hobbies should be removed (all entries filtered out)
        assert "hobbies" not in filtered.cv.sections

    def test_filter_model_preserves_original(self):
        """Test that filtering creates a copy and doesn't modify original."""
        original_model = RenderCVModel(
            cv=Cv(
                name="Test Person",
                sections={
                    "experience": [
                        ExperienceEntry(
                            company="Company A",
                            position="Engineer",
                            tags=["ml"],
                        ),
                        ExperienceEntry(
                            company="Company B",
                            position="Developer",
                            tags=["web"],
                        ),
                    ],
                },
            ),
            versions=[Version(name="ml-focused", include=["ml"])],
        )

        filtered = filter_rendercv_model_by_version(original_model, "ml-focused")

        assert original_model.cv.sections is not None
        assert filtered.cv.sections is not None
        # Original should still have both entries
        assert len(original_model.cv.sections["experience"]) == 2

        # Filtered should have only one
        assert len(filtered.cv.sections["experience"]) == 1
