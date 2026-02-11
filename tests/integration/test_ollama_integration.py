"""Integration tests for Ollama provider.

These tests require a running Ollama service at http://localhost:11434.
Skip if service is unavailable.
"""

import pytest
from anyfile_to_ai.llm_client import (
    LLMClient,
    LLMConfig,
    LLMRequest,
    LLMResponse,
    Message,
    ModelInfo,
)
from anyfile_to_ai.llm_client.exceptions import ConnectionError as LLMConnectionError, GenerationError
from provider_env import (
    check_ollama_available,
    generation_skip_reason,
    provider_mismatch_reason,
    resolve_base_url,
    resolve_text_model,
)

# Test configuration
OLLAMA_BASE_URL = resolve_base_url("ollama", "http://localhost:11434")
TEST_TIMEOUT = 30.0
REQUESTED_TEXT_MODEL = resolve_text_model()

_SKIP_REASON = provider_mismatch_reason("ollama")
if not _SKIP_REASON and not check_ollama_available(OLLAMA_BASE_URL):
    _SKIP_REASON = f"Ollama service not available at {OLLAMA_BASE_URL}"

# Skip all tests if Ollama is not running
pytestmark = pytest.mark.skipif(_SKIP_REASON is not None, reason=_SKIP_REASON or "")


def _select_model(models: list[ModelInfo]) -> str:
    if not models:
        pytest.skip("No models available in Ollama")
    if REQUESTED_TEXT_MODEL:
        for model in models:
            if model.id == REQUESTED_TEXT_MODEL:
                return model.id
        pytest.skip(f"TEXT_MODEL not available: {REQUESTED_TEXT_MODEL}")
    return models[0].id


def _generate_or_skip(client: LLMClient, request: LLMRequest):
    try:
        return client.generate(request)
    except GenerationError as exc:
        skip_reason = generation_skip_reason(exc, "ollama")
        if skip_reason:
            pytest.skip(skip_reason)
        raise


@pytest.mark.integration
class TestOllamaConnection:
    """Test Ollama service connection."""

    def test_ollama_service_reachable(self):
        """Test that Ollama service is reachable."""
        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL, timeout=TEST_TIMEOUT)
        client = LLMClient(config)

        # Should not raise ConnectionError
        models = client.list_models()
        assert isinstance(models, list)

    def test_ollama_connection_with_invalid_url(self):
        """Test connection error with invalid URL."""
        config = LLMConfig(
            provider="ollama",
            base_url="http://localhost:99999",  # Invalid port
            timeout=2.0,
            max_retries=0,  # Disable retries for faster test
        )
        client = LLMClient(config)

        with pytest.raises(LLMConnectionError):
            client.list_models()


@pytest.mark.integration
class TestOllamaModelListing:
    """Test Ollama model listing functionality."""

    def test_list_models_returns_models(self):
        """Test that list_models returns available models."""
        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL)
        client = LLMClient(config)

        models = client.list_models()

        assert isinstance(models, list)
        assert len(models) > 0  # Assumes at least one model is installed

        # Check model structure
        model = models[0]
        assert isinstance(model, ModelInfo)
        assert model.id
        assert model.provider == "ollama"

    def test_list_models_caching(self):
        """Test that model listing uses cache."""
        import time

        config = LLMConfig(
            provider="ollama",
            base_url=OLLAMA_BASE_URL,
            cache_ttl=60,  # 1 minute cache
        )
        client = LLMClient(config)

        # First call - should fetch from API
        start = time.time()
        models1 = client.list_models()
        first_call_duration = time.time() - start

        # Second call - should use cache (much faster)
        start = time.time()
        models2 = client.list_models()
        second_call_duration = time.time() - start

        assert models1 == models2
        assert second_call_duration < first_call_duration / 2

    def test_invalidate_cache_forces_refresh(self):
        """Test that cache invalidation forces fresh fetch."""
        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL)
        client = LLMClient(config)

        # Populate cache
        models1 = client.list_models()

        # Invalidate cache
        client.invalidate_cache()

        # Next call should fetch fresh (not from cache)
        models2 = client.list_models()

        assert models1 == models2  # Same models, but fresh fetch


@pytest.mark.integration
class TestOllamaGeneration:
    """Test Ollama text generation."""

    def test_basic_generation(self):
        """Test basic text generation."""
        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL)
        client = LLMClient(config)

        # Get first available model
        models = client.list_models()
        assert len(models) > 0, "No models available for testing"

        target_model = _select_model(models)
        request = LLMRequest(
            messages=[Message(role="user", content="Say 'test' and nothing else.")],
            model=target_model,
            temperature=0.0,
            max_tokens=10,
        )

        response = _generate_or_skip(client, request)

        assert isinstance(response, LLMResponse)
        assert response.content
        assert response.model
        assert response.provider == "ollama"
        assert response.latency_ms > 0

    def test_generation_with_system_message(self):
        """Test generation with system prompt."""
        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL)
        client = LLMClient(config)

        models = client.list_models()
        target_model = _select_model(models)
        request = LLMRequest(
            messages=[
                Message(role="system", content="You are a helpful assistant."),
                Message(role="user", content="Say hello."),
            ],
            model=target_model,
            temperature=0.5,
        )

        response = _generate_or_skip(client, request)

        assert response.content
        assert response.finish_reason in ["stop", "length"]

    def test_generation_with_temperature(self):
        """Test generation with different temperature values."""
        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL)
        client = LLMClient(config)

        models = client.list_models()

        # Low temperature (deterministic)
        target_model = _select_model(models)

        request_low = LLMRequest(
            messages=[Message(role="user", content="What is 2+2?")],
            model=target_model,
            temperature=0.0,
        )

        response_low = _generate_or_skip(client, request_low)
        assert response_low.content

        # High temperature (creative)
        request_high = LLMRequest(
            messages=[Message(role="user", content="What is 2+2?")],
            model=target_model,
            temperature=1.5,
        )

        response_high = _generate_or_skip(client, request_high)
        assert response_high.content

    def test_generation_response_metadata(self):
        """Test that response includes proper metadata."""
        config = LLMConfig(provider="ollama", base_url=OLLAMA_BASE_URL)
        client = LLMClient(config)

        models = client.list_models()
        target_model = _select_model(models)
        request = LLMRequest(messages=[Message(role="user", content="Hello")], model=target_model)

        response = _generate_or_skip(client, request)

        # Check metadata
        assert response.response_id
        assert response.provider == "ollama"
        assert response.latency_ms >= 0
        assert response.retry_count >= 0
        assert isinstance(response.used_fallback, bool)
