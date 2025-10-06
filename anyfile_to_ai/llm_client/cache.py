"""Model list caching for LLM client.

This module provides an in-memory cache for model listings with TTL expiration
and thread-safe operations.
"""

import threading
import time
from typing import Any, Dict, Optional


class ModelCache:
    """Thread-safe in-memory cache for model listings with TTL expiration."""

    def __init__(self, ttl: int = 300):
        """Initialize model cache.

        Args:
            ttl: Time-to-live in seconds for cached entries (default: 300 = 5 minutes)
        """
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get cached value for key if not expired.

        Args:
            key: Cache key (typically provider base URL)

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            if self.is_expired(key):
                # Remove expired entry
                del self._cache[key]
                return None

            return entry["value"]

    def set(self, key: str, value: Any) -> None:
        """Set cache value for key with current timestamp.

        Args:
            key: Cache key (typically provider base URL)
            value: Value to cache (usually list of ModelInfo)
        """
        with self._lock:
            self._cache[key] = {"value": value, "expires_at": time.time() + self.ttl}

    def invalidate(self, key: Optional[str] = None) -> None:
        """Invalidate cache entry or entire cache.

        Args:
            key: Specific key to invalidate, or None to clear entire cache
        """
        with self._lock:
            if key is None:
                self._cache.clear()
            elif key in self._cache:
                del self._cache[key]

    def is_expired(self, key: str) -> bool:
        """Check if cache entry is expired.

        Args:
            key: Cache key to check

        Returns:
            True if entry is expired or doesn't exist, False otherwise

        Note:
            This method does NOT acquire the lock. Caller must hold lock.
        """
        if key not in self._cache:
            return True

        entry = self._cache[key]
        return time.time() >= entry["expires_at"]
