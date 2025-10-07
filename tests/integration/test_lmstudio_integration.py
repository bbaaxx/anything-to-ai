"""Integration tests for LM Studio provider.

These tests require a running LM Studio service at http://localhost:1234.
Skip if service is unavailable.
"""

import os
import pytest
from anyfile_to_ai.llm_client import (
    LLMClient,
    LLMConfig,
    LLMRequest,
    LLMResponse,
    Message,
    ModelInfo,
)
from anyfile_to_ai.llm_client.exceptions import (
    ConnectionError as LLMConnectionError,
    AuthenticationError,
)

# Test configuration
LMSTUDIO_BASE_URL = "http://localhost:1234"
TEST_TIMEOUT = 30.0


def check_lmstudio_available() -> bool:
    """Check if LM Studio service is available."""
    try:
        import httpx

        response = httpx.get(f"{LMSTUDIO_BASE_URL}/v1/models", timeout=5.0)
        return response.status_code in [
            200,
            401,
        ]  # 401 means auth required but service is up
    except Exception:
        return False


# Skip all tests if LM Studio is not running
pytestmark = pytest.mark.skipif(
    not check_lmstudio_available(),
    reason="LM Studio service not available at localhost:1234",
)


@pytest.mark.integration
class TestLMStudioConnection:
    """Test LM Studio service connection."""

    def test_lmstudio_service_reachable(self):
        """Test that LM Studio service is reachable."""
        config = LLMConfig(provider="lmstudio", base_url=LMSTUDIO_BASE_URL, timeout=TEST_TIMEOUT)
        client = LLMClient(config)

        # Should not raise ConnectionError
        # May raise AuthenticationError if auth is required
        try:
            models = client.list_models()
            assert isinstance(models, list)
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

    def test_lmstudio_connection_with_invalid_url(self):
        """Test connection error with invalid URL."""
        config = LLMConfig(
            provider="lmstudio",
            base_url="http://localhost:99999",  # Invalid port
            timeout=2.0,
            max_retries=0,  # Disable retries for faster test
        )
        client = LLMClient(config)

        with pytest.raises(LLMConnectionError):
            client.list_models()


@pytest.mark.integration
class TestLMStudioAuthentication:
    """Test LM Studio authentication."""

    def test_without_api_key(self):
        """Test access without API key (should work if auth is disabled)."""
        config = LLMConfig(provider="lmstudio", base_url=LMSTUDIO_BASE_URL, api_key=None)
        client = LLMClient(config)

        try:
            models = client.list_models()
            assert isinstance(models, list)
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

    def test_with_api_key_from_env(self):
        """Test authentication with API key from environment."""
        api_key = os.environ.get("LMSTUDIO_API_KEY")
        if not api_key:
            pytest.skip("LMSTUDIO_API_KEY not set")

        config = LLMConfig(provider="lmstudio", base_url=LMSTUDIO_BASE_URL, api_key=api_key)
        client = LLMClient(config)

        models = client.list_models()
        assert isinstance(models, list)


@pytest.mark.integration
class TestLMStudioModelListing:
    """Test LM Studio model listing functionality."""

    def test_list_models_returns_models(self):
        """Test that list_models returns available models."""
        config = LLMConfig(
            provider="lmstudio",
            base_url=LMSTUDIO_BASE_URL,
            api_key=os.environ.get("LMSTUDIO_API_KEY"),
        )
        client = LLMClient(config)

        try:
            models = client.list_models()
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

        assert isinstance(models, list)
        if len(models) > 0:
            model = models[0]
            assert isinstance(model, ModelInfo)
            assert model.id
            assert model.provider == "lmstudio"

    def test_list_models_caching(self):
        """Test that model listing uses cache."""
        import time

        config = LLMConfig(
            provider="lmstudio",
            base_url=LMSTUDIO_BASE_URL,
            api_key=os.environ.get("LMSTUDIO_API_KEY"),
            cache_ttl=60,
        )
        client = LLMClient(config)

        try:
            # First call
            start = time.time()
            models1 = client.list_models()
            first_call_duration = time.time() - start

            # Second call (cached)
            start = time.time()
            models2 = client.list_models()
            second_call_duration = time.time() - start

            assert models1 == models2
            assert second_call_duration < first_call_duration / 2
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")


@pytest.mark.integration
class TestLMStudioGeneration:
    """Test LM Studio text generation."""

    def test_basic_generation(self):
        """Test basic text generation."""
        config = LLMConfig(
            provider="lmstudio",
            base_url=LMSTUDIO_BASE_URL,
            api_key=os.environ.get("LMSTUDIO_API_KEY"),
        )
        client = LLMClient(config)

        try:
            models = client.list_models()
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

        if len(models) == 0:
            pytest.skip("No models available in LM Studio")

        request = LLMRequest(
            messages=[Message(role="user", content="Say 'test' and nothing else.")],
            model=models[0].id,
            temperature=0.0,
            max_tokens=10,
        )

        response = client.generate(request)

        assert isinstance(response, LLMResponse)
        assert response.content
        assert response.model
        assert response.provider == "lmstudio"
        assert response.latency_ms > 0

    def test_generation_with_specific_model(self):
        """Test generation with specific model selection."""
        config = LLMConfig(
            provider="lmstudio",
            base_url=LMSTUDIO_BASE_URL,
            api_key=os.environ.get("LMSTUDIO_API_KEY"),
        )
        client = LLMClient(config)

        try:
            models = client.list_models()
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

        if len(models) == 0:
            pytest.skip("No models available")

        # Use first available model
        target_model = models[0].id

        request = LLMRequest(
            messages=[Message(role="user", content="Hello")],
            model=target_model,
            temperature=0.5,
        )

        response = client.generate(request)

        assert response.content
        assert response.model == target_model

    def test_generation_response_metadata(self):
        """Test that response includes proper metadata."""
        config = LLMConfig(
            provider="lmstudio",
            base_url=LMSTUDIO_BASE_URL,
            api_key=os.environ.get("LMSTUDIO_API_KEY"),
        )
        client = LLMClient(config)

        try:
            models = client.list_models()
        except AuthenticationError:
            pytest.skip("LM Studio requires authentication")

        if len(models) == 0:
            pytest.skip("No models available")

        request = LLMRequest(messages=[Message(role="user", content="Hello")], model=models[0].id)

        response = client.generate(request)

        # Check metadata
        assert response.response_id
        assert response.provider == "lmstudio"
        assert response.latency_ms >= 0
        assert response.retry_count >= 0
        assert isinstance(response.used_fallback, bool)
