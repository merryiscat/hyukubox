"""TinyDB-based caching for API responses."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from tinydb import Query, TinyDB


class MetadataCache:
    """TinyDB-based cache for API responses.

    Provides simple key-value caching with TTL (time-to-live) support.
    """

    def __init__(self, cache_path: Path):
        """Initialize cache.

        Args:
            cache_path: Directory to store cache database
        """
        cache_path.mkdir(parents=True, exist_ok=True)
        self.db = TinyDB(cache_path / "metadata_cache.json")
        self.query = Query()

    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get cached value if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        result = self.db.search(self.query.key == key)
        if not result:
            return None

        entry = result[0]
        expires = datetime.fromisoformat(entry['expires'])

        if expires < datetime.now():
            # Expired, remove it
            self.db.remove(doc_ids=[entry.doc_id])
            return None

        return entry['value']

    def set(self, key: str, value: dict[str, Any], ttl: int = 3600) -> None:
        """Cache a value with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        expires = datetime.now() + timedelta(seconds=ttl)

        # Upsert: update if exists, insert if not
        self.db.upsert(
            {
                'key': key,
                'value': value,
                'expires': expires.isoformat()
            },
            self.query.key == key
        )

    def delete(self, key: str) -> None:
        """Delete cached value.

        Args:
            key: Cache key
        """
        self.db.remove(self.query.key == key)

    def clear(self) -> None:
        """Clear all cached values."""
        self.db.truncate()

    def cleanup_expired(self) -> int:
        """Remove all expired entries.

        Returns:
            Number of entries removed
        """
        now = datetime.now()
        all_entries = self.db.all()

        removed_count = 0
        for entry in all_entries:
            expires = datetime.fromisoformat(entry['expires'])
            if expires < now:
                self.db.remove(doc_ids=[entry.doc_id])
                removed_count += 1

        return removed_count
