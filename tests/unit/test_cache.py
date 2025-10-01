"""Unit tests for ModelCache."""

import time
from llm_client.cache import ModelCache


class TestModelCache:
    """Test cases for ModelCache functionality."""

    def test_cache_initialization(self):
        """Cache can be initialized with TTL."""
        cache = ModelCache(ttl=60)
        assert cache.ttl == 60

    def test_cache_get_miss(self):
        """Cache returns None for missing key."""
        cache = ModelCache()
        result = cache.get("missing-key")
        assert result is None

    def test_cache_set_and_get(self):
        """Cache can store and retrieve values."""
        cache = ModelCache()
        test_data = ["model1", "model2"]

        cache.set("test-key", test_data)
        result = cache.get("test-key")

        assert result == test_data

    def test_cache_ttl_expiration(self):
        """Cache entries expire after TTL."""
        cache = ModelCache(ttl=1)  # 1 second TTL
        cache.set("test-key", ["model1"])

        # Should be available immediately
        assert cache.get("test-key") == ["model1"]

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("test-key") is None

    def test_cache_invalidate_specific_key(self):
        """Cache can invalidate specific key."""
        cache = ModelCache()
        cache.set("key1", ["data1"])
        cache.set("key2", ["data2"])

        cache.invalidate("key1")

        assert cache.get("key1") is None
        assert cache.get("key2") == ["data2"]

    def test_cache_invalidate_all(self):
        """Cache can invalidate all entries."""
        cache = ModelCache()
        cache.set("key1", ["data1"])
        cache.set("key2", ["data2"])

        cache.invalidate()

        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_is_expired_for_missing_key(self):
        """is_expired returns True for missing keys."""
        cache = ModelCache()
        # Note: is_expired requires caller to hold lock
        # In real usage, this is called from within get()
        # For testing, we can call it directly since it's single-threaded
        assert cache.is_expired("missing-key") is True

    def test_cache_overwrites_existing_key(self):
        """Setting existing key overwrites old value."""
        cache = ModelCache()
        cache.set("key", ["old"])
        cache.set("key", ["new"])

        assert cache.get("key") == ["new"]
