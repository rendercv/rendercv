"""In-memory render cache keyed by document hash.

Why:
    Typst compilation is expensive; identical (cv, design, locale, settings)
    documents should not be recompiled on every request. Guardrails pattern:
    "cache renders by (yaml-hash, theme)". A small in-memory dict is enough
    for the Phase 0 scaffold (docs/plans/completed/cv-editor-web-app.md);
    persistence-backed caching can replace this in a later phase.
"""

import hashlib
import threading
from collections import OrderedDict

from .core import CvDocuments

MAX_CACHE_ENTRIES = 50


class RenderCache:
    """Thread-safe, size-capped cache of rendered PDF bytes.

    Why:
        FastAPI can serve a sync endpoint from multiple worker threads at
        once; the cache must not corrupt under concurrent access.
    """

    def __init__(self, max_entries: int = MAX_CACHE_ENTRIES) -> None:
        """Create an empty cache.

        Args:
            max_entries: Maximum number of cached renders to keep.
        """
        self.max_entries = max_entries
        self.entries: OrderedDict[str, bytes] = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: str) -> bytes | None:
        """Look up a cached render by key.

        Args:
            key: Cache key, as produced by `cache_key_for`.

        Returns:
            Cached PDF bytes, or None on a cache miss.
        """
        with self.lock:
            return self.entries.get(key)

    def put(self, key: str, value: bytes) -> None:
        """Store a render, evicting the oldest entry once over capacity.

        Args:
            key: Cache key, as produced by `cache_key_for`.
            value: Rendered PDF bytes to store.
        """
        with self.lock:
            self.entries[key] = value
            self.entries.move_to_end(key)
            while len(self.entries) > self.max_entries:
                self.entries.popitem(last=False)


def cache_key_for(documents: CvDocuments) -> str:
    """Compute the sha256 cache key for a set of CV documents.

    Args:
        documents: The four YAML documents.

    Returns:
        Hex-encoded sha256 digest of the concatenated documents.
    """
    hasher = hashlib.sha256()
    for part in (
        documents.cv_yaml,
        documents.design_yaml,
        documents.locale_yaml,
        documents.settings_yaml,
    ):
        hasher.update(part.encode("utf-8"))
        hasher.update(b"\x00")
    return hasher.hexdigest()


def image_cache_key_for(documents: CvDocuments) -> str:
    """Cache key for the PNG render of the same documents.

    Why a separate key rather than a second cache: the PDF and the images
    come from identical input, so they would collide on `cache_key_for` and
    one would be served as the other. A suffix keeps them apart in the one
    cache.

    Args:
        documents: The four YAML documents.

    Returns:
        The PDF key with an image marker appended.
    """
    return f"{cache_key_for(documents)}:png"


render_cache = RenderCache()
