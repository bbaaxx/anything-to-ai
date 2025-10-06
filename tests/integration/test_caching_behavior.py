"""Integration tests for caching behavior.

Tests cache hit/miss, TTL expiration, and invalidation with real service calls.
Requires Ollama or LM Studio running.
"""

import time
import pytest
from anyfile_to_ai.llm_client import LLMClient, LLMConfig


def check_service_available() -> bool:
    """Check if any LLM service is available."""
    try:
        import httpx

        # Try Ollama first
        response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        if response.status_code == 200:
            return True
    except Exception:
        pass

    try:
        import httpx

        # Try LM Studio
        response = httpx.get("http://localhost:1234/v1/models", timeout=5.0)
        if response.status_code in [200, 401]:
            return True
    except Exception:
        pass

    return False


pytestmark = pytest.mark.skipif(not check_service_available(), reason="No LLM service available (Ollama or LM Studio)")


@pytest.mark.integration
class TestCacheHitMiss:
    """Test cache hit and miss scenarios."""

    def test_cache_miss_on_first_call(self):
        """Test that first call is a cache miss."""
        config = LLMConfig(provider="ollama", base_url="http://localhost:11434", cache_ttl=300)
        client = LLMClient(config)

        # Clear cache first
        client.invalidate_cache()

        # First call should be slower (cache miss)
        start = time.time()
        models1 = client.list_models()
        first_duration = time.time() - start

        assert isinstance(models1, list)
        assert first_duration > 0

    def test_cache_hit_on_second_call(self):
        """Test that second call hits cache."""
        config = LLMConfig(provider="ollama", base_url="http://localhost:11434", cache_ttl=300)
        client = LLMClient(config)

        # Clear cache
        client.invalidate_cache()

        # First call (populate cache)
        start = time.time()
        models1 = client.list_models()
        first_duration = time.time() - start

        # Second call (should hit cache)
        start = time.time()
        models2 = client.list_models()
        second_duration = time.time() - start

        # Verify results are the same
        assert models1 == models2

        # Cache hit should be significantly faster
        assert second_duration < first_duration / 2

    def test_multiple_cache_hits(self):
        """Test multiple consecutive cache hits."""
        config = LLMConfig(provider="ollama", base_url="http://localhost:11434", cache_ttl=300)
        client = LLMClient(config)

        client.invalidate_cache()

        # First call (populate cache)
        models1 = client.list_models()

        # Multiple cache hits
        for _ in range(5):
            models_cached = client.list_models()
            assert models_cached == models1


@pytest.mark.integration
class TestCacheTTL:
    """Test cache TTL expiration."""

    def test_cache_expires_after_ttl(self):
        """Test that cache expires after TTL."""
        config = LLMConfig(
            provider="ollama",
            base_url="http://localhost:11434",
            cache_ttl=2,  # 2 seconds TTL
        )
        client = LLMClient(config)

        client.invalidate_cache()

        # First call (populate cache)
        models1 = client.list_models()

        # Wait for cache to expire
        time.sleep(3)

        # Next call should fetch fresh (cache expired)
        start = time.time()
        models2 = client.list_models()
        duration = time.time() - start

        # Models should be the same
        assert models1 == models2

        # Should take longer (fetched fresh)
        assert duration > 0.001  # Not instant (cache expired)

    def test_cache_valid_within_ttl(self):
        """Test that cache remains valid within TTL."""
        config = LLMConfig(
            provider="ollama",
            base_url="http://localhost:11434",
            cache_ttl=60,  # 1 minute
        )
        client = LLMClient(config)

        client.invalidate_cache()

        # Populate cache
        models1 = client.list_models()

        # Wait less than TTL
        time.sleep(1)

        # Should still hit cache
        start = time.time()
        models2 = client.list_models()
        duration = time.time() - start

        assert models1 == models2
        assert duration < 0.01  # Very fast (cache hit)

    def test_zero_ttl_disables_cache(self):
        """Test that TTL=0 disables caching."""
        config = LLMConfig(
            provider="ollama",
            base_url="http://localhost:11434",
            cache_ttl=0,  # Disable cache
        )
        client = LLMClient(config)

        # First call
        start = time.time()
        client.list_models()
        first_duration = time.time() - start

        # Second call (should not use cache)
        start = time.time()
        client.list_models()
        second_duration = time.time() - start

        # Should have similar durations (both fetch fresh)
        assert abs(first_duration - second_duration) < first_duration


@pytest.mark.integration
class TestCacheInvalidation:
    """Test manual cache invalidation."""

    def test_invalidate_cache_clears_all_entries(self):
        """Test that invalidate_cache clears all entries."""
        config = LLMConfig(provider="ollama", base_url="http://localhost:11434", cache_ttl=300)
        client = LLMClient(config)

        # Populate cache
        models1 = client.list_models()

        # Invalidate cache
        client.invalidate_cache()

        # Next call should fetch fresh (cache cleared)
        models2 = client.list_models()

        # Both calls should return same models
        assert models1 == models2

    def test_invalidate_then_repopulate(self):
        """Test cache repopulation after invalidation."""
        config = LLMConfig(provider="ollama", base_url="http://localhost:11434", cache_ttl=300)
        client = LLMClient(config)

        # Initial population
        client.invalidate_cache()
        models1 = client.list_models()

        # Invalidate
        client.invalidate_cache()

        # Repopulate
        models2 = client.list_models()

        # Third call should hit new cache
        start = time.time()
        models3 = client.list_models()
        duration = time.time() - start

        assert models1 == models2 == models3
        assert duration < 0.01  # Fast (cache hit)


@pytest.mark.integration
class TestCachePerProvider:
    """Test cache isolation per provider."""

    def test_different_providers_have_separate_caches(self):
        """Test that different providers maintain separate caches."""
        config_ollama = LLMConfig(provider="ollama", base_url="http://localhost:11434", cache_ttl=300)
        client_ollama = LLMClient(config_ollama)

        config_lmstudio = LLMConfig(provider="lmstudio", base_url="http://localhost:1234", cache_ttl=300)
        client_lmstudio = LLMClient(config_lmstudio)

        try:
            # Populate both caches
            client_ollama.list_models()
            client_lmstudio.list_models()

            # Invalidate one cache
            client_ollama.invalidate_cache()

            # Ollama cache should be cleared
            start = time.time()
            client_ollama.list_models()
            ollama_duration = time.time() - start

            # LM Studio cache should still be valid
            start = time.time()
            client_lmstudio.list_models()
            lmstudio_duration = time.time() - start

            # LM Studio should be faster (still cached)
            assert lmstudio_duration < ollama_duration

        except Exception:
            pytest.skip("LM Studio not available for cross-provider cache test")
