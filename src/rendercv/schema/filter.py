"""The `rendercv.schema.filter` module provides tag-based filtering for CV entries.

This module enables generating different versions of a CV by filtering entries
based on their tags. The filtering is permissive: entries without tags are always
included.
"""

from copy import deepcopy
from typing import Any

from rendercv.exception import RenderCVUserError

from .models.cv.entries.bases.entry import BaseEntry
from .models.rendercv_model import RenderCVModel
from .models.versions import Version


def get_entry_tags(entry: Any) -> list[str] | None:
    """Extract tags from an entry.

    Args:
        entry: An entry object (BaseEntry subclass, TextEntry, or plain string).

    Returns:
        List of tags if the entry has tags, None otherwise.
    """
    if isinstance(entry, BaseEntry):
        return entry.tags
    # Plain strings don't have tags
    return None


def should_include_entry(
    entry: Any,
    include_tags: list[str] | None,
    exclude_tags: list[str] | None,
) -> bool:
    """Determine if an entry should be included based on tag filters.

    Filtering is permissive:
    - Entries without tags are always included
    - Entries with tags are filtered based on include/exclude rules

    Args:
        entry: The entry to check.
        include_tags: Tags to include (entry must have at least one).
        exclude_tags: Tags to exclude (entry must not have any).

    Returns:
        True if the entry should be included, False otherwise.
    """
    entry_tags = get_entry_tags(entry)

    # Entries without tags are always included (permissive filtering)
    if entry_tags is None or len(entry_tags) == 0:
        return True

    entry_tags_set = set(entry_tags)

    # Apply include filter: entry must have at least one included tag
    if include_tags is not None:
        include_tags_set = set(include_tags)
        if not (entry_tags_set & include_tags_set):
            return False

    # Apply exclude filter: entry must not have any excluded tag
    if exclude_tags is not None:
        exclude_tags_set = set(exclude_tags)
        if entry_tags_set & exclude_tags_set:
            return False

    return True


def filter_entries(
    entries: list[Any],
    include_tags: list[str] | None,
    exclude_tags: list[str] | None,
) -> list[Any]:
    """Filter a list of entries based on tag rules.

    Args:
        entries: List of entries to filter.
        include_tags: Tags to include.
        exclude_tags: Tags to exclude.

    Returns:
        Filtered list of entries.
    """
    return [
        entry
        for entry in entries
        if should_include_entry(entry, include_tags, exclude_tags)
    ]


def find_version(rendercv_model: RenderCVModel, version_name: str) -> Version:
    """Find a version by name in the model.

    Args:
        rendercv_model: The RenderCV model containing versions.
        version_name: The name of the version to find.

    Returns:
        The matching Version object.

    Raises:
        RenderCVUserError: If no versions are defined or the version is not found.
    """
    if rendercv_model.versions is None:
        raise RenderCVUserError(
            message=(
                f"No versions are defined in the input file, but --version "
                f"'{version_name}' was specified."
            )
        )

    for version in rendercv_model.versions:
        if version.name == version_name:
            return version

    available_versions = [v.name for v in rendercv_model.versions]
    raise RenderCVUserError(
        message=(
            f"Version '{version_name}' not found. "
            f"Available versions: {', '.join(available_versions)}"
        )
    )


def filter_rendercv_model_by_version(
    rendercv_model: RenderCVModel,
    version_name: str,
) -> RenderCVModel:
    """Filter a RenderCV model based on a version's tag rules.

    Why:
        Users want to generate different CV versions (e.g., academic vs industry)
        from a single YAML file. This function applies tag-based filtering to
        create a filtered copy of the model.

    Example:
        ```python
        filtered_model = filter_rendercv_model_by_version(model, "academic")
        # filtered_model contains only entries matching the "academic" version's rules
        ```

    Args:
        rendercv_model: The original RenderCV model.
        version_name: The name of the version to apply.

    Returns:
        A new RenderCVModel with filtered entries.
    """
    version = find_version(rendercv_model, version_name)

    # Create a deep copy to avoid modifying the original
    filtered_model = deepcopy(rendercv_model)

    # Filter entries in each section
    if filtered_model.cv.sections is not None:
        filtered_sections: dict[str, list[Any]] = {}

        for section_title, entries in filtered_model.cv.sections.items():
            filtered_entries = filter_entries(
                entries,
                version.include,
                version.exclude,
            )

            # Only include sections that have entries after filtering
            if filtered_entries:
                filtered_sections[section_title] = filtered_entries

        filtered_model.cv.sections = filtered_sections if filtered_sections else None

    return filtered_model
